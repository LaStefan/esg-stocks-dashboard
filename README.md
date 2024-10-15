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
   - Links: datasets, video etc.

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
Existing Indicators and Visualizations (50-150 words): 
    For each indicator/visualization you have implemented so far, 
        CSF/KPI supported by the indicator
        Original data source(s) used to create this indicator
        If the indicator is computed using multiple attributes or data sources, explain how is it computed
        Which files in your code (python, html, javascript etc) generates the indicator

### ESG scores against Market Capitalization
The ESG scores are scatter plotted against the companies market capitalization visualized using a python script. It is inner joined with sql queried using the stock and esg_history csv's. 

### Price trend over time
The price trend over time including a moving average of the close price is generated using a Python script. The source of this data is from the FMP API.

### Analyst recommendations
The analyst recommendations shows an overview of the recommended action to take from a collection of analysts, per stock. 

### other KPI's

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
