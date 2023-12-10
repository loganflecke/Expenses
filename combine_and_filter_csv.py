import pandas as pd
from datetime import datetime, timedelta
import sys
import json
import os

try:
    with open("config.json", "r") as config_file:
        config_data = json.load(config_file)

    # Access values from the variable names
    category = config_data['headers']['category']
    grocery = config_data['headers']['grocery']
    retailer = config_data['headers']['retailer']
    cost = config_data['headers']['cost']

    transaction_path = config_data['filePaths']['transactionPath']

except FileNotFoundError:
    print(f"Error: Configuration file '{file_path}' not found.")
    raise

def main():
    # Check if at least two arguments are provided
    if sys.argv[1] == "-h":
        print("Usage: python combine_and_filter_csv.py")
        print("     -o <output file>")
        print("     -f <filtered output file>")
        print("     -c <categorized output file")
        return

    input_files = [f for f in os.listdir(transaction_path) if os.path.isfile(os.path.join(transaction_path, f))]

    output_file = config_data['outputFiles']['combined']
    filtered_output_file = config_data['outputFiles']['filtered']
    categorized_output_file = config_data['outputFiles']['categorized']

    for i in range(len(sys.argv)):        
        if sys.argv[i] == "-o":
            output_file = sys.argv[(i+1)]
        elif sys.argv[i] == "-c":
            categorized_output_file = sys.argv[(i+1)]
        elif sys.argv[i] == "-f":
            filtered_output_file = sys.argv[(i+1)]    

    # Call the functions
    merged_df = merge_csv(input_files, output_file)
    filtered_df = filter_csv_date(merged_df, output_file, filtered_output_file)
    categories_df = filter_csv_categories(filtered_df, output_file, categorized_output_file)
    print_data(output_file, filtered_output_file, categorized_output_file, categories_df)    

# Combine multiple CSV files into one and remove duplicate lines
def merge_csv(input_files, output_file):
        dfs = [pd.read_csv(os.path.join(transaction_path, file)) for file in input_files]
        merged_df = pd.concat(dfs).drop_duplicates()
        merged_df.to_csv(output_file, index=False)
        return merged_df

# get the last month of data
def filter_csv_date(merged_df, output_file, filtered_output_file):
    date_format = "%Y-%m-%d"
    merged_df.iloc[:, 1] = pd.to_datetime(merged_df.iloc[:, 1], format=date_format)
    cutoff_date = datetime.now() - timedelta(days=30)
    filtered_df = merged_df[merged_df.iloc[:, 1] >= cutoff_date]
    filtered_df.to_csv(filtered_output_file, index=False)
    return filtered_df

# categorize based on transaction categories
def filter_csv_categories(filtered_df, output_file, categorized_output_file):
    filtered_df.loc[filtered_df[retailer].str.contains(grocery, case=False), category] = 'Grocery'
    categories_df = filtered_df.groupby(category)[cost].sum().reset_index()
    categories_df.to_csv(categorized_output_file, index=False)
    return categories_df

# print data to the console
def print_data(output_file, filtered_output_file, categorized_output_file, categories_df):
    print(f"Merged CSV written to: {output_file}")
    print(f"Filtered CSV written to: {filtered_output_file}")
    print(f"Categorized CSV written to: {categorized_output_file}")
    print(categories_df)


if __name__ == "__main__":
    main()