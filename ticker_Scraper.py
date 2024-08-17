import yfinance as yf
import pandas as pd
import datetime as dt
import os

# Read the list of S&P 500 companies from Wikipedia
payload = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
first_table = payload[0]

df = first_table

symbols = df['Symbol'].values.tolist()

# Create a folder for S&P500 data if it doesn't exist
folder_path = 'S&P500'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Download stock data and save as CSV in the folder
for symbol in symbols:
    stock = yf.Ticker(symbol)
    new_df = stock.history(start=dt.date(2000, 1, 1), end=dt.date(2024, 8, 17), interval='1d')
    file_path = os.path.join(folder_path, symbol + ".csv")
    new_df.to_csv(file_path)
    print(f"Added: {file_path}")
