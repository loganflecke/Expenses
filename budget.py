from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)
category = 'Category'
grocery = ['KROGER', 'wholefoods', 'traderjoes', 'gianteagle', 'aldis']
retailer = 'Description'
cost = 'Debit'
date = 'Transaction Date'
myCard = 936

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

            merged_df = merge_csv(transaction_path, input_files, combined)
            filtered_df = filter_date_and_card(num_days, merged_df, filtered)
            categories_total_df = filter_csv_categories(filtered_df, combined, categorized)
            grouped_categories = groupby_categories(filtered_df, categories_total_df)
            categories_text = print_data(categories_total_df)
            transactions_text = print_data(filtered_df)
            sum_text = filtered_df[cost].sum()

            return render_template('index.html', sum_text=sum_text, grouped_categories=grouped_categories, categories_text=categories_text, transactions_text=transactions_text, num_days=num_days, transaction_path=transaction_path)

        except Exception as e:
            result_text = f"An error occurred: {str(e)}"    
            return render_template('index.html', sum_text=sum_text, grouped_categories=grouped_categories, categories_text=categories_text, transactions_text=transactions_text)
    else:
        # Default rendering for the initial page load
        return render_template('index.html')

def merge_csv(transaction_path, input_files, combined):
    dfs = [pd.read_csv(os.path.join(transaction_path, file)) for file in input_files]
    merged_df = pd.concat(dfs).drop_duplicates()
    merged_df.to_csv(combined, index=False)
    return merged_df

def filter_date_and_card(num_days, merged_df, filtered):
    date_format = "%Y-%m-%d"
    merged_df.iloc[:, 1] = pd.to_datetime(merged_df.iloc[:, 1], format=date_format)
    cutoff_date = datetime.now() - timedelta(days=int(num_days))
    filtered_df = merged_df[merged_df.iloc[:, 1] >= cutoff_date]
    filtered_df = filtered_df[filtered_df.iloc[:, 2] == myCard]
    filtered_df = filtered_df.sort_values(by=[date], ascending=False)
    filtered_df.to_csv(filtered, index=False)
    return filtered_df

def filter_csv_categories(filtered_df, combined, categorized):
    filtered_df.loc[filtered_df[retailer].isin(grocery), category] = 'Grocery'
    categories_total_df = filtered_df.groupby(category)[cost].sum().reset_index()
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
