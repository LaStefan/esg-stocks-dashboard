FROM jupyter/scipy-notebook
RUN pip3 install psycopg2-binary sqlalchemy pulp python-gnupg
USER root
RUN apt-get update && apt-get install -y gnupg