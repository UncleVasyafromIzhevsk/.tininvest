# Importing all the required libraries

import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import pandas as pd
import matplotlib.dates as mpl_dates
import numpy as np
import datetime


# Defining a dataframe showing stock prices
# of a week
stock_prices = pd.DataFrame({'date': np.array([datetime.datetime(2021, 11, i+1)
											for i in range(7)]),
							'open': [36, 56, 45, 29, 65, 66, 67],
							'close': [29, 72, 11, 4, 23, 68, 45],
							'high': [42, 73, 61, 62, 73, 56, 55],
							'low': [22, 11, 10, 2, 13, 24, 25]})

ohlc = stock_prices.loc[:, ['date', 'open', 'high', 'low', 'close']]
ohlc['date'] = pd.to_datetime(ohlc['date'])
ohlc['date'] = ohlc['date'].apply(mpl_dates.date2num)
ohlc = ohlc.astype(float)

# Creating Subplots
fig, ax = plt.subplots()

candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='blue',
				colordown='green', alpha=0.4)

# Setting labels & titles
ax.set_xlabel('Date')
ax.set_ylabel('Price')
fig.suptitle('Stock Prices of a week')

# Formatting Date
date_format = mpl_dates.DateFormatter('%d-%m-%Y')
ax.xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()

fig.tight_layout()

plt.show()
