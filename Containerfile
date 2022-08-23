FROM bitnami/minideb:latest

RUN apt update && apt install -y  \
            curl \
            firefox-esr \
            python3.9-full \
            python3-pip \
     && rm -rf /var/lib/apt/lists/*
RUN curl -L -o /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz && \
    ls -l /tmp && \
    tar xfva /tmp/geckodriver.tar.gz && \
    rm /tmp/geckodriver.tar.gz && \
    mv geckodriver /usr/bin/
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt && rm /tmp/requirements.txt
COPY main.py /main.py

ENTRYPOINT ["python3", "/main.py"]