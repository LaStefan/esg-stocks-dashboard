from flask import Flask, render_template

# Initialise Flask app
app = Flask(__name__)

@app.route('/home')
def hello():
    return 'Welcome to the coolest data science project!'

@app.route('/')
def index():
    stocks = ["APPL","MCFT","S&P500", "NASDAQ100", "ALPHABET"]
    return render_template("index.html", stocks = stocks) 

