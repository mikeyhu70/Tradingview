import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf


def calculate_rsi(data, window=14):
    data['Price_Diff'] = data['Close'].diff()
    data['UpMove'] = np.where(data['Price_Diff'] > 0, data['Price_Diff'], 0)
    data['DownMove'] = np.where(data['Price_Diff'] < 0, -data['Price_Diff'], 0)
    data['AvgUpMove'] = data['UpMove'].rolling(window=window).mean()
    data['AvgDownMove'] = data['DownMove'].rolling(window=window).mean()
    data['RS'] = data['AvgUpMove'] / data['AvgDownMove']
    data['RSI'] = 100 - (100 / (1 + data['RS']))
    return data

ticker = "LABU"
start_date = "2022-01-01"
end_date = "2024-04-14"

data = yf.download(ticker, start=start_date, end=end_date)
data = calculate_rsi(data)

data['EMA_13'] = data['Close'].ewm(span=13, adjust=False).mean()
data['EMA_34'] = data['Close'].ewm(span=34, adjust=False).mean()

overbought = 70
oversold = 30

apds = [
    mpf.make_addplot(data['EMA_13'], color='purple', linestyle='--'),
    mpf.make_addplot(data['EMA_34'], color='orange', linestyle='--'),
    mpf.make_addplot(data['RSI'], color='black', panel=1, ylabel='RSI'),
    mpf.make_addplot([overbought] * len(data), color='red', linestyle='--', panel=1),
    mpf.make_addplot([oversold] * len(data), color='green', linestyle='--', panel=1)
]
fig, axlist = mpf.plot(
    data, 
    type='candle',
    volume=False,
    style='yahoo',
    title=f'{ticker} Price and RSI',
    ylabel='Price',
    addplot=apds,
    figsize=(25,12),
    returnfig=True,
    panel_ratios=(4,1)  # Adjust the ratio of the main panel to the RSI panel
)

ax1 = axlist[0]
ax1.legend(['EMA 13', 'EMA 34'])

ax2 = axlist[2]
ax2.legend(['RSI', f'Overbought ({overbought})', f'Oversold ({oversold})'], loc='lower right')
ax2.set_ylim([0, 100])

# Annotate the last candlestick date on the RSI plot
last_date = data.index[-1].strftime('%Y-%m-%d')
ax2.annotate(last_date, xy=(0.95, 0.95), xycoords='axes fraction', fontsize=12, 
             horizontalalignment='right', verticalalignment='top')

fig.subplots_adjust(hspace=0.3)  # Adjust the vertical space between subplots

fig.savefig('chart.png', dpi=300)
plt.show()