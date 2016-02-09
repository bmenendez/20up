FROM ubuntu:14.04

ENV BUILD_TIMESTAMP 20160201

RUN apt-get update -qq
RUN apt-get install -y python-pip git

RUN pip install beautifulsoup4 mechanize

RUN git clone https://github.com/bmenendez/20up.git /project

WORKDIR /volume

VOLUME ["/volume"]

ENTRYPOINT ["python", "/project/20up.py"]
