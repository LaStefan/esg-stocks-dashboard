from datetime import datetime

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
