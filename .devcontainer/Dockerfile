FROM 038297999601.dkr.ecr.ap-southeast-2.amazonaws.com/spark/emr-6.5.0:20211119

USER root

## Add hadoop to sudo
RUN yum install -y sudo git \
  && echo "hadoop ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

## Install python packages
COPY ./pkgs /tmp/pkgs
RUN pip3 install -r /tmp/pkgs/requirements.txt

USER hadoop:hadoop