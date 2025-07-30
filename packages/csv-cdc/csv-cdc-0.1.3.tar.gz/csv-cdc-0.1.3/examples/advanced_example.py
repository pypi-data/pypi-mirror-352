from csvcdc import CSVCDC, OutputFormatter
import json
import time
import os
import random
import string

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

def create_large_sample_data(num_rows=100000):
    """Create large sample data for testing large file processing"""
    print(f"\n📊 Creating large sample data with {num_rows:,} rows...")
    
    os.makedirs('sample_data', exist_ok=True)
    
    # Generate base file
    with open('sample_data/large_products_old.csv', 'w') as f:
        f.write("store_id,product_id,name,price,stock,category,last_updated\n")
        
        for i in range(num_rows):
            store_id = random.randint(1, 100)
            product_id = random.randint(1000, 9999)
            name = f"Product_{random.randint(1, 1000)}"
            price = round(random.uniform(10.0, 1000.0), 2)
            stock = random.randint(0, 100)
            category = random.choice(['Electronics', 'Clothing', 'Home', 'Sports', 'Books'])
            date = f"2024-01-{random.randint(1, 28):02d}"
            
            f.write(f"{store_id},{product_id},{name},{price},{stock},{category},{date}\n")
    
    # Generate delta file with some changes
    with open('sample_data/large_products_new.csv', 'w') as f:
        f.write("store_id,product_id,name,price,stock,category,last_updated\n")
        
        # Read old file and modify some records
        with open('sample_data/large_products_old.csv', 'r') as old_f:
            lines = old_f.readlines()[1:]  # Skip header
            
            for i, line in enumerate(lines):
                parts = line.strip().split(',')
                
                # Modify some records (about 10%)
                if random.random() < 0.1:
                    if len(parts) >= 7:
                        # Change price
                        parts[3] = str(round(float(parts[3]) * random.uniform(0.8, 1.2), 2))
                        # Change stock
                        parts[4] = str(max(0, int(parts[4]) + random.randint(-10, 10)))
                        # Update date
                        parts[6] = f"2024-02-{random.randint(1, 28):02d}"
                
                # Skip some records (deletions - about 5%)
                if random.random() > 0.05:
                    f.write(','.join(parts) + '\n')
                
                # Add some new records (about 3%)
                if random.random() < 0.03:
                    store_id = random.randint(1, 100)
                    product_id = random.randint(10000, 19999)  # Different range for new products
                    name = f"NewProduct_{random.randint(1, 1000)}"
                    price = round(random.uniform(10.0, 1000.0), 2)
                    stock = random.randint(0, 100)
                    category = random.choice(['Electronics', 'Clothing', 'Home', 'Sports', 'Books'])
                    date = f"2024-02-{random.randint(1, 28):02d}"
                    
                    f.write(f"{store_id},{product_id},{name},{price},{stock},{category},{date}\n")
    
    print("✅ Large sample data created")

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

def large_file_processing_example():
    """Example demonstrating large file processing with chunked approach"""
    print("\n" + "="*60)
    print("LARGE FILE PROCESSING EXAMPLE")
    print("="*60)
    
    # Create large sample data first
    create_large_sample_data(50000)  # 50K rows for demo
    
    print("\n🔄 Processing large files with regular mode...")
    start_time = time.time()
    
    # Regular processing
    cdc_regular = CSVCDC(
        primary_key=[0, 1],
        progressbar=1,
        largefiles=0  # Regular mode
    )
    
    result_regular = cdc_regular.compare('sample_data/large_products_old.csv', 'sample_data/large_products_new.csv')
    regular_time = time.time() - start_time
    
    print(f"⏱️  Regular mode time: {regular_time:.3f} seconds")
    print(f"📊 Results: {len(result_regular.additions)} additions, {len(result_regular.modifications)} modifications, {len(result_regular.deletions)} deletions")
    
    print("\n🚀 Processing same files with large file optimization...")
    start_time = time.time()
    
    # Large file processing with chunking
    cdc_large = CSVCDC(
        primary_key=[0, 1],
        progressbar=1,
        largefiles=1,  # Enable large file mode
        chunk_size=500000  # Custom chunk size
    )
    
    result_large = cdc_large.compare('sample_data/large_products_old.csv', 'sample_data/large_products_new.csv')
    large_time = time.time() - start_time
    
    print(f"⏱️  Large file mode time: {large_time:.3f} seconds")
    print(f"📊 Results: {len(result_large.additions)} additions, {len(result_large.modifications)} modifications, {len(result_large.deletions)} deletions")
    
    # Compare results
    print(f"\n📈 Performance comparison:")
    if regular_time > 0:
        speedup = regular_time / large_time if large_time > 0 else float('inf')
        print(f"   Speed difference: {speedup:.2f}x")
    
    # Verify results are identical
    results_match = (
        len(result_regular.additions) == len(result_large.additions) and
        len(result_regular.modifications) == len(result_large.modifications) and
        len(result_regular.deletions) == len(result_large.deletions)
    )
    
    print(f"   Results identical: {'✅ Yes' if results_match else '❌ No'}")

