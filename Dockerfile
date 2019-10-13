FROM python:3.7

RUN mkdir /opt/apl/

WORKDIR /opt/apl/
RUN cd /opt/apl/

COPY requirements.txt /opt/apl
RUN pip3 install -r requirements.txt

COPY ./src/ /opt/apl/src
COPY ./resources /opt/apl/resources
COPY ./token.txt /opt/

RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "tesseract-ocr", "tesseract-ocr-por"]

RUN echo $(ls)
RUN echo $(pwd)

ARG submit
ARG contas_host

ENV contas_host ${contas_host:-35.188.218.51}
ENV submit ${submit:-true}

WORKDIR /opt/apl/src
RUN cd /opt/apl/src
CMD python3 /opt/apl/src/app.py $submit $contas_host