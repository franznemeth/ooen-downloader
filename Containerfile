FROM alpine:latest

RUN apk add --no-cache --update \
            geckodriver \
            firefox-esr \
            python3 \
            py3-pip
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt && rm requirements.txt
COPY main.py /main.py

ENTRYPOINT ["python3", "/main.py"]