import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt
import time

# calculate the gain and return the overall gain in 2 decimal float
def calculate_gain(buy, sell, df_clean):
    overall_gain = []
    for i in range(len(sell)):
        gain = ((df_clean['Last'][sell[i]]-df_clean['Last'][buy[i]])/df_clean['Last'][buy[i]])*100
        overall_gain.append(gain)
    return round(sum(overall_gain), 2)

# make the matplotlib image and return the string
def make_stock_image(df_clean, Buy, Sell):

    fig, axs = plt.subplots(2, sharex=True, figsize=(8,5), gridspec_kw={'height_ratios': [2, 1]})
    fig.tight_layout()
    #fig.suptitle('Sharing both axes')
    axs[0].plot(df_clean['Last'], label='Last Price', c='blue', alpha=0.5)
    axs[0].plot(df_clean['MA 20'],label='MA 20', c='black', alpha=0.9)
    axs[0].plot(df_clean['MA 50'],label='MA 50', c='magenta', alpha=0.9)
    axs[0].plot(df_clean['MA 8'],label='MA 8', c='red', alpha=0.9)
    axs[0].scatter(df_clean.iloc[Buy].index, df_clean.iloc[Buy]['Last'], marker='^', color='g', s=100)
    axs[0].scatter(df_clean.iloc[Sell].index, df_clean.iloc[Sell]['Last'], marker='v', color='r', s=100)
    axs[0].grid(which='major', alpha=0.5)

    axs[1].plot(df_clean['RSI(14)'],label='RSI(14)', c='green', alpha=0.9)
    axs[1].plot(df_clean['%K'],label='%K', c='blue', alpha=0.5)
    axs[1].plot(df_clean['%D'],label='%D', c='red', alpha=0.5)
    axs[1].plot(df_clean['CHOP(28)'],label='CHOP(28)', c='red', alpha=0.9)
    axs[1].grid(which='major', alpha=0.5)
    
    plt.yticks(np.arange(0, 100, 10))
    plt.xticks(np.arange(0, len(df_clean.index)+1, 20))
    plt.xticks(rotation='60')
    
    new_graph_name = "stock" + str(time.time()) + ".png"

    for filename in os.listdir('app/static/images'):
        if filename.startswith('stock'):  # not to remove other images
            os.remove('app/static/images/' + filename)

    plt.savefig("app/static/images/" + new_graph_name, dpi=100, bbox_inches ="tight", pad_inches = 0.5)

    return "/images/" + new_graph_name

# return the list of values of the last price time to buy
def display_when_buy(buy_index, df_clean):
    bought = []
    for i in range(len(df_clean)):
        if i in buy_index:
            bought.append(df_clean['Last'].iloc[i])
    return bought

# return the list of values of the last price when time to sell
def display_when_sell(sell_index, df_clean):
    sold = []
    for i in range(len(df_clean)):
        if i in sell_index:
            sold.append(df_clean['Last'].iloc[i])
    return sold

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

def calculate_chop(period=28, stock_df=None):
    df = stock_df
    n = period
    if df is not None:
        for index, values in df.iterrows():
            try:
                prev_last = df.loc[previous_index, 'Last']
                a = df.loc[index, 'High'] - df.loc[index, 'Low']
                b = abs(df.loc[index, 'High']-prev_last)
                c = abs(df.loc[index, 'Low']-prev_last)
                df.loc[index, 'ATR((1)'] = max(a, b, c)
            except:
                pass
            previous_index = index
        # SUM(ATR(1),n) = sum of the average true range over past n bars
        df['SUM(ATR(1), 28)'] = df['ATR((1)'].rolling(window=n).sum()
        # MaxHi(n) = the highest high over past n bars
        df['MaxHi(28)'] = df['High'].rolling(window=n).max()
        # MaxLo(n) = the lowest low over past n bars
        df['MinLo(28)'] = df['Low'].rolling(window=n).min()
        df['CHOP(28)'] = 100 * np.log10(df['SUM(ATR(1), 28)']/(df['MaxHi(28)']-df['MinLo(28)']))/np.log10(n)
        df_clean = df[['Last', 'MA 20', 'MA 50', 'MA 8', 'RSI(14)', '%K', '%D', 'CHOP(28)']]
    return df_clean



class CrossUpStrategy():
    """20 day moving average crosses up 50 day moving average"""
    def __init__(self, stock_selected):
        self.df = stock_selected
        self.entry_strat = ['MA 20 Cross Up MA 50']
        self.exit_strat = ['MA 20 Cross Down MA 50']
        self.buy = []
        self.sell = []
        self.backtest()
        self.gain = calculate_gain(self.buy, self.sell, self.df)
        self.image_link = make_stock_image(self.df, self.buy, self.sell)
        self.buy_list = display_when_buy(self.buy, self.df)
        self.sell_list = display_when_sell(self.sell, self.df)
        self.bought_sold = zip(self.buy_list, self.sell_list)

    def backtest(self):
        bought = False
        for i in range(len(self.df)):
            if self.df['MA 20'].iloc[i] > self.df['MA 50'].iloc[i] and not bought:
                self.buy.append(i)
                bought = True
            elif self.df['MA 20'].iloc[i] < self.df['MA 50'].iloc[i] and bought:
                self.sell.append(i)
                bought = False