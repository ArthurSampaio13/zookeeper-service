import random
import json
import grpc
import simple_calculate_pb2 as calculate_pb2
import simple_calculate_pb2_grpc as calculate_grpc
from kazoo.client import KazooClient
from settings_local import settings_info

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def invoke_calculate(stub):
    """
    Cliente do serviço de cálculo
    Unary RPC (Chamada de Procedimento Remoto Unário)
    :param stub:
    :return:
    """
    num1 = int(input("Digite o primeiro número: "))
    num2 = int(input("Digite o segundo número: "))
    print("\nEscolha a operação:")
    print("1: Adição (+)")
    print("2: Subtração (-)")
    print("3: Multiplicação (*)")
    print("4: Divisão (//)")
    op_choice = int(input("Escolha a operação (1-4): "))

    work = calculate_pb2.Work(num1=num1, num2=num2)
    
    if op_choice == 1:
        work.op = calculate_pb2.Work.ADD
    elif op_choice == 2:
        work.op = calculate_pb2.Work.SUBTRACT
    elif op_choice == 3:
        work.op = calculate_pb2.Work.MULTIPLY
    elif op_choice == 4:
        work.op = calculate_pb2.Work.DIVIDE
    
    try:
        result = stub.Calculate(work)
        print(f'Resultado: {result.val}')
    except grpc.RpcError as e:
        print("Erro na operação de cálculo! Talvez você tenha tentado dividir por zero.")


def invoke_get_subject_question_types(stub):
    """
    Obtém tipos de questões com base na disciplina
    Server Streaming RPC (RPC de fluxo do servidor)
    O cliente envia uma solicitação e o servidor responde com múltiplas respostas
    :param stub:
    :return:
    """
    print("\nEscolha um assunto para estudar:")
    subjects = ["Português", "Matemática", "Inglês", "Física", "Química", "Biologia", "História"]
    for idx, subject in enumerate(subjects, 1):
        print(f"{idx}: {subject}")
    choice = int(input("Digite o número correspondente ao assunto: "))
    selected_subject = subjects[choice - 1]

    subject = calculate_pb2.Subject(name=selected_subject)
    question_types = stub.GetSubjectQuestionTypes(subject)
    print(f"\nTipos de questões para {selected_subject}:")
    for question_type in question_types:    
        print(question_type.name)



def invoke_accumulate(stub):
    """
    Client Streaming RPC (RPC de fluxo do cliente)
    O cliente envia uma sequência de solicitações ao servidor em vez de uma única, e o servidor responde com uma única resposta.
    O cliente envia vários números e o servidor acumula e retorna a soma.
    :param stub:
    :return:
    """

    def generate_delta():
        """
        O servidor percorre um iterador, enquanto o cliente é um gerador
        :return:
        """
        print("\nDigite 10 números para acumular:")
        for _ in range(10):
            num = int(input("Digite um número: "))
            yield calculate_pb2.Delta(val=num)

    delta_iterator = generate_delta()
    sum = stub.Accumulate(delta_iterator)
    print(f'Soma acumulada = {sum.val}')


def invoke_guess_number(stub):
    """
    RPC de fluxo bidirecional
    O cliente e o servidor podem ler e escrever dados de fluxo de forma independente em qualquer ordem.
    O servidor pode retornar a resposta depois de receber todas as informações de solicitação,
    ou responder a cada solicitação recebida, ou retornar algumas respostas após algumas solicitações.
    Jogo de adivinhar números: o servidor só retorna um resultado quando o número estiver correto.
    :param stub:
    :return:
    """

    def generate_num():
        print("\nTente adivinhar um número entre 1 e 20. O servidor responderá quando você acertar.")
        while True:
            num = int(input("Digite um número: "))
            yield calculate_pb2.Number(val=num)

    number_iterator = generate_num()
    answers = stub.GuessNumber(number_iterator)
    for answer in answers:
        print(f'{answer.desc}: {answer.val}')


class DistributedChannel(object):
    def __init__(self):
        self._zk = KazooClient(hosts='{host}:{port}'.format(
            host=settings_info["zookeeper"]["host"],
            port=settings_info["zookeeper"]["port"])
        )
        self._zk.start()
        self._get_servers()

    def _get_servers(self, event=None):
        """
        Obtém a lista de endereços dos servidores a partir do Zookeeper
        """
        servers = self._zk.get_children(
            '/rpc_calc', watch=self._get_servers
        )
        print(servers)
        self._servers = []
        for server in servers:
            data = self._zk.get('/rpc_calc/' + server)[0]
            if data:
                addr = json.loads(data.decode())
                self._servers.append(addr)

    def get_server(self):
        """
        Seleciona aleatoriamente um servidor disponível
        """
        return random.choice(self._servers)
    

def run():
    channel = DistributedChannel()
    server = channel.get_server()
    with grpc.insecure_channel("{}:{}".format(
            server.get("host"),
            server.get("port")
    )
    ) as channel:
        # Cria o objeto stub para chamadas de cliente
        stub = calculate_grpc.SimpleRpcServerStub(channel)

        while True:
            print("\nEscolha uma ação:")
            print("1: Calcular")
            print("2: Escolher assunto para estudar")
            print("3: Acumular números")
            print("4: Adivinhar o número")
            print("5: Sair")
            choice = int(input("Digite o número da ação (1-5): "))

            if choice == 1:
                invoke_calculate(stub)
            elif choice == 2:
                invoke_get_subject_question_types(stub)
            elif choice == 3:
                invoke_accumulate(stub)
            elif choice == 4:
                invoke_guess_number(stub)
            elif choice == 5:
                print("Encerrando o cliente.")
                break
            else:
                print("Escolha inválida! Tente novamente.")
            
            print("")
            print("Deseja continuar?")
            entrada = int(input("Digite 1 para continuar ou 0 para parar: "))

            if  entrada == 1:
                continue
            break 


if __name__ == '__main__':
    run()
