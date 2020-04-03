FROM python:3.7

WORKDIR /src
COPY /src/ .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "kopf", "run", "operator.py"]