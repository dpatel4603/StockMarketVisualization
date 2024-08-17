import pandas as pd
import os


# Define the path to your folder containing CSV files
folder_path = 'S&P500'

# Load all CSV files from the folder
all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
data_list = []

for file in all_files:
    company_name = os.path.basename(file).replace('.csv', '')
    df = pd.read_csv(file, parse_dates=['Date'])  # Adjust the 'Date' column name if needed
    df['Company'] = company_name  # Add a new column with the company name
    data_list.append(df)

# Combine all DataFrames into a single DataFrame
full_data = pd.concat(data_list, ignore_index=True)

# Sort data by date if necessary
full_data.sort_values('Date', inplace=True)

full_data.to_pickle('S&P500_Data.pkl')
