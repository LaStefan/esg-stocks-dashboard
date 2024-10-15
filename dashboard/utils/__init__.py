from datetime import datetime
import json
import os

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
  try:
    root_dir = os.path.dirname(os.path.abspath(os.getcwd()))
    ticker_list_path = os.path.join(root_dir, 'dashboard', 'stock_list.json')
    with open(ticker_list_path) as f:
      return json.load(f) 
  except Exception as e:
    raise f"Error reading stock_list.json: {e}"