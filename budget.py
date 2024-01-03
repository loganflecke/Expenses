from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime, timedelta
import os
from functools import reduce

app = Flask(__name__)

## THESE ARE HEADER NAMES STRAIGHT FROM THE CSV. CHANGE THEM TO FIT YOUR FORMATTING
category = 'Category'
retailer = 'Description'
cost = 'Debit'
date = 'Transaction Date'
myCard = ## CHANGE TO THE LAST 4 DIGITS OF YOUR CARD

## THESE ARE THE NAMES OF GROCERIES AS THEY APPEAR ON THE TRANSACTIONS CSV FILE
grocery = ['KROGER', 'wholefoods', 'traderjoes', 'gianteagle', 'aldis']

## OUTPUT FILES. FEEL FREE TO REMOVE
combined = "combined.csv"
filtered = "filtered.csv"
categorized = "categorized.csv"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            num_days = request.form['num_days']
            transaction_path = request.form['transaction_path']

            input_files = [f for f in os.listdir(transaction_path) if os.path.isfile(os.path.join(transaction_path, f))]

            merged_df = merge_csv(transaction_path, input_files)
            filtered_df = filter_date_and_card(num_days, merged_df)
            categories_total_df = filter_csv_categories(filtered_df)
            grouped_categories = groupby_categories(filtered_df, categories_total_df)
            categories_text = print_data(categories_total_df)
            transactions_text = print_data(filtered_df)
            sum_text = filtered_df[cost].sum()
            date_range_text = str(format_date(filtered_df[date].iloc[-1]) + " - " + format_date(filtered_df[date].iloc[0]))

            return render_template('index.html', date_range_text=date_range_text, sum_text=sum_text, grouped_categories=grouped_categories, categories_text=categories_text, transactions_text=transactions_text, num_days=num_days, transaction_path=transaction_path)

        except Exception as e:
            result_text = f"An error occurred: {str(e)}"    
            return render_template('index.html', date_range_text=date_range_text, sum_text=sum_text, grouped_categories=grouped_categories, categories_text=categories_text, transactions_text=transactions_text)
    elif request.method == 'GET':
        return render_template('index.html')

def format_date(date_value):
    return pd.to_datetime(date_value).strftime('%B %d, %Y')

def merge_csv(transaction_path, input_files):
    dfs = [pd.read_csv(os.path.join(transaction_path, file)) for file in input_files]
    merged_df = pd.concat(dfs).drop_duplicates(subset=[retailer, cost, date])
    merged_df.to_csv(combined, index=False)
    return merged_df

def filter_date_and_card(num_days, merged_df):
    date_format = "%Y-%m-%d"
    merged_df.iloc[:, 1] = pd.to_datetime(merged_df.iloc[:, 1], format=date_format)
    cutoff_date = datetime.now() - timedelta(days=int(num_days))
    filtered_df = merged_df[merged_df.iloc[:, 1] >= cutoff_date]
    filtered_df = filtered_df[filtered_df.iloc[:, 2] == myCard]
    filtered_df = filtered_df.sort_values(by=[date], ascending=False)
    filtered_df.to_csv(filtered, index=False)
    return filtered_df

def filter_csv_categories(filtered_df):
    for i in grocery:
        condition_grocery = filtered_df[retailer].str.contains(i, case=False, na=False)
        condition_not_fuel = ~filtered_df[retailer].str.contains('FUEL', case=False, na=False)
        if condition_grocery.any() and condition_not_fuel.any():
            filtered_df.loc[condition_grocery & condition_not_fuel, category] = 'Grocery'

    categories_total_df = filtered_df.groupby(category)[cost].sum().round(2).reset_index()
    categories_total_df.to_csv(categorized, index=False)
    return categories_total_df

def groupby_categories(filtered_df, categories_total_df):
    result_text = ""
    for i,r in categories_total_df.iterrows():
        category_df = filtered_df[filtered_df.iloc[:, 4] == categories_total_df.iloc[i, 0]]
        result_text += f"\n{categories_total_df.iloc[i, 0]}:\n"
        for index, row in category_df.iterrows():
            result_text += f"{row[retailer].ljust(30)} {row[cost]}\n"
    return result_text

def print_data(dataframe):
    result_text = ""
    for index, row in dataframe.iterrows():
        try:
            result_text += f"{row[date].ljust(20)} {row[category].ljust(20)} {row[retailer].ljust(30)} {row[cost]}\n"
        except:
            result_text += f"{row[category].ljust(30)} {row[cost]}\n"
    return result_text

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
