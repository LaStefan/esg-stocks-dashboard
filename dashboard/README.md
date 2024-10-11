# Dashboard
This folder contains all the code for running the dashboard

## Setup requirements
- Make sure you have a .env file inside of this folder, containing the necessary variables
- Install requirements with `pip install -r requirements.txt`
<!-- TODO: Add instructions for running the seeding scripts -->

## Fetching new data
To fetch new data, run the `fetch_data.py` script
This file expects two environment variables: "FINNHUB_API_KEY" and "FMP_API_KEY"
To get this working, copy the .env.example file and rename it to '.env'
Then, run the file by doing `python fetch_data.py` (assuming you are in the `dashboard` directory)