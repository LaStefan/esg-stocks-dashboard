import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import time

# PostgreSQL database configuration
db_config = {
    "dbname": "esg-stocks-database",
    "user": "team13",
    "password": "team13",
    "host": "localhost",
    "port": "5432",
}

# Function to check if the DB is ready
def is_db_ready(engine):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("Connected successfully!")
        return True
    except OperationalError as e:
        print(f"Database not ready: {e}")
        return False

# Function to drop the table if it exists
def drop_table(table_name, engine):
    with engine.connect() as conn:
        drop_table_query = text(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        conn.execute(drop_table_query)

# Function to upload CSV files to PostgreSQL
def upload_csv_to_postgres(csv_file, table_name, engine):
    df = pd.read_csv(csv_file, dtype=str, delimiter=',')
    df.to_sql(table_name, engine, if_exists='replace', index=False)

# Main function to upload all CSV files in the local folder
def main():
    conn_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    engine = create_engine(conn_url)

    # Wait for the database to be ready
    while not is_db_ready(engine):
        print("Waiting for database to be ready...")
        time.sleep(120)  # Wait for 120 seconds before trying again

    try:
        

        transformed_data_path = f'{os.getcwd()}/data/transformed/'
        # Get list of CSV files in the current directory
        csv_files = [file for file in os.listdir(transformed_data_path) if file.endswith(".csv")]

        # Drop existing tables and upload new data
        for csv_file in csv_files:
            table_name = os.path.splitext(csv_file)[0]  # Use CSV filename as table name
            drop_table(table_name, engine)  # Drop table if it exists
            upload_csv_to_postgres(f'{transformed_data_path}/{csv_file}', table_name, engine)  # Upload new data
            print(f"Uploaded data from {csv_file} to table {table_name}.")


    except Exception as e:
        print(f"Error: {e}")
    

if __name__ == "__main__":
    main()