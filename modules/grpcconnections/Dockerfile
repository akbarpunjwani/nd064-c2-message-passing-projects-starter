FROM python:3.7.5-slim

WORKDIR .

RUN pip install requests
RUN pip install grpcio-tools
RUN pip install kafka-python

COPY . .

EXPOSE 50051

ENTRYPOINT ["python", "server/connections.py"]
