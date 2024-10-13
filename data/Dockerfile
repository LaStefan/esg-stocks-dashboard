FROM python:3.11

WORKDIR /app

RUN pip3 install psycopg2 sqlalchemy pandas 

# Add this line to see what files are in the container
RUN ls -la /app

# Copy everything in the current directory (which is ./data) to /app in the container
COPY . /app

CMD ["python3", "loader.py"]