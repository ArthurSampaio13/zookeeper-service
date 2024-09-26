# zookeeper-service

# Recomendo instalar [zsh](https://www.dio.me/articles/desvendando-a-eficiencia-no-terminal-zsh-oh-my-zsh)

## Como rodar:
  
- Agora vai ser necessário entrar em uma distro linux:
  
# Caso não tenha python:
```
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get install python3.9
```
# Instale a dependências
- pip install grpcio grpcio-tools kazoo

# Caso não tenha o Docker:
```
- # Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
- sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

- chmod +x run.sh
- /run.sh

# Caso não tenha o Java
- sudo apt install default-jre

# Inicie o servidor zookeeper
- cd apache-zookeeper-3.8.4-bin\binz
- ./zkServer.sh start-foreground

# Agora é rodar os arquivos .py
- python3 server.py localhost 8081
- python3 client.py

