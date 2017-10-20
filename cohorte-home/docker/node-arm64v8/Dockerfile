FROM cohorte/runtime-arm64v8:latest

#-----------------------------------------------------------------------------
# Cohorte Runtime image.
#
# Cohorte Platform version: 1.2.1
#-----------------------------------------------------------------------------

MAINTAINER "Bassem Debbabi" <bassem.debbabi@cohorte-technologies.com>

ENV REFRESHED_AT 20170707_1130

# Installation commands

ENV COHORTE_BASE /opt/node
ENV COHORTE_DATA /opt/data

RUN mkdir -p $COHORTE_BASE
RUN mkdir -p $COHORTE_DATA
COPY ../node/install/run_service /opt
COPY ../node/install/boot.sh /opt
COPY ../node/install/cohorte.service ./etc/systemd/system/cohorte.service
COPY ../node/install/get-pip.py /tmp/
COPY ../node/install/init_* /opt

# install pip 
RUN python3 /tmp/get-pip.py 
RUN pip3 install jsoncomment

RUN chmod +x /opt/boot.sh

RUN systemctl enable cohorte.service

ENTRYPOINT ["/opt/boot.sh"]

RUN ls -l /opt

VOLUME [ "/opt/node" ]

EXPOSE 9000 9001 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009 8010