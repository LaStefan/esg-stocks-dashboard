# This file gathers data from different sources, and generates a CSV file that will be used to seed the database
from typing import List
from dotenv import load_dotenv
from utils import generate_csv, convert_date
import pandas as pd
import finnhub
import json
import asyncio
import os
import fmpsdk
load_dotenv()

# Get the path of the current python file
script_dir = os.path.dirname(os.path.abspath(__file__))
# Change the working directory to the script's directory
os.chdir(script_dir)

FMP_API_KEY= os.getenv('FMP_API_KEY')
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
if not FMP_API_KEY or not FINNHUB_API_KEY:
  raise "The required API keys were not found in the .env file"

# Get the list ticker symbols from the stock_list.json file
ticker_symbols: List[str]
try:
  with open('stock_list.json') as f:
    ticker_symbols = json.load(f) 
except Exception as e:
  raise f"Error reading stock_list.json: {e}"

# Prepare data sources
# Finnhub
finnhub_client = finnhub.Client(FINNHUB_API_KEY)

# ESG data
esg_dataframe = pd.read_csv('../data/raw/esg-ratings.csv')

# Gets the raw esg row from the csv file, and returns it as a dictionary
def get_esg_data(ticker_symbol: str):
  filtered_df = esg_dataframe[(esg_dataframe['ticker'].str.upper() == ticker_symbol)]
  return filtered_df.to_dict('records')[0] or None


# Extraction functions. These functions will be used to extract data from the various sources
def extract_stock_info(ticker_symbol: str):
  # Get general stock information from Finnhub, needed for the Stock table
  print(f"Fetching stock info from Finnhub for {ticker_symbol}")
  company_profile_response = finnhub_client.company_profile2(symbol=ticker_symbol)
  if not company_profile_response: return
  print(f"Fetching stock info from FMP for {ticker_symbol}")
  # Additional request for getting company description. Commented for now, but we can use it later
  fmp_company_profile_response = fmpsdk.company_profile(FMP_API_KEY, ticker_symbol)
  
  return {
    'ticker_symbol': ticker_symbol,
    'name': company_profile_response['name'],
    'industry': company_profile_response['finnhubIndustry'],
    'market_cap': company_profile_response['marketCapitalization'],
    'country': company_profile_response['country'],
    'description': fmp_company_profile_response[0]['description'],
    'logo': company_profile_response['logo'],
    # Market cap data changes, so added current date to keep track of this
    'updated_at': pd.Timestamp.now()
  }

def extract_pricing_history(ticker_symbol: str):
  # Get pricing history data
  extracted_pricing_history_list = []
  print(f"Fetching pricing history from FMP for {ticker_symbol}")
  # TODO: Make the date range bigger
  daily_price_history = fmpsdk.historical_price_full(FMP_API_KEY, ticker_symbol, '2023-01-01', '2023-02-31')
  for daily_price in daily_price_history:
    pricing_history = {
      'ticker_symbol': ticker_symbol,
      'date': daily_price['date'],
      'open': daily_price['open'],
      'high': daily_price['high'],
      'low': daily_price['low'],
      'close': daily_price['close'],
    }
    extracted_pricing_history_list.append(pricing_history)
  return extracted_pricing_history_list
  
# Extracts data from the csv, and returns as a row 
def extract_esg_data(ticker_symbol: str):
  # Get the raw row from the csv, based on the ticker_symbol
  filtered_df = esg_dataframe[(esg_dataframe['ticker'].str.upper() == ticker_symbol)]
  raw_esg_row = filtered_df.to_dict('records')[0] or None
  if not raw_esg_row: return
  print(f"Extracting ESG data for {ticker_symbol}")
  # Extract & return the relevant data from the row
  return {
    'ticker_symbol': ticker_symbol,
    'date': convert_date(raw_esg_row['last_processing_date']),
    'total_score': raw_esg_row['total_score'],
    'environment_score': raw_esg_row['environment_score'],
    'social_score': raw_esg_row['social_score'],
    'governance_score': raw_esg_row['governance_score'],
  }
# This function will be used to extract the data from the various sources
# It will only add the data for a ticker_symbol to the list, if data is found for all the tables
def extract_data():
  # Initialize lists to store the data. This corresponds to the tables in the database
  stocks_info_list = []
  pricing_history_list = []
  esg_history_list = []
  
  # Loop through the ticker_symbols and gather the data from the various sources
  for ticker_symbol in ticker_symbols:
    # Stock table
    stock_row = extract_stock_info(ticker_symbol)
    if not stock_row:
      # If no data is found for the current ticker_symbol, skip to the next ticker_symbol
      print("No stock data found for ", ticker_symbol)
      break
    stocks_info_list.append(stock_row)
    
    # Pricing_history table 
    extracted_pricing_history_list = extract_pricing_history(ticker_symbol)
    if not extracted_pricing_history_list:
      print("No pricing history data found for ", ticker_symbol)
      stocks_info_list.pop()
      break
    
    # ESG_history table
    esg_row = extract_esg_data(ticker_symbol)
    if not esg_row:
      print("No ESG data found for ", ticker_symbol)
      stocks_info_list.pop()
      break
      
    # Add the extracted_pricing_history_list for the current ticker_symbol to the pricing_history_list. 
    # This is done in this step, to make sure this list is only added when there is also ESG data for the current ticker_symbol
    pricing_history_list = [*pricing_history_list, *extracted_pricing_history_list]
    esg_history_list.append(esg_row)
    
    print(f"Extracted data for stock {ticker_symbol}")
  return stocks_info_list, pricing_history_list, esg_history_list
  
async def main():
  print("Extracting data...")
  stocks_info_list, pricing_history_list, esg_history_list = extract_data()
  generate_csv(stocks_info_list, '../data/transformed/stock.csv')
  generate_csv(pricing_history_list, '../data/transformed/pricing_history.csv', index=True)
  generate_csv(esg_history_list, '../data/transformed/esg_history.csv', index=True)
  print("Done :)")

if __name__ == '__main__':
  asyncio.run(main())
