FROM python:3.10-slim

WORKDIR /app

# We need to set the host to 0.0.0.0 to allow outside access
ENV HOST 0.0.0.0

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential wget cmake sqlite3

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . /app

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 80
