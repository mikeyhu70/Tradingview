import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.dates as mdates

def calculate_rsi(data, window=14):
    data['Price_Diff'] = data['Close'].diff()
    data['UpMove'] = np.where(data['Price_Diff'] > 0, data['Price_Diff'], 0)
    data['DownMove'] = np.where(data['Price_Diff'] < 0, -data['Price_Diff'], 0)
    data['AvgUpMove'] = data['UpMove'].rolling(window=window).mean()
    data['AvgDownMove'] = data['DownMove'].rolling(window=window).mean()
    data['RS'] = data['AvgUpMove'] / data['AvgDownMove']
    data['RSI'] = 100 - (100 / (1 + data['RS']))
    return data

def find_local_extrema(data, n=5):
    local_max = data.rolling(window=n, center=True).max()
    local_min = data.rolling(window=n, center=True).min()
    return local_max, local_min

def find_waves(data, local_max, local_min):
    waves = []
    wave_labels = []
    wave_type = 'impulse'
    wave_count = 1
    for i in range(len(data)):
        if (data['Close'].iloc[i] == local_max.iloc[i]).any():
            if wave_type == 'impulse':
                waves.append(data['Close'].iloc[i])
                wave_labels.append(str(wave_count))
                wave_count += 1
                if wave_count > 5:
                    wave_type = 'corrective'
                    wave_count = 1
            else:
                waves.append(data['Close'].iloc[i])
                wave_labels.append('a')
        elif (data['Close'].iloc[i] == local_min.iloc[i]).any():
            if wave_type == 'impulse':
                waves.append(data['Close'].iloc[i])
                wave_labels.append(str(wave_count))
                wave_count += 1
                if wave_count > 5:
                    wave_type = 'corrective'
                    wave_count = 1
            else:
                waves.append(data['Close'].iloc[i])
                if wave_count == 1:
                    wave_labels.append('b')
                    wave_count += 1
                else:
                    wave_labels.append('c')
                    wave_type = 'impulse'
                    wave_count = 1
    return waves, wave_labels
    waves = []
    wave_labels = []
    wave_type = 'impulse'
    wave_count = 1
    for i in range(len(data)):
        if data['Close'].iloc[i] == local_max.iloc[i]:
            if wave_type == 'impulse':
                waves.append(data['Close'].iloc[i])
                wave_labels.append(str(wave_count))
                wave_count += 1
                if wave_count > 5:
                    wave_type = 'corrective'
                    wave_count = 1
            else:
                waves.append(data['Close'].iloc[i])
                wave_labels.append('a')
        elif data['Close'].iloc[i] == local_min.iloc[i]:
            if wave_type == 'impulse':
                waves.append(data['Close'].iloc[i])
                wave_labels.append(str(wave_count))
                wave_count += 1
                if wave_count > 5:
                    wave_type = 'corrective'
                    wave_count = 1
            else:
                waves.append(data['Close'].iloc[i])
                if wave_count == 1:
                    wave_labels.append('b')
                    wave_count += 1
                else:
                    wave_labels.append('c')
                    wave_type = 'impulse'
                    wave_count = 1
    return waves, wave_labels

def plot_fib_levels(ax, data, waves, wave_labels):
    fib_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1, 1.618, 2.618]
    fib_colors = ['black', 'r', 'g', 'b', 'cyan', 'magenta', 'yellow', 'orange', 'purple']
    for i in range(len(waves)-1):
        if wave_labels[i] in ['1', '3', '5', 'a', 'c']:
            start_price = waves[i]
            end_price = waves[i+1]
            price_range = end_price - start_price
            for level, color in zip(fib_levels, fib_colors):
                fib_price = end_price - price_range * level
                ax.axhline(fib_price, color=color, linestyle='--', alpha=0.5)

ticker = "AAPL"
start_date = "2022-01-01"
end_date = "2023-04-14"

data = yf.download(ticker, start=start_date, end=end_date)
data = calculate_rsi(data)

data['EMA_13'] = data['Close'].ewm(span=13, adjust=False).mean()
data['EMA_34'] = data['Close'].ewm(span=34, adjust=False).mean()

local_max, local_min = find_local_extrema(data)
waves, wave_labels = find_waves(data, local_max, local_min)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
fig.suptitle(f'{ticker} Price, RSI and Elliot Wave', fontsize=16)

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
    segments.append([(mdates.date2num(data.index[i]), data['Close'][i]), (mdates.date2num(data.index[i+1]), data['Close'][i+1])])

line_segments = LineCollection(segments, colors=colors, linewidths=1.5)
ax1.add_collection(line_segments)
ax1.autoscale_view()
ax1.set_ylabel('Price')

ax1.plot(data.index, data['EMA_13'], color='purple', linestyle='--', label='EMA 13')
ax1.plot(data.index, data['EMA_34'], color='orange', linestyle='--', label='EMA 34')
ax1.legend(loc='upper left')

plot_fib_levels(ax1, data, waves, wave_labels)

for i in range(len(waves)):
    ax1.annotate(wave_labels[i], xy=(data.index[data['Close'] == waves[i]][0], waves[i]),
                 xytext=(10, 0), textcoords='offset points', fontsize=12)

ax2.plot(data.index, data['RSI'], color='black')
ax2.axhline(overbought, color='red', linestyle='--', label=f'Overbought ({overbought})')
ax2.axhline(oversold, color='green', linestyle='--', label=f'Oversold ({oversold})')
ax2.set_ylabel('RSI')
ax2.set_ylim([0, 100])
ax2.legend(loc='upper left')

plt.tight_layout()
plt.show()