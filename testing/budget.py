import tkinter as tk
from tkinter import filedialog
import pandas as pd
from datetime import datetime, timedelta
import json
import os

with open("config.json", "r") as config_file:
    config_data = json.load(config_file)

category = config_data['headers']['category']
grocery = config_data['headers']['grocery']
retailer = config_data['headers']['retailer']
cost = config_data['headers']['cost']
transaction_path = config_data['filePaths']['transactionPath']

def merge_csv(input_files, output_file):
    dfs = [pd.read_csv(os.path.join(transaction_path, file)) for file in input_files]
    merged_df = pd.concat(dfs).drop_duplicates()
    merged_df.to_csv(output_file, index=False)
    return merged_df

def filter_csv_date(merged_df, output_file, filtered_output_file):
    date_format = "%Y-%m-%d"
    merged_df.iloc[:, 1] = pd.to_datetime(merged_df.iloc[:, 1], format=date_format)
    cutoff_date = datetime.now() - timedelta(days=30)
    filtered_df = merged_df[merged_df.iloc[:, 1] >= cutoff_date]
    filtered_df.to_csv(filtered_output_file, index=False)
    return filtered_df

def filter_csv_categories(filtered_df, output_file, categorized_output_file):
    filtered_df.loc[filtered_df[retailer].str.contains(grocery, case=False), category] = 'Grocery'
    categories_df = filtered_df.groupby(category)[cost].sum().reset_index()
    categories_df.to_csv(categorized_output_file, index=False)
    return categories_df

def print_data(output_file, filtered_output_file, categorized_output_file, categories_df):
    result_text.set(f"Merged CSV written to: {output_file}\n"
                    f"Filtered CSV written to: {filtered_output_file}\n"
                    f"Categorized CSV written to: {categorized_output_file}\n\n"
                    f"{categories_df}")

def run_script():
    try:
        input_files = [f for f in os.listdir(transaction_path) if os.path.isfile(os.path.join(transaction_path, f))]

        output_file = output_entry.get()
        filtered_output_file = filtered_entry.get()
        categorized_output_file = categorized_entry.get()

        merged_df = merge_csv(input_files, output_file)
        filtered_df = filter_csv_date(merged_df, output_file, filtered_output_file)
        categories_df = filter_csv_categories(filtered_df, output_file, categorized_output_file)
        print_data(output_file, filtered_output_file, categorized_output_file, categories_df)
    except FileNotFoundError:
        result_text.set(f"Error: Configuration file 'config.json' not found.")
    except Exception as e:
        result_text.set(f"An error occurred: {str(e)}")

root = tk.Tk()
root.title("CSV Processing Tool")

result_text = tk.StringVar()

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=20, pady=20)

output_label = tk.Label(frame, text="Output File:")
output_label.grid(row=0, column=0, padx=5, pady=5)

output_entry = tk.Entry(frame)
output_entry.grid(row=0, column=1, padx=5, pady=5)

filtered_label = tk.Label(frame, text="Filtered Output File:")
filtered_label.grid(row=1, column=0, padx=5, pady=5)

filtered_entry = tk.Entry(frame)
filtered_entry.grid(row=1, column=1, padx=5, pady=5)

categorized_label = tk.Label(frame, text="Categorized Output File:")
categorized_label.grid(row=2, column=0, padx=5, pady=5)

categorized_entry = tk.Entry(frame)
categorized_entry.grid(row=2, column=1, padx=5, pady=5)

run_button = tk.Button(frame, text="Run Script", command=run_script)
run_button.grid(row=3, columnspan=2, pady=10)

result_label = tk.Label(frame, textvariable=result_text)
result_label.grid(row=4, columnspan=2)

root.mainloop()
