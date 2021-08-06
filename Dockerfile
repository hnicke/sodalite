FROM ubuntu
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
        gpg \
        curl \
    && curl http://debian.hnicke.de/repo/go | sh \
    && apt-get install sodalite -y \
    && apt-get clean
WORKDIR /root
RUN echo "source /usr/share/sodalite/shell-integration.sh" >> ~/.bashrc

