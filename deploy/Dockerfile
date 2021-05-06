FROM python:latest

WORKDIR /app/

# install some basics
RUN apt update \
    && apt install -y vim curl netcat

# install psycopg2 dependencies
RUN apt update \
    && apt install -y libpq-dev postgresql postgresql-contrib

ENV PIP_NO_CACHE_DIR 1

ADD ./requirements ./requirements
RUN pip install -r ./requirements/requirements.txt
# RUN pip install -r ./requirements/scientific-requirements.txt

# copy entrypoint.sh
ADD ./deploy/postgres/entrypoint.sh /app/entrypoint.sh


ADD ./ ./
RUN ./manage.py collectstatic --noinput

# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
