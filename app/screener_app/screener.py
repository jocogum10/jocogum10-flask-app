import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt
import time


# sort the stock list
def sorted_stock(stock_list):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(stock_list, key = alphanum_key)

# list all the stock in the dataset
def list_of_stock():
    stock_names = []
    for name in os.listdir('app/dataset/'):
        name = str(name)
        stock_names.append(name.split('.')[0])
    a = sorted_stock(stock_names)
    return a

# load the stock into a dataframe
def load_stock(name=''):
    stock_name = name.upper()
    df = pd.read_csv('app/dataset/{}.csv'.format(stock_name))
    df1 = df[['Last', 'Date', 'MA 20', 'MA 50', 'STS(14,3,3)', 'RSI(14)', 'High', 'Low']]
    # rename the fast stoch
    df1 = df1.rename(columns={'STS(14,3,3)': '%K'}) 
    # sort the dataframe by date
    df = df1.set_index('Date') 
    df = df.sort_index(ascending=True)
    # calculate the stochastic
    df['%D'] = df['%K'].rolling(3).mean()
    df['MA 8'] = df['Last'].rolling(8).mean()
    df_complete = calculate_chop(stock_df=df, period=28)
    return df_complete

# class CrossUpScreener():
#     """20 day moving average crosses up 50 day moving average"""
#     def __init__(self, stock_selected, date):
#         self.df = stock_selected
#         self.date = date
#         self.entry_strat = ['MA 20 Cross Up MA 50']
#         self.exit_strat = ['MA 20 Cross Down MA 50']
#         self.screen()

#     def screen(self):
