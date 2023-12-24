# Budget

**CreditCardAnalyzer**

## Overview

CreditCardAnalyzer is a Python tool designed to analyze credit card transactions from CSV files, categorize spending, and provide insights into the user's financial habits. The primary purpose is to help users track and manage their expenses, providing a breakdown of spending across various categories.

## Features

- **Graphical User Interface (GUI):** The `budget.py` file contains a Tkinter-based GUI allowing users to specify the location of their credit card CSV files and the names of various output files.

- **CSV File Operations:**
  - Combine transactions from multiple CSV files into a single CSV file.
  - Generate a CSV file containing all transactions filtered for the past month.
  - Create a CSV file displaying money spent in each predefined category (dining, gas, merchandise, grocery, other).

- **Category Categorization:**
  - Automatically categorize transactions into predefined categories based on the transaction descriptions.

- **Total Spending:**
  - Display the total amount spent in each category.

## Installation

Clone the repository:

   ```bash
   git clone https://github.com/your-username/credit-card-analyzer.git
   ```

## Usage

1. Run the `budget.py` file:

   ```bash
   python3 budget.py
   ```

2. Use the GUI to specify the location of your credit card CSV files.

3. Specify the desired output file names (combined transactions, filtered for the past month, categorized spending).

4. Review the generated CSV files and analyze your spending patterns.

## Future Enhancements

- **Budget Tracking:** Implement a budget tracking feature to compare actual spending against a predefined budget.

- **Visualizations:** Include graphical representations (charts, graphs) to enhance data visualization.

- **Interface:** Make the interface more user friendly and persistent, perhaps through displaying it on a web browser.
