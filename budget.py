# budget.py
from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)
category = 'Category'
grocery = ['KROGER', 'wholefoods', 'traderjoes', 'gianteagle', 'aldis']
retailer = 'Description'
cost = 'Debit'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            transaction_path = request.form['transaction_path']
            combined = request.form['output']
            filtered = request.form['filtered']
            categorized = request.form['categorized']

            input_files = [f for f in os.listdir(transaction_path) if os.path.isfile(os.path.join(transaction_path, f))]

            merged_df = merge_csv(transaction_path, input_files, combined)
            filtered_df = filter_csv_date(merged_df, combined, filtered)
            categories_df = filter_csv_categories(filtered_df, combined, categorized)
            result_text = print_data(combined, filtered, categorized, categories_df, filtered_df)

            return render_template('index.html', result_text=result_text, transaction_path=transaction_path,
                                   combined=combined, filtered=filtered, categorized=categorized)

        except Exception as e:
            result_text = f"An error occurred: {str(e)}"
            return render_template('index.html', result_text=result_text)
    else:
        # Default rendering for the initial page load
        return render_template('index.html')



def merge_csv(transaction_path, input_files, combined):
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
    result_text = ""
    for index, row in categories_df.iterrows():
        category_name = row['Category']
        total_cost = row['Debit']
        result_text += f"{category_name.ljust(30)} {total_cost}\n"

    result_text += f"\nOther Transactions:\n"
    other_df = filtered_df[filtered_df['Category'].str.contains('Other')]

    for index, row in other_df.iterrows():
        result_text += f"{row['Description'].ljust(30)} {row['Debit']}\n"

    return result_text

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
