import pandas as pd
import matplotlib.pyplot as plt
import os

# Define the path to your folder containing CSV files
folder_path = 'S&P500'

# Load all CSV files from the folder
all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
data_list = []

for file in all_files:
    df = pd.read_csv(file, parse_dates=['Date'])  # Adjust the 'Date' column name if needed
    data_list.append(df)

# Combine all DataFrames into a single DataFrame
full_data = pd.concat(data_list, ignore_index=True)

# Sort data by date if necessary
full_data.sort_values('Date', inplace=True)

# Plotting the S&P 500 index values over time
plt.figure(figsize=(10, 5))
plt.plot(full_data['Date'], full_data['High'], label='S&P 500 Index')  # Adjust 'SP500' to your specific column name
plt.title('S&P 500 Index Over Time')
plt.xlabel('Date')
plt.ylabel('Index Value')
plt.legend()
plt.grid(True)
plt.show()
