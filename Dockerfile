FROM ubuntu:xenial
ADD ./common/sources.list /etc/apt/sources.list
RUN apt-get -y update --fix-missing && apt-get -y update

WORKDIR /proj
ADD requirements.txt /proj
RUN apt-get install -y python python-dev python3 python3-dev python3-pip
RUN apt-get install -y libmysqlclient-dev libssl-dev
