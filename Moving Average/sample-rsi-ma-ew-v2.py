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

def is_impulse(wave):
    if len(wave) != 5:
        return False
    if wave[3] < wave[1] or wave[3] < wave[4]:
        return False
    if wave[2] > wave[0] or wave[2] > wave[4]: 
        return False
    if min(wave[1], wave[3]) < wave[0]:
        return False
    return True

def is_corrective(wave):
    if len(wave) != 3:
        return False
    if wave[2] > wave[0]:
        return False
    return True

def find_elliott_waves(data):
    waves = []
    wave = []
    for i in range(len(data)):
        if not wave:
            wave.append(i)
        else:
            if data['Close'][i] > data['Close'][wave[-1]]:
                wave.append(i)
            else:
                if len(wave) > 2:
                    if is_impulse(data['Close'][wave].tolist()):
                        waves.append((wave, 'impulse'))
                    elif is_corrective(data['Close'][wave].tolist()):
                        waves.append((wave, 'corrective'))
                wave = [i]
    return waves

ticker = "AAPL"
start_date = "2022-01-01"
end_date = "2023-04-14"

data = yf.download(ticker, start=start_date, end=end_date)
data = calculate_rsi(data)

data['EMA_13'] = data['Close'].ewm(span=13, adjust=False).mean()
data['EMA_34'] = data['Close'].ewm(span=34, adjust=False).mean()

waves = find_elliott_waves(data)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
fig.suptitle(f'{ticker} Price and RSI with Elliott Waves', fontsize=16)

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

for wave, wave_type in waves:
    if wave_type == 'impulse':
        ax1.plot(data.index[wave], data['Close'][wave], color='purple')
        ax1.annotate('(1)', (data.index[wave[0]], data['Close'][wave[0]]), xytext=(-10,10), textcoords='offset points')
        ax1.annotate('(2)', (data.index[wave[1]], data['Close'][wave[1]]), xytext=(-10,10), textcoords='offset points')
        ax1.annotate('(3)', (data.index[wave[2]], data['Close'][wave[2]]), xytext=(-10,10), textcoords='offset points')
        ax1.annotate('(4)', (data.index[wave[3]], data['Close'][wave[3]]), xytext=(-10,10), textcoords='offset points')
        ax1.annotate('(5)', (data.index[wave[4]], data['Close'][wave[4]]), xytext=(-10,10), textcoords='offset points')
    else:
        ax1.plot(data.index[wave], data['Close'][wave], color='orange')
        ax1.annotate('(A)', (data.index[wave[0]], data['Close'][wave[0]]), xytext=(-10,10), textcoords='offset points')
        ax1.annotate('(B)', (data.index[wave[1]], data['Close'][wave[1]]), xytext=(-10,10), textcoords='offset points')
        ax1.annotate('(C)', (data.index[wave[2]], data['Close'][wave[2]]), xytext=(-10,10), textcoords='offset points')

ax1.plot(data.index, data['EMA_13'], color='purple', linestyle='--', label='EMA 13') 
ax1.plot(data.index, data['EMA_34'], color='orange', linestyle='--', label='EMA 34')
ax1.legend(loc='upper left')

ax2.plot(data.index, data['RSI'], color='black')
ax2.axhline(overbought, color='red', linestyle='--', label=f'Overbought ({overbought})')
ax2.axhline(oversold, color='green', linestyle='--', label=f'Oversold ({oversold})')
ax2.set_ylabel('RSI')
ax2.set_ylim([0, 100])
ax2.legend(loc='upper left')

plt.tight_layout()
plt.show()