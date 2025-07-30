from csvcdc import CSVCDC, OutputFormatter
import json
import time
import os

def create_advanced_sample_data():
    """Create more complex sample data"""
    
    # Products with composite primary key (store_id + product_id)
    products_old = """store_id,product_id,name,price,stock,last_updated
1,101,Laptop,999.99,5,2024-01-01
1,102,Mouse,25.99,50,2024-01-01
2,101,Laptop,1099.99,3,2024-01-01
2,103,Keyboard,75.00,20,2024-01-01
3,101,Laptop,949.99,8,2024-01-01
"""

    products_new = """store_id,product_id,name,price,stock,last_updated
1,101,Laptop,899.99,3,2024-01-15
1,102,Mouse,25.99,45,2024-01-15
1,104,Monitor,299.99,10,2024-01-15
2,101,Laptop,999.99,5,2024-01-15
2,103,Keyboard,79.99,18,2024-01-15
3,105,Tablet,199.99,15,2024-01-15
"""
    
    os.makedirs('sample_data', exist_ok=True)
    
    with open('sample_data/products_old.csv', 'w') as f:
        f.write(products_old)
        
    with open('sample_data/products_new.csv', 'w') as f:
        f.write(products_new)
    
    print("✅ Advanced sample data created")

def composite_primary_key_example():
    """Example using composite primary key"""
    print("\n" + "="*60)
    print("COMPOSITE PRIMARY KEY EXAMPLE")
    print("="*60)
    
    # Use store_id + product_id as composite primary key
    cdc = CSVCDC(primary_key=[0, 1])
    
    result = cdc.compare('sample_data/products_old.csv', 'sample_data/products_new.csv')
    
    print("Using composite primary key (store_id + product_id):")
    output = OutputFormatter.format_diff(result)
    print(output)

def auto_primary_key_example():
    """Example using auto primary key detection"""
    print("\n" + "="*60)
    print("AUTO PRIMARY KEY DETECTION EXAMPLE")
    print("="*60)
    
    # Let the tool automatically detect the best primary key
    cdc = CSVCDC(autopk=1, progressbar=1)
    
    print("Auto-detecting primary key...")
    result = cdc.compare('sample_data/products_old.csv', 'sample_data/products_new.csv')
    
    output = OutputFormatter.format_diff(result)
    print(output)

def performance_monitoring_example():
    """Example with performance monitoring"""
    print("\n" + "="*60)
    print("PERFORMANCE MONITORING EXAMPLE")
    print("="*60)
    
    start_time = time.time()
    
    cdc = CSVCDC(
        primary_key=[0, 1],
        progressbar=1  # Show progress bars
    )
    
    result = cdc.compare('sample_data/products_old.csv', 'sample_data/products_new.csv')
    
    end_time = time.time()
    
    print(f"\n⏱️  Execution time: {end_time - start_time:.3f} seconds")
    print(f"📊 Results: {len(result.additions)} additions, {len(result.modifications)} modifications, {len(result.deletions)} deletions")

def custom_processing_example():
    """Example of custom processing of results"""
    print("\n" + "="*60)
    print("CUSTOM PROCESSING EXAMPLE")
    print("="*60)
    
    cdc = CSVCDC(primary_key=[0, 1])
    result = cdc.compare('sample_data/products_old.csv', 'sample_data/products_new.csv')
    
    # Custom analysis
    price_changes = []
    stock_changes = []
    
    for mod in result.modifications:
        orig_parts = mod['Original'].split(',')
        curr_parts = mod['Current'].split(',')
        
        if len(orig_parts) >= 5 and len(curr_parts) >= 5:
            try:
                # Extract details
                store_id = orig_parts[0]
                product_id = orig_parts[1]
                product_name = orig_parts[2]
                
                old_price = float(orig_parts[3])
                new_price = float(curr_parts[3])
                
                old_stock = int(orig_parts[4])
                new_stock = int(curr_parts[4])
                
                # Track price changes
                if old_price != new_price:
                    price_changes.append({
                        'store_id': store_id,
                        'product_id': product_id,
                        'name': product_name,
                        'old_price': old_price,
                        'new_price': new_price,
                        'price_change': new_price - old_price,
                        'percent_change': ((new_price - old_price) / old_price) * 100
                    })
                
                # Track stock changes
                if old_stock != new_stock:
                    stock_changes.append({
                        'store_id': store_id,
                        'product_id': product_id,
                        'name': product_name,
                        'old_stock': old_stock,
                        'new_stock': new_stock,
                        'stock_change': new_stock - old_stock
                    })
                    
            except (ValueError, IndexError):
                continue
    
    print("💰 Price Changes:")
    for change in price_changes:
        print(f"   {change['name']} (Store {change['store_id']}): ${change['old_price']:.2f} → ${change['new_price']:.2f} ({change['percent_change']:+.1f}%)")
    
    print(f"\n📦 Stock Changes:")
    for change in stock_changes:
        print(f"   {change['name']} (Store {change['store_id']}): {change['old_stock']} → {change['new_stock']} ({change['stock_change']:+d})")
    
    # Save detailed analysis
    analysis = {
        'summary': {
            'total_additions': len(result.additions),
            'total_modifications': len(result.modifications),
            'total_deletions': len(result.deletions),
            'price_changes': len(price_changes),
            'stock_changes': len(stock_changes)
        },
        'price_changes': price_changes,
        'stock_changes': stock_changes
    }
    
    with open('sample_data/detailed_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n💾 Detailed analysis saved to sample_data/detailed_analysis.json")

def different_formats_example():
    """Example showing different output formats"""
    print("\n" + "="*60)
    print("DIFFERENT OUTPUT FORMATS EXAMPLE")
    print("="*60)
    
    cdc = CSVCDC(primary_key=[0, 1])
    result = cdc.compare('sample_data/products_old.csv', 'sample_data/products_new.csv')
    
    # Word diff format
    print("🔤 Word Diff Format:")
    word_diff = OutputFormatter.format_word_diff(result)
    print(word_diff)
    
    print(f"\n📋 Rowmark Format:")
    rowmark = OutputFormatter.format_rowmark(result)
    print(rowmark)

def selective_column_comparison():
    """Example of comparing only specific columns"""
    print("\n" + "="*60)
    print("SELECTIVE COLUMN COMPARISON EXAMPLE")
    print("="*60)
    
    # Compare only price and stock columns (ignore last_updated)
    print("Comparing only critical business data (ignoring timestamps):")
    
    cdc = CSVCDC(
        primary_key=[0, 1],
        columns=[0, 1, 2, 3, 4]  # Exclude last_updated column (index 5)
    )
    
    result = cdc.compare('sample_data/products_old.csv', 'sample_data/products_new.csv')
    output = OutputFormatter.format_diff(result)
    print(output)
    
    print(f"\n" + "-"*40)
    print("Now including timestamp column:")
    
    cdc_all = CSVCDC(primary_key=[0, 1])  # Include all columns
    result_all = cdc_all.compare('sample_data/products_old.csv', 'sample_data/products_new.csv')
    output_all = OutputFormatter.format_diff(result_all)
    print(output_all)

if __name__ == '__main__':
    print("🚀 CSV CDC Advanced Examples")
    
    # Create sample data
    create_advanced_sample_data()
    
    # Run advanced examples
    composite_primary_key_example()
    auto_primary_key_example()
    performance_monitoring_example()
    custom_processing_example()
    different_formats_example()
    selective_column_comparison()
    
    print(f"\n✨ Advanced examples completed! Check the sample_data/ directory for generated files.")