# Data Science and Society Dashboard: ESG Stocks Application

Welcome to the ESG Stocks Application! This is a project related to Data Science & Society course. It focuses on the analysis and metrics of ESG (Environment, Social, Governance) scores related to most popular stocks from S&P 500 and NASDAQ indexes. The idea of this project is to help investors make information based decisions for sustainable investing. 

## Getting started

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/LaStefan/esg-stocks-dashboard.git
   cd esg-stocks-dashboard

2. **Start the App:**
    ```bash
    docker compose up -d

3. **Access the Application:**
    - Streamlit App: Visit http://localhost:8501 in your browser.
    - Jupyter Notebook: Visit http://127.0.0.1:8888/ and follow the instructions in the terminal to access your notebooks.

4. **Relevant links**
   - Video link: https://solisservices.sharepoint.com/:v:/s/DataScience-Team13/EQotC56hb5NGvUIe6-ueHWEBPTpcBuwIyeAOB0Ak-uj1Pw?e=DDBQVf 

## Data Preparation and Collection
During this process we collected data from various sources such as public APIs and data sets already stored in the CSV files. We used an ETL process for our project in order to do proper data preparation and collection.
- **fetch-data.py** script serves the purpose of extracting data from sources and transforming it. After this it saves the data in respective csv files in /transformed folder.
- **loader.py** script serves the purpose of loading/seeding the data to our Postgres SQL database. 
After this we query the data directly from the database in order to visualise it.

### Data Sources

1. Kaggle ESG ratings: https://www.kaggle.com/datasets/alistairking/public-company-esg-ratings-dataset/data
    This data source we used for getting ESG ratings for around 700 companies. The file is saved in ./data/raw/esg-ratings.csv
2. FINNHUB API: https://finnhub.io/
3. FMP API: https://site.financialmodelingprep.com/
    For two APIs mentioned above we used these to gather data such as company information and stock pricing history.
    They are saved in data/transformed/stock.csv and data/transformed/pricing_history.csv

## Indicators and Visualizations

### ESG scores against Market Capitalization
The ESG scores are scatter plotted against the companies market capitalization visualized using a python script. It is inner joined with sql queried using the stock and esg_history csv's. 

### Price trend over time
The price trend over time including a moving average of the close price is generated using a Python script. The source of this data is from the FMP API.

### Quarterly average margin trend
The quarterly average margin trends of the chosen 10 stocks. Based on the daily open en close prices, generated using Python scripts.

### Analyst recommendations
The analyst recommendations shows an overview of the recommended action to take from a collection of analysts, per stock.

### ESG Score Breakdown Across Industries
The average ESG scores are broken down by industry, providing insights into how different sectors perform in terms of environmental, social, and governance criteria. This was visualized using a Python script after joining the stock and esg_history data through a SQL query.

### ESG Score vs Risk-Adjusted Returns
This chart compares ESG scores with risk-adjusted returns (Sharpe Ratio) to help investors identify companies that offer strong returns relative to their risk while maintaining high sustainability standards. The data was processed using SQL queries from the stock and esg_history CSVs and analyzed in a Python script.

### Total ESG scores divided into categories for each stock
This KPI gives insight in how each stock is performing for each segment of the ESG scale. Which means how sustainable the company is.​ The indicator was computed with two data sources; esg_history.csv and stock information which was gather from the API, SQL query was used to join two tables which were previously loaded into our database. The indicator was initially created in the jupyter notebook (workspace-stefan.ipynb) and then it was beautified with streamlit library in the esg.py script for visualisation in the dashboard app.
## Contributing
### Git

1. Fork the repository
     ```bash
    git clone https://github.com/LaStefan/esg-stocks-dashboard.git

- **if you already cloned the repo make sure to do this always before creating a new branch for your work:**
    ```bash
    git checkout main
    git pull
- In order to update your branch with latest main changes just run
    ```bash
     git fetch && git rebase origin/main

2. Create a new branch (git checkout -b feature-branch).
    - When you do this step make sure you create branch from "dev" (at the end main/master will be used for final version of the app)
3. Commit your changes (git commit -m 'Add new feature').
4. Push to the branch (git push origin feature-branch).
5. Open a pull request.

### Contributors

Authors of this project are:
- Stefan Lazarevic - 7818157
- Jort van Meenen - 3639369
- Jeroen Goossens - 6487882
- Mart Kempenaar - 0541400
- Pelle Verhoeff - 3124536
- Rutger Rouppe van der Voort - 4306619

## License

[MIT](https://choosealicense.com/licenses/mit/)
