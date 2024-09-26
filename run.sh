#!/bin/bash

# Definir diretório do proto
PROTO_DIR="protos"

# Função para verificar se os comandos anteriores falharam
check_failure() {
  if [ $? -ne 0 ]; then
    echo "Erro: $1"
    exit 1
  fi
}

# Compilar proto
echo "Compilando arquivos proto..."
cd $PROTO_DIR || { echo "Erro: Diretório $PROTO_DIR não encontrado"; exit 1; }  # Entrar no diretório do proto
python3 -m grpc_tools.protoc -I. --python_out=.. --grpc_python_out=.. simple_calculate.proto
check_failure "Erro ao compilar arquivos proto"
cd ..  # Voltar para o diretório anterior

# Construir imagem Docker do servidor
echo "Construindo imagem Docker do servidor..."
sudo docker build -t simple_calculate -f Dockerfile .
check_failure "Erro ao construir imagem do servidor"

# Construir imagem Docker do nginx
echo "Construindo imagem Docker do nginx..."
sudo docker build -t simple_calculate_nginx -f common/nginx/Dockerfile .
check_failure "Erro ao construir imagem do nginx"

# Iniciar o docker-compose
echo "Iniciando o serviço com docker-compose..."
docker compose up -d
check_failure "Erro ao iniciar docker-compose"

echo "Serviço iniciado com sucesso!"
