"""
Generate test CSV data for development and testing
"""

import csv
import random
import argparse
import os
from datetime import datetime, timedelta

def generate_products_data(filename, num_products=1000):
    """Generate product catalog data"""
    
    categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Toys', 'Automotive']
    suppliers = [f'SUP{i:03d}' for i in range(1, 21)]
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['product_id', 'name', 'price', 'category', 'supplier_id', 'stock', 'last_updated'])
        
        for i in range(1, num_products + 1):
            product_id = f'P{i:04d}'
            name = f'Product {i}'
            price = round(random.uniform(5.99, 999.99), 2)
            category = random.choice(categories)
            supplier = random.choice(suppliers)
            stock = random.randint(0, 100)
            last_updated = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
            
            writer.writerow([product_id, name, price, category, supplier, stock, last_updated])
    
    print(f"Generated {num_products} products in {filename}")

def generate_customers_data(filename, num_customers=500):
    """Generate customer data"""
    
    first_names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry']
    last_names = ['Smith', 'Johnson', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas']
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'company.com', 'example.com']
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['customer_id', 'first_name', 'last_name', 'email', 'phone', 'city', 'registration_date'])
        
        for i in range(1, num_customers + 1):
            customer_id = f'C{i:05d}'
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f'{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}'
            phone = f'{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}'
            city = random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia'])
            registration_date = (datetime.now() - timedelta(days=random.randint(30, 1095))).strftime('%Y-%m-%d')
            
            writer.writerow([customer_id, first_name, last_name, email, phone, city, registration_date])
    
    print(f"Generated {num_customers} customers in {filename}")

def generate_orders_data(filename, num_orders=2000):
    """Generate order data"""
    
    statuses = ['pending', 'shipped', 'delivered', 'cancelled']
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['order_id', 'customer_id', 'product_id', 'quantity', 'order_date', 'status', 'total_amount'])
        
        for i in range(1, num_orders + 1):
            order_id = f'O{i:06d}'
            customer_id = f'C{random.randint(1, 500):05d}'
            product_id = f'P{random.randint(1, 1000):04d}'
            quantity = random.randint(1, 5)
            order_date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
            status = random.choice(statuses)
            total_amount = round(random.uniform(10.00, 500.00), 2)
            
            writer.writerow([order_id, customer_id, product_id, quantity, order_date, status, total_amount])
    
    print(f"Generated {num_orders} orders in {filename}")

def modify_data(input_file, output_file, change_rate=0.1, add_rate=0.05, delete_rate=0.05):
    """Create modified version of data"""
    
    with open(input_file, 'r') as f_in:
        reader = csv.reader(f_in)
        headers = next(reader)
        rows = list(reader)
    
    total_rows = len(rows)
    
    # Determine which rows to modify
    random.seed(42)  # For reproducible results
    rows_to_change = set(random.sample(range(total_rows), int(total_rows * change_rate)))
    rows_to_delete = set(random.sample(range(total_rows), int(total_rows * delete_rate)))
    
    with open(output_file, 'w', newline='') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(headers)
        
        # Write existing rows (modified or deleted)
        for i, row in enumerate(rows):
            if i in rows_to_delete:
                continue
            
            if i in rows_to_change:
                # Modify some fields
                if 'price' in headers:
                    price_idx = headers.index('price')
                    current_price = float(row[price_idx])
                    new_price = round(current_price * random.uniform(0.8, 1.2), 2)
                    row[price_idx] = str(new_price)
                
                if 'stock' in headers:
                    stock_idx = headers.index('stock')
                    row[stock_idx] = str(random.randint(0, 100))
                
                if 'status' in headers:
                    status_idx = headers.index('status')
                    statuses = ['pending', 'shipped', 'delivered', 'cancelled']
                    row[status_idx] = random.choice(statuses)
            
            writer.writerow(row)
        
        # Add new rows
        new_rows_count = int(total_rows * add_rate)
        
        if 'product_id' in headers:
            # Generate new products
            for i in range(new_rows_count):
                new_id = total_rows + i + 1
                new_row = [
                    f'P{new_id:04d}',
                    f'New Product {new_id}',
                    round(random.uniform(5.99, 999.99), 2),
                    'Electronics',
                    'SUP001',
                    random.randint(0, 100),
                    datetime.now().strftime('%Y-%m-%d')
                ]
                writer.writerow(new_row)
        
        elif 'customer_id' in headers:
            # Generate new customers
            first_names = ['John', 'Jane', 'Bob', 'Alice']
            last_names = ['Smith', 'Johnson', 'Brown', 'Davis']
            
            for i in range(new_rows_count):
                new_id = total_rows + i + 1
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                new_row = [
                    f'C{new_id:05d}',
                    first_name,
                    last_name,
                    f'{first_name.lower()}.{last_name.lower()}@example.com',
                    f'{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    'New York',
                    datetime.now().strftime('%Y-%m-%d')
                ]
                writer.writerow(new_row)
        
        elif 'order_id' in headers:
            # Generate new orders
            for i in range(new_rows_count):
                new_id = total_rows + i + 1
                new_row = [
                    f'O{new_id:06d}',
                    f'C{random.randint(1, 500):05d}',
                    f'P{random.randint(1, 1000):04d}',
                    random.randint(1, 5),
                    datetime.now().strftime('%Y-%m-%d'),
                    'pending',
                    round(random.uniform(10.00, 500.00), 2)
                ]
                writer.writerow(new_row)
    
    print(f"Modified data saved to {output_file}")
    print(f"  Changed: {len(rows_to_change)} rows")
    print(f"  Deleted: {len(rows_to_delete)} rows") 
    print(f"  Added: {new_rows_count} rows")

def main():
    parser = argparse.ArgumentParser(description='Generate test CSV data')
    parser.add_argument('--output-dir', '-o', default='test_data', help='Output directory')
    parser.add_argument('--products', type=int, default=1000, help='Number of products')
    parser.add_argument('--customers', type=int, default=500, help='Number of customers')
    parser.add_argument('--orders', type=int, default=2000, help='Number of orders')
    parser.add_argument('--generate-deltas', action='store_true', help='Generate delta files')
    parser.add_argument('--change-rate', type=float, default=0.1, help='Rate of changes for delta files')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"🏭 Generating test data in {args.output_dir}/")
    
    # Generate base data
    products_file = os.path.join(args.output_dir, 'products.csv')
    customers_file = os.path.join(args.output_dir, 'customers.csv')
    orders_file = os.path.join(args.output_dir, 'orders.csv')
    
    generate_products_data(products_file, args.products)
    generate_customers_data(customers_file, args.customers)
    generate_orders_data(orders_file, args.orders)
    
    if args.generate_deltas:
        print(f"\n🔄 Generating delta files with {args.change_rate*100}% change rate")
        
        # Generate delta files
        products_delta = os.path.join(args.output_dir, 'products_delta.csv')
        customers_delta = os.path.join(args.output_dir, 'customers_delta.csv')
        orders_delta = os.path.join(args.output_dir, 'orders_delta.csv')
        
        modify_data(products_file, products_delta, args.change_rate)
        modify_data(customers_file, customers_delta, args.change_rate)
        modify_data(orders_file, orders_delta, args.change_rate)
    
    print(f"\n✅ Data generation complete!")
    print(f"Files created in: {args.output_dir}/")

if __name__ == '__main__':
    main()