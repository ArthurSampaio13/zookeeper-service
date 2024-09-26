import sys
import time
import json
import grpc
import simple_calculate_pb2 as calculate_pb2
import simple_calculate_pb2_grpc as calculate_grpc
from kazoo.client import KazooClient
from concurrent import futures
import random

from settings_local import settings_info

import warnings
warnings.filterwarnings("ignore")


class SimpleRpcServerServicer(calculate_grpc.SimpleRpcServerServicer):
    """
    Implementa o código específico do método chamado
    """

    def __init__(self):
        self.subject_question_type_db = {
            'Português': ['Interpretação de Texto', 'Gramática', 'Ortografia', 'Literatura Brasileira', 'Figuras de Linguagem', 'Técnicas de Escrita', 'Estrutura de Redação', 'Dissertação'],
            'Matemática': ['Álgebra', 'Geometria', 'Equações do 1º Grau', 'Funções', 'Trigonometria', 'Probabilidade'],
            'Inglês': ['Interpretação de Texto', 'Gramática', 'Vocabulário', 'Formação de Sentenças', 'Essay Writing', 'Grammar and Style'],
            'Física': ['Mecânica', 'Termodinâmica', 'Óptica', 'Eletromagnetismo', 'Leis de Newton', 'Trabalho e Energia'],
            'Química': ['Tabelas Periódicas', 'Ligações Químicas', 'Estequiometria', 'Reações Químicas', 'Cálculos Estequiométricos', 'Ácidos e Bases'],
            'Biologia': ['Citologia', 'Genética', 'Evolução', 'Ecologia', 'Biotecnologia', 'Imunologia'],
            'História': ['Brasil Colônia', 'Brasil Império', 'Guerra Fria', 'Revolução Francesa', 'Segunda Guerra Mundial', 'Independência do Brasil', 'Era Vargas', 'Ditadura Militar no Brasil']
        }
        self.answers = list(range(10))
        self.correct_number = random.randint(1, 21)

    def Calculate(self, request, context):
        """
        Serviço de cálculo - Adição, Subtração, Multiplicação, Divisão
        RPC Unária - O tipo mais simples de RPC, onde o cliente envia uma única solicitação e retorna uma única resposta
        :param request:
        :param context:
        :return:
        """
        if request.op == calculate_pb2.Work.ADD:
            result = request.num1 + request.num2
            return calculate_pb2.Result(val=result)
        elif request.op == calculate_pb2.Work.SUBTRACT:
            result = request.num1 - request.num2
            return calculate_pb2.Result(val=result)
        elif request.op == calculate_pb2.Work.MULTIPLY:
            result = request.num1 * request.num2
            return calculate_pb2.Result(val=result)
        elif request.op == calculate_pb2.Work.DIVIDE:
            if request.num2 == 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("ERRO! Não se pode dividir por zero.")
                return calculate_pb2.Result()
            result = request.num1 // request.num2
            return calculate_pb2.Result(val=result)
        else:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Operação inválida.')
            return calculate_pb2.Result()

    def GetSubjectQuestionTypes(self, request, context):
        """
        Chamada de RPC de streaming do servidor - Obtém tipos de questões com base no assunto
        :param request:
        :param context:
        :return:
        """
        subject = request.name
        question_types = self.subject_question_type_db.get(subject)
        
        if question_types is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Assunto '{subject}' não encontrado.")
            return
        
        for question_type in question_types:
            yield calculate_pb2.QuestionType(name=question_type)
            
    def Accumulate(self, request_iterator, context):
        """
        Chamada de RPC de streaming do cliente - O cliente envia várias solicitações, e o servidor acumula e retorna
        Itera sobre o iterador e executa a operação de soma
        :param request_iterator:
        :param context:
        :return:
        """
        sum = 0
        for num in request_iterator:
            sum += num.val
        return calculate_pb2.Sum(val=sum)

    def GuessNumber(self, request_iterator, context):
        """
        Chamada de RPC de streaming bidirecional entre cliente e servidor
        O cliente envia vários dados e, se o servidor reconhecer, ele responde
        :param request_iterator:
        :param context:
        :return:
        """
        for num in request_iterator:
            if num.val == self.correct_number:  # Verifica se o número enviado é o correto
                yield calculate_pb2.Answer(
                    val=num.val, desc='\nVocê acertou o número!'
                )
                break
            else:
                yield calculate_pb2.Answer(
                    val=num.val, desc='\nTente novamente!'
                )


def register_zk(host, port):
    """
    Registrar no zookeeper
    """
    zk = KazooClient(hosts='{host}:{port}'.format(
        host=settings_info["zookeeper"]["host"],
        port=settings_info["zookeeper"]["port"])
    )
    zk.start()
    zk.ensure_path('/rpc_calc')  # Criar o nó raiz
    value = json.dumps({'host': host, 'port': port})

    # Criar um nó filho do serviço
    zk.create(
        '/rpc_calc/calculate_server',
        value.encode(),
        ephemeral=True,
        sequence=True
    )


# Iniciar o servidor para fornecer chamadas RPC
def server(host, port):
    # Criar um objeto servidor
    rpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Registrar os métodos implementados no objeto servidor
    calculate_grpc.add_SimpleRpcServerServicer_to_server(
        SimpleRpcServerServicer(), rpc_server
    )
    # Configurar o endereço do servidor e começar a escutar
    rpc_server.add_insecure_port('{}:{}'.format(host, port))

    # Iniciar o serviço e começar a receber solicitações
    rpc_server.start()

    register_zk(host, port)

    # Para encerrar o serviço, use ctrl+c para sair
    try:
        print("Iniciando servidor...")
        time.sleep(1000)
    except KeyboardInterrupt:
        rpc_server.stop(0)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage:python server.py [host] [port]")
        exit(1)
    host = sys.argv[1]
    port = sys.argv[2]

    server(host, port)
