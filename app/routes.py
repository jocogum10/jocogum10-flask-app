from app import app
from flask import render_template, url_for, request
from app.backtester_app import strategies
from app.screener_app import screener
from app.journal_app import journal
import pandas as pd

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/backtester', methods=['POST', 'GET'])
def backtester():
    list_stock = strategies.list_of_stock()
    stock = request.form.get('stock_selected', None)
    if request.method == 'POST':
        strategy = request.form.get('strategy_selected', None)
        stock_selected = strategies.load_stock(stock)
        if strategy == 'cross_up':
            strat = strategies.CrossUpStrategy(stock_selected)
            return render_template('backtester.html', 
                            list_stocks=list_stock,
                            current_stock=stock, 
                            strategy=strategy, 
                            gain=strat.gain, 
                            photo=strat.image_link, 
                            bought_sold=strat.bought_sold,
                            strategy_entry=strat.entry_strat,
                            strategy_exit=strat.exit_strat)
    else:
        stock_selected = pd.DataFrame(columns=['Last','MA 20','MA 50','%K','RSI(14)','High','Low', '%D','MA 8'])
        return render_template('backtester.html', 
                                list_stocks=list_stock,
                                current_stock=stock, 
                                strategy='', 
                                gain=0, 
                                photo='', 
                                bought_sold=zip([0], [0]),
                                strategy_entry=[],
                                strategy_exit=[])

@app.route('/screener')
def screener():
    return render_template('screener.html')

@app.route('/journal')
def journal():
    return render_template('journal.html')

@app.route('/hello')
def hello():
    return render_template('hello.html')