FROM python:3.11

WORKDIR /app

RUN pip3 install psycopg2 sqlalchemy pandas 

# Copy the current directory contents to /app
COPY ./data /app

CMD ["python3", "loader.py"]