FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1 \
        PIP_NO_CACHE_DIR=off \
        PIP_DISABLE_PIP_VERSION_CHECK=on \
        PIP_DEFAULT_TIMEOUT=100 \
        PYTHONPATH=${PYTHONPATH}:${PWD}


        RUN apt-get -y update \
            && apt-get -y install unzip python3-dev musl-dev curl\
            && apt-get install netcat -y --no-install-recommends apt-utils


            RUN mkdir /code
            COPY . /code
            COPY ./wait-for /bin/wait-for
            RUN chmod 777 /code/install-requirements.sh
            RUN /code/install-requirements.sh
            RUN chmod 777 -R /bin/wait-for
            COPY pyproject.toml /code/
            WORKDIR /code



            RUN pip3 install poetry
            RUN poetry config virtualenvs.create false
            RUN poetry install
