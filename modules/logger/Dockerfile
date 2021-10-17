FROM python:3.7.5-slim

WORKDIR .

RUN pip install kafka-python

COPY . .
CMD ["python", "kafka/logconsumer.py"]