def memory_efficient_processing_example():
    """Example showing memory-efficient processing for very large files"""
    print("\n" + "="*60)
    print("MEMORY-EFFICIENT PROCESSING EXAMPLE")
    print("="*60)
    
    print("This example shows how to handle very large files that might not fit in memory...")
    
    # Simulate processing a very large file
    cdc = CSVCDC(
        primary_key=[0, 1],
        progressbar=1,
        largefiles=1,
        chunk_size=10000  # Smaller chunks for memory efficiency
    )
    
    # Use the large files we created
    if os.path.exists('sample_data/large_products_old.csv'):
        print(f"\n💾 Processing with small chunks (10,000 rows per chunk)...")
        start_time = time.time()
        
        result = cdc.compare('sample_data/large_products_old.csv', 'sample_data/large_products_new.csv')
        
        elapsed = time.time() - start_time
        print(f"⏱️  Processing time: {elapsed:.3f} seconds")
        print(f"📊 Results: {len(result.additions)} additions, {len(result.modifications)} modifications, {len(result.deletions)} deletions")
        
        # Show a sample of results
        if result.modifications:
            print(f"\n📝 Sample modifications (first 3):")
            for i, mod in enumerate(result.modifications[:3]):
                print(f"   {i+1}. Original: {mod['Original'][:60]}...")
                print(f"      Current:  {mod['Current'][:60]}...")
    else:
        print("⚠️  Large sample files not found. Run large_file_processing_example() first.")

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

def chunked_processing_comparison():
    """Compare different chunk sizes for large file processing"""
    print("\n" + "="*60)
    print("CHUNKED PROCESSING COMPARISON")
    print("="*60)
    
    # Create moderate-sized sample data
    create_large_sample_data(20000)  # 20K rows
    
    chunk_sizes = [5000, 10000, 50000, 500000]
    results = {}
    
    for chunk_size in chunk_sizes:
        print(f"\n🔄 Testing chunk size: {chunk_size:,}")
        
        start_time = time.time()
        
        cdc = CSVCDC(
            primary_key=[0, 1],
            progressbar=0,  # Disable progress bar for cleaner output
            largefiles=1,
            chunk_size=chunk_size
        )
        
        result = cdc.compare('sample_data/large_products_old.csv', 'sample_data/large_products_new.csv')
        
        elapsed = time.time() - start_time
        results[chunk_size] = {
            'time': elapsed,
            'additions': len(result.additions),
            'modifications': len(result.modifications),
            'deletions': len(result.deletions)
        }
        
        print(f"   ⏱️  Time: {elapsed:.3f}s | Results: {len(result.additions)}A, {len(result.modifications)}M, {len(result.deletions)}D")
    
    # Find optimal chunk size
    optimal_chunk = min(results.keys(), key=lambda k: results[k]['time'])
    
    print(f"\n🏆 Optimal chunk size for this dataset: {optimal_chunk:,} rows")
    print(f"   Best time: {results[optimal_chunk]['time']:.3f} seconds")
    
    # Save benchmark results
    with open('sample_data/chunk_benchmark.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Benchmark results saved to sample_data/chunk_benchmark.json")

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
    
    # New large file examples
    large_file_processing_example()
    memory_efficient_processing_example()
    chunked_processing_comparison()
    
    print(f"\n✨ Advanced examples completed! Check the sample_data/ directory for generated files.")