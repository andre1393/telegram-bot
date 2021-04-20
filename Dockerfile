FROM python:3.7

RUN mkdir /opt/apl/

WORKDIR /opt/apl/

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

ARG SUBMIT_BILL
ARG CONTAS_HOST
ARG CONTAS_PORT
ARG TELEGRAM_TOKEN

ENV TELEGRAM_TOKEN $TELEGRAM_TOKEN
ENV CONTAS_HOST ${CONTAS_HOST:-contas}
ENV CONTAS_PORT ${CONTAS_PORT:-8000}
ENV SUBMIT_BILL ${SUBMIT_BILL:-true}

COPY ./ ./

RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "tesseract-ocr", "tesseract-ocr-por"]

ENTRYPOINT ["sh", "init.sh"]