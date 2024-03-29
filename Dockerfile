FROM docker.io/python:3.10

WORKDIR /app

# --- [Install python and pip] ---
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y python3 python3-pip git
COPY . /app

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install gunicorn

ENV GUNICORN_CMD_ARGS="--workers=3 --bind=0.0.0.0:8086"

EXPOSE 8086

CMD [ "gunicorn", "app:app" ]
