FROM tensorflow/tensorflow:1.12.0-gpu-py3

RUN mkdir /queue
COPY . /queue
WORKDIR /queue

RUN pip install -r requirements.txt

ENTRYPOINT celery -A tasks worker --loglevel=info --concurrency=1 --max-tasks-per-child=1


