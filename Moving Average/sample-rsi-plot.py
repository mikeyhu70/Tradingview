import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

def calculate_rsi(data, window=14):
    data['Price_Diff'] = data['Close'].diff()
    data['UpMove'] = np.where(data['Price_Diff'] > 0, data['Price_Diff'], 0)
    data['DownMove'] = np.where(data['Price_Diff'] < 0, -data['Price_Diff'], 0)
    data['AvgUpMove'] = data['UpMove'].rolling(window=window).mean()
    data['AvgDownMove'] = data['DownMove'].rolling(window=window).mean()
    data['RS'] = data['AvgUpMove'] / data['AvgDownMove']
    data['RSI'] = 100 - (100 / (1 + data['RS']))
    return data

ticker = "AAPL"
start_date = "2022-01-01"
end_date = "2023-04-14"

data = yf.download(ticker, start=start_date, end=end_date)
data = calculate_rsi(data)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})

overbought = 70
oversold = 30

segments = []
colors = []
for i in range(len(data) - 1):
    if data['RSI'][i] > overbought:
        colors.append('red')
    elif data['RSI'][i] < oversold:
        colors.append('green')
    else:
        colors.append('blue')
    segments.append([(data.index[i].timestamp(), data['Close'][i]), (data.index[i+1].timestamp(), data['Close'][i+1])])

line_segments = LineCollection(segments, colors=colors, linewidths=1.5)
ax1.add_collection(line_segments)
ax1.autoscale_view()
ax1.set_ylabel('Price')

ax2.plot(data.index, data['RSI'], color='black')
ax2.axhline(overbought, color='red', linestyle='--', label=f'Overbought ({overbought})')
ax2.axhline(oversold, color='green', linestyle='--', label=f'Oversold ({oversold})')
ax2.set_ylabel('RSI')
ax2.set_ylim([0, 100])
ax2.legend(loc='upper left')

plt.tight_layout()
plt.show()