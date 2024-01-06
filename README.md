# Expenses

**Expenses**

## Overview

Expenses is a Python tool designed to analyze credit card transactions from CSV files, categorize spending, and provide insights into the user's financial habits. The primary purpose is to help users track and manage their expenses, providing a breakdown of spending across various categories.

## Features

- **Graphical User Interface (GUI):** The `budget.py` file contains a browser-based GUI allowing users to specify the location of their credit card CSV files and the number of past days to include in its analysis.

- **CSV File Operations:**
  - Combine transactions from multiple CSV files into a single CSV file.
  - Generate a CSV file containing all transactions filtered for the past number of days.
  - Create a CSV file displaying money spent in each predefined category (dining, gas, merchandise, grocery, etc.).

- **Total Spending:**
  - Display the total amount spent in each category.
  - Display the overall amount spent during the given period.

## Installation

Open the Terminal application by entering Command + Space Bar and typing "Terminal"

Ensure dependencies are installed:
  - Git
  - Python3

Paste the following into the terminal:

   ```bash
   git clone https://github.com/loganflecke/expenses.git
   ```

## Usage

1. Run the `Run` file:

   ```bash
   chmod 555 Run
   ./Run
   ```

2. Place your CSV file(s) in a directory called Transactions (or a name of your choice) within the Expenses directory that was just created.

4. Use the webpage to specify the location of your credit card CSV files (ex: ./Transactions).

6. Click Continue.

## Future Enhancements

- **Budget Tracking:** Implement a budget tracking feature to compare actual spending against a predefined budget.

- **Visualizations:** Include graphical representations (charts, graphs) to enhance data visualization.

- **Date Range:** Specify the start and end dates of the transactions to include.
