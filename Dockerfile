FROM debian:stable

WORKDIR /srv


RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential unzip wget cmake python libopenblas-dev

COPY ./requirements.txt /srv/requirements.txt

ENV CXX=clang++

#  Ccompile llama-cpp-python with Openblas
ENV LLAMA_OPENBLAS=1

RUN pip install --no-cache-dir --upgrade -r /srv/requirements.txt

COPY ./app /srv/app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]