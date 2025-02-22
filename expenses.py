from flask import Flask, render_template, request
import pandas as pd
import os

## THESE ARE HEADER NAMES STRAIGHT FROM THE CSV. CHANGE THEM TO FIT YOUR FORMATTING
category = 'Category'
retailer = 'Description'
cost = 'Debit'
date = 'Transaction Date'

excel_filename = "transactions.xlsx"

## THESE ARE THE NAMES OF GROCERIES AS THEY APPEAR ON THE TRANSACTIONS CSV FILE
grocery_keywords = ['KROGER', 'GIANT', 'wholefoods', 'traderjoes', 'gianteagle', 'aldis', 'FOOD LION']

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            transaction_path = request.form.get('transaction_path')
            excel = request.form.get('excel')

            input_files = [f for f in os.listdir(transaction_path) if os.path.isfile(os.path.join(transaction_path, f))]

            merged_transactions = merge_transactions(transaction_path, input_files)
            filtered_transactions = filter_transaction_by_date(start_date, end_date, merged_transactions)
            daily_transactions = daily_totals(filtered_transactions, start_date, end_date)
            categories_summary = summarize_categories(filtered_transactions)

            grouped_categories_text = generate_category_group_text(filtered_transactions, categories_summary)
            categories_text = generate_category_text(categories_summary)
            transactions_text = generate_transaction_text(filtered_transactions)
            total_cost = filtered_transactions[cost].sum().round(decimals=2)
            daily_transactions_text = generate_daily_transactions_text(daily_transactions)
            date_range_text = f"{format_date(start_date)} - {format_date(end_date)}"

            if excel == "Y":
                try:
                    with pd.ExcelWriter(excel_filename) as writer:
                        filtered_transactions.to_excel(writer, sheet_name='Days with Transactions', index=False)  # Write df1 to Sheet1
                        daily_transactions.to_excel(writer, sheet_name='All Days', index=False)  # Write df2 to Sheet2
                except Exception as e:
                    print("Failed to create Excel file:", e)
                else:
                    print("Excel file created successfully.")
                    

            return render_template('index.html', date_range_text=date_range_text, daily_transactions_text=daily_transactions_text, total_cost=total_cost, grouped_categories_text=grouped_categories_text, categories_text=categories_text, transactions_text=transactions_text, start_date=start_date, end_date=end_date, transaction_path=transaction_path, excel=excel)

        except FileNotFoundError as e:
            error_message = f"Error: {str(e)}"
            return render_template('index.html', error=error_message)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"    
            return render_template('index.html', error=error_message)
    elif request.method == 'GET':
        return render_template('index.html')

def format_date(date_value):
    return pd.to_datetime(date_value).strftime('%B %d, %Y')

def merge_transactions(transaction_path, input_files):
    transaction_dfs = [pd.read_csv(os.path.join(transaction_path, file)) for file in input_files]
    merged_transactions = pd.concat(transaction_dfs).drop_duplicates(subset=[retailer, cost, date])
    return merged_transactions

def filter_transaction_by_date(start_date, end_date, merged_transactions):    
    filtered_transactions = merged_transactions[(merged_transactions.iloc[:, 0] >= start_date) & 
                            (merged_transactions.iloc[:, 0] <= end_date)].sort_values(by=date, ascending=False)    
    return filtered_transactions

def summarize_categories(filtered_transactions):
    for keyword in grocery_keywords:
        contains_keyword = filtered_transactions[retailer].str.contains(keyword, case=False, na=False)
        not_fuel = ~filtered_transactions[retailer].str.contains('FUEL', case=False, na=False)
        if contains_keyword.any() and not_fuel.any():
            filtered_transactions.loc[contains_keyword & not_fuel, category] = 'Grocery'

    categories_summary = filtered_transactions.groupby(category)[cost].sum().round(2).reset_index()
    return categories_summary

def daily_totals(df, start, end):
    global date, cost
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    date_range_df = pd.DataFrame({date: pd.date_range(start=start, end=end, freq='D')})
    date_range_df[date] = date_range_df[date].dt.date
    df[cost] = df[cost].fillna(0)

    df['Count'] = 0
    date_range_df[cost] = float('nan')
    date_range_df['Count'] = 0

    for index, row in df.iterrows():
        for i, r in date_range_df.iterrows():
            if str(row[date]) == str(r[date]):
                date_range_df.at[i, 'Count'] += 1
                if pd.isna(date_range_df.at[i, cost]):
                    date_range_df.at[i, cost] = row[cost]
                else:
                    date_range_df.at[i, cost] += row[cost]
                    date_range_df.at[i, cost] = date_range_df.at[i, cost].round(decimals=2)
                break
    date_range_df[cost] = date_range_df[cost].fillna(0)   

    return date_range_df

def generate_daily_transactions_text(daily_transactions):
    result_text = "Date > Total Spent > Transaction Count\n"
    for i, row in daily_transactions.iterrows():
        result_text += f"{str(row['Transaction Date']).ljust(30)} {str(row['Debit']).ljust(20)} {str(row['Count'])}\n"
    return result_text
    
def generate_category_group_text(filtered_transactions, categories_summary):
    result_text = ""
    for i, category_row in categories_summary.iterrows():
        category_df = filtered_transactions[filtered_transactions[category] == categories_summary.iloc[i, 0]]
        result_text += f"\n{categories_summary.iloc[i, 0]}:\n"
        for index, transaction_row in category_df.iterrows():
            result_text += f"{transaction_row[retailer].ljust(30)} {transaction_row[cost]}\n"
    return result_text

def generate_category_text(categories_summary):
    result_text = ""
    for i, category_row in categories_summary.iterrows():
        result_text += f"{category_row[category].ljust(30)} {category_row[cost]}\n"
    return result_text

def generate_transaction_text(filtered_transactions):
    result_text = "Date > Category > Retailer > Cost\n"
    for index, row in filtered_transactions.iterrows():
        try:
            result_text += f"{row[date].ljust(20)} {row[category].ljust(20)} {row[retailer].ljust(30)} {row[cost]}\n"
        except:
            result_text += f"{row[category].ljust(30)} {row[cost]}\n"
    return result_text

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
