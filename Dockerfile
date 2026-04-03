FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
ENV PATH=$JAVA_HOME/bin:$PATH
ENV HOME=/tmp

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    openjdk-17-jre-headless \
    libreoffice \
    libreoffice-java-common \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Java 경로 (AMD64 / ARM64 자동 대응)
RUN JAVA_PATH=$(dirname $(dirname $(readlink -f $(which java)))) && \
    echo "export JAVA_HOME=$JAVA_PATH" >> /etc/environment && \
    ln -sf $JAVA_PATH /usr/lib/jvm/java-default

ENV JAVA_HOME=/usr/lib/jvm/java-default

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY server.py .
COPY index.html .

RUN mkdir -p /tmp/hwp_output /tmp/hwp_tmp /tmp/lo_profile

EXPOSE 8000

CMD ["python3", "server.py"]
