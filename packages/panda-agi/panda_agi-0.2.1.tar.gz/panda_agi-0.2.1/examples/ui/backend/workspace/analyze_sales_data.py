import pandas as pd
import numpy as np
from datetime import datetime
import json

# Read the CSV file
print("Loading sales data...")
df = pd.read_csv('./Supermarket Sales.csv', delimiter=';')

print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Basic data info
print("\n=== BASIC DATA OVERVIEW ===")
print(f"Total records: {len(df)}")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"Branches: {df['Branch'].unique()}")
print(f"Cities: {df['City'].unique()}")
print(f"Product lines: {df['Product line'].unique()}")

# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
df['Month'] = df['Date'].dt.strftime('%Y-%m')
df['Day_of_Week'] = df['Date'].dt.day_name()

# Key Performance Indicators
print("\n=== KEY PERFORMANCE INDICATORS ===")
total_revenue = df['Total'].sum()
total_transactions = len(df)
avg_transaction_value = df['Total'].mean()
total_quantity_sold = df['Quantity'].sum()
avg_rating = df['Rating'].mean()

print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Total Transactions: {total_transactions:,}")
print(f"Average Transaction Value: ${avg_transaction_value:.2f}")
print(f"Total Items Sold: {total_quantity_sold:,}")
print(f"Average Customer Rating: {avg_rating:.1f}/10")

# Sales by Branch
print("\n=== SALES BY BRANCH ===")
branch_sales = df.groupby(['Branch', 'City']).agg({
    'Total': ['sum', 'count', 'mean'],
    'Quantity': 'sum',
    'Rating': 'mean'
}).round(2)
print(branch_sales)

# Sales by Product Line
print("\n=== SALES BY PRODUCT LINE ===")
product_sales = df.groupby('Product line').agg({
    'Total': ['sum', 'count', 'mean'],
    'Quantity': 'sum',
    'Rating': 'mean'
}).round(2)
print(product_sales)

# Sales by Customer Type
print("\n=== SALES BY CUSTOMER TYPE ===")
customer_sales = df.groupby('Customer type').agg({
    'Total': ['sum', 'count', 'mean'],
    'Rating': 'mean'
}).round(2)
print(customer_sales)

# Sales by Gender
print("\n=== SALES BY GENDER ===")
gender_sales = df.groupby('Gender').agg({
    'Total': ['sum', 'count', 'mean'],
    'Rating': 'mean'
}).round(2)
print(gender_sales)

# Payment Method Analysis
print("\n=== PAYMENT METHOD ANALYSIS ===")
payment_analysis = df.groupby('Payment').agg({
    'Total': ['sum', 'count', 'mean']
}).round(2)
print(payment_analysis)

# Monthly Sales Trend
print("\n=== MONTHLY SALES TREND ===")
monthly_sales = df.groupby('Month').agg({
    'Total': 'sum',
    'Quantity': 'sum'
}).round(2)
print(monthly_sales)

# Day of Week Analysis
print("\n=== DAY OF WEEK ANALYSIS ===")
dow_sales = df.groupby('Day_of_Week').agg({
    'Total': ['sum', 'count', 'mean']
}).round(2)
print(dow_sales)

# Top performing products by revenue
print("\n=== TOP PRODUCTS BY REVENUE ===")
top_products = df.groupby('Product line')['Total'].sum().sort_values(ascending=False)
print(top_products)

# Prepare data for dashboard JSON
dashboard_data = {
    'kpis': {
        'total_revenue': float(total_revenue),
        'total_transactions': int(total_transactions),
        'avg_transaction_value': float(avg_transaction_value),
        'total_quantity_sold': int(total_quantity_sold),
        'avg_rating': float(avg_rating)
    },
    'branch_data': df.groupby(['Branch', 'City']).agg({
        'Total': 'sum',
        'Quantity': 'sum'
    }).reset_index().to_dict('records'),
    'product_data': df.groupby('Product line').agg({
        'Total': 'sum',
        'Quantity': 'sum',
        'Rating': 'mean'
    }).reset_index().to_dict('records'),
    'customer_type_data': df.groupby('Customer type').agg({
        'Total': 'sum',
        'Quantity': 'sum'
    }).reset_index().to_dict('records'),
    'gender_data': df.groupby('Gender').agg({
        'Total': 'sum',
        'Quantity': 'sum'
    }).reset_index().to_dict('records'),
    'payment_data': df.groupby('Payment').agg({
        'Total': 'sum',
        'Quantity': 'sum'
    }).reset_index().to_dict('records'),
    'monthly_data': df.groupby('Month').agg({
        'Total': 'sum',
        'Quantity': 'sum'
    }).reset_index().to_dict('records'),
    'daily_data': df.groupby('Day_of_Week').agg({
        'Total': 'sum',
        'Quantity': 'sum'
    }).reset_index().to_dict('records')
}

# Save dashboard data as JSON
with open('dashboard_data.json', 'w') as f:
    json.dump(dashboard_data, f, indent=2)

print("\n=== DASHBOARD DATA SAVED ===")
print("Dashboard data saved to dashboard_data.json")

print("\n=== KEY INSIGHTS ===")
print("1. Revenue Distribution:")
for branch, city in zip(df['Branch'].unique(), df['City'].unique()):
    branch_revenue = df[df['Branch'] == branch]['Total'].sum()
    percentage = (branch_revenue / total_revenue) * 100
    print(f"   - Branch {branch} ({city}): ${branch_revenue:,.2f} ({percentage:.1f}%)")

print("\n2. Product Performance:")
for product in top_products.head(3).index:
    revenue = top_products[product]
    percentage = (revenue / total_revenue) * 100
    print(f"   - {product}: ${revenue:,.2f} ({percentage:.1f}%)")

print(f"\n3. Customer Insights:")
member_revenue = df[df['Customer type'] == 'Member']['Total'].sum()
normal_revenue = df[df['Customer type'] == 'Normal']['Total'].sum()
print(f"   - Member customers: ${member_revenue:,.2f} ({(member_revenue/total_revenue)*100:.1f}%)")
print(f"   - Normal customers: ${normal_revenue:,.2f} ({(normal_revenue/total_revenue)*100:.1f}%)")

print(f"\n4. Payment Preferences:")
for payment in df['Payment'].value_counts().index:
    count = df[df['Payment'] == payment].shape[0]
    percentage = (count / total_transactions) * 100
    print(f"   - {payment}: {count} transactions ({percentage:.1f}%)")