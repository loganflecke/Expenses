import tkinter as tk
import pandas as pd
from datetime import datetime, timedelta
import os
import argparse
import sys

category = 'Category'
grocery = ['KROGER', 'wholefoods', 'traderjoes', 'gianteagle', 'aldis']
retailer = 'Description'
cost = 'Debit'
transaction_path = './Transactions'

parser = argparse.ArgumentParser(description='Command-line arguments example')

# Add optional arguments (flags)
parser.add_argument('-c', '--categorized', help='Categorized file path')
parser.add_argument('-f', '--filtered', help='Filtered file path')
parser.add_argument('-o', '--output', help='Output file path')

# Parse the command-line arguments
args = parser.parse_args()

# Access the values of the flags
categorized = args.categorized or "categorized.csv"
filtered = args.filtered or "filtered.csv"
combined = args.output or "combined.csv"

def merge_csv(input_files, combined):
    dfs = [pd.read_csv(os.path.join(transaction_path, file)) for file in input_files]
    merged_df = pd.concat(dfs).drop_duplicates()
    merged_df.to_csv(combined, index=False)
    return merged_df

def filter_csv_date(merged_df, combined, filtered):
    date_format = "%Y-%m-%d"
    merged_df.iloc[:, 1] = pd.to_datetime(merged_df.iloc[:, 1], format=date_format)
    cutoff_date = datetime.now() - timedelta(days=30)
    filtered_df = merged_df[merged_df.iloc[:, 1] >= cutoff_date]
    filtered_df.to_csv(filtered, index=False)
    return filtered_df

def filter_csv_categories(filtered_df, combined, categorized):
    filtered_df.loc[filtered_df[retailer].isin(grocery), category] = 'Grocery'
    categories_df = filtered_df.groupby(category)[cost].sum().reset_index()
    categories_df.to_csv(categorized, index=False)
    return categories_df

def print_data(combined, filtered, categorized, categories_df, filtered_df):
    for index, row in categories_df.iterrows():
        category_name = row[category]
        total_cost = row[cost]
        result_text.set(result_text.get() + f"{category_name.ljust(30)} {total_cost}\n")

    result_text.set(result_text.get() + f"\nOther Transactions:\n")
    other_df = filtered_df[filtered_df[category].str.contains('Other')]

    for index, row in other_df.iterrows():
        result_text.set(result_text.get() + f"{row[retailer].ljust(30)} {row[cost]}\n")

def run_script():
    try:
        input_files = [f for f in os.listdir(transaction_path) if os.path.isfile(os.path.join(transaction_path, f))]

        combined = output_entry.get()
        filtered = filtered_entry.get()
        categorized = categorized_entry.get()

        merged_df = merge_csv(input_files, combined)
        filtered_df = filter_csv_date(merged_df, combined, filtered)
        categories_df = filter_csv_categories(filtered_df, combined, categorized)
        print_data(combined, filtered, categorized, categories_df, filtered_df)
    except Exception as e:
        result_text.set(f"An error occurred: {str(e)}")

root = tk.Tk()
root.title("Budget Processing Tool")

result_text = tk.StringVar()

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=20, pady=20)

transaction_label = tk.Label(frame, text="Transaction Directory Path:")
transaction_label.grid(row=0, column=0, padx=5, pady=5)

transaction_entry = tk.Entry(frame)
transaction_entry.insert(0, transaction_path)
transaction_entry.grid(row=0, column=1, padx=5, pady=5)

output_label = tk.Label(frame, text="Output File:")
output_label.grid(row=1, column=0, padx=5, pady=5)

output_entry = tk.Entry(frame)
output_entry.insert(0, combined)
output_entry.grid(row=1, column=1, padx=5, pady=5)

filtered_label = tk.Label(frame, text="Filtered Output File:")
filtered_label.grid(row=2, column=0, padx=5, pady=5)

filtered_entry = tk.Entry(frame)
filtered_entry.insert(0, filtered)
filtered_entry.grid(row=2, column=1, padx=5, pady=5)

categorized_label = tk.Label(frame, text="Categorized Output File:")
categorized_label.grid(row=3, column=0, padx=5, pady=5)

categorized_entry = tk.Entry(frame)
categorized_entry.insert(0, categorized)
categorized_entry.grid(row=3, column=1, padx=5, pady=5)

run_button = tk.Button(frame, text="Run Script", command=run_script)
run_button.grid(row=4, columnspan=2, pady=10)

result_label = tk.Label(frame, textvariable=result_text)
result_label.grid(row=5, columnspan=2)

root.mainloop()
