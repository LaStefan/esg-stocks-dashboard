from datetime import datetime
import json
import os
from itertools import islice
import pandas as pd

def generate_csv(data: dict, filename: str, index=False):
  df = pd.DataFrame.from_dict(data) 
  df.to_csv(filename, index=index)

# Converts date to YYYY-MM-DD format
def convert_date(input_date):
    try:
        parsed_date = datetime.strptime(input_date, '%d-%m-%Y')
        return parsed_date.strftime('%Y-%m-%d')
    except ValueError:
        return "Invalid date format"

def get_ticker_symbols():
  # Get the list ticker symbols from esg-ratings.csv and return it as a list
  try:
    root_dir = os.path.dirname(os.path.abspath(os.getcwd()))
    esg_path = os.path.join(root_dir, 'data', 'raw', 'esg-ratings.csv')
    esg_dataframe = pd.read_csv(esg_path)
    # TODO: Increase number
    return esg_dataframe['ticker'].str.upper().to_list()[0:200]
    
  except Exception as e:
    raise f"Error reading esg list: {e}"
  
def get_chunks(symbols, chunk_size=5):
  it = iter(symbols)
  for first in it:
      yield [first] + list(islice(it, chunk_size - 1))