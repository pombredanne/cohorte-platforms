FROM ubuntu:16.04

#-----------------------------------------------------------------------------
# Cohorte Base image X86 for cohorte device
#
# Contains: 
# - ubuntu Xenial 
# - Oracle JVM 8 
# - Python 3.6
#
# Installed tools:
# - vim
# - wget
# - tar
# - nc
# - python 3.6
#
#-----------------------------------------------------------------------------

# meta-data
MAINTAINER "Bassem Debbabi" <bassem.debbabi@cohorte-technologies.com>

# force rebuilind all this Dockerfile by changing the date
ENV REFRESHED_AT 20161013_1730
ENV JAVA_VERSION 8u151
ENV JAVA_LONG_VERSION 8u151-b12
ENV JAVA_HOME /opt/java
ENV PATH $JAVA_HOME/bin:$PATH

# informer systemd qu'il s'execute sur un conteneur docker
ENV container docker


# installation du systemd au lieu du fakesystemd
# ceci est necessaire pour pouvoir lancer mysql et openldap comme un service OS
# avec les commandes "service" et "systemctl".
RUN apt-get update


RUN apt-get install -y software-properties-common python-software-properties
RUN add-apt-repository -y ppa:jonathonf/python-3.6

RUN apt-get update

# installer d'autres outils
RUN apt-get  install -y vim wget tar netcat-openbsd
#RUN apt-get  install -y epel-release
RUN apt-get  install -y python3.6  python
# to have systemctl command
RUN apt-get install -y systemd

# Installer Java 8 (Oracle)
# inspired from: https://hub.docker.com/r/cooniur/java/
RUN mkdir -p $JAVA_HOME
COPY ./jdk/* /opt/java/
RUN chmod +x /opt/java/bin/*
   

# Test de java
RUN java -version

# Pour definir des limitations (cpu, ram, etc) a des groupes de processus
VOLUME [ "/sys/fs/cgroup", "/var/log/journal" ]

# au demarage lancer du conteneur, il faut lancer /usr/sbin/init (systemd)
CMD ["/usr/sbin/init"]
