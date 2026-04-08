import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

print("MarketMind AI: Fetching Live Market Data...")

# Yahan kisi bhi company ka ticker daal sakte ho (Jaise AAPL, TSLA, ya Indian market ke liye TATAMOTORS.NS)
ticker_symbol = "AAPL" 

# Pichle 5 saal ka data uthao
data = yf.download(ticker_symbol, start="2019-01-01", end="2026-04-01")

# Humein sirf 'Close' price (Din ke end ka rate) se matlab hai prediction ke liye
df = data[['Close']]

print("\nData Head (Pehle 5 din):")
print(df.head())

# Data ko graph pe dekhte hain
plt.figure(figsize=(10,5))
plt.plot(df.index, df['Close'], color='cyan')
plt.title(f"{ticker_symbol} Stock Price History")
plt.xlabel("Date")
plt.ylabel("Price")
plt.grid(True)
plt.show()

print("Data successfully loaded!")