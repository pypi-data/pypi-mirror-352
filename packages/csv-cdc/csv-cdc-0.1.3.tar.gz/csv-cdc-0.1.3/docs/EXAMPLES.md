# CSV CDC Examples

This document provides comprehensive examples of using the CSV CDC tool for various scenarios.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Advanced Configuration](#advanced-configuration)
3. [Large File Processing](#large-file-processing)
4. [Real-World Scenarios](#real-world-scenarios)
5. [Integration Examples](#integration-examples)
6. [Performance Examples](#performance-examples)
7. [Troubleshooting Examples](#troubleshooting-examples)

## Basic Examples

### Example 1: Simple Product Catalog Comparison

**Scenario:** You have two versions of a product catalog and want to see what changed.

**Data Setup:**
```bash
# Create base catalog
cat > products_old.csv << EOF
sku,name,price,category,stock
P001,Wireless Mouse,29.99,Electronics,45
P002,USB Keyboard,49.99,Electronics,23
P003,Office Chair,199.99,Furniture,8
P004,Desk Lamp,75.00,Furniture,15
EOF

# Create updated catalog
cat > products_new.csv << EOF
sku,name,price,category,stock
P001,Wireless Mouse,24.99,Electronics,50
P002,USB Keyboard,49.99,Electronics,18
P004,Desk Lamp,69.99,Furniture,12
P005,Monitor Stand,89.99,Electronics,25
EOF
```

**Command:**
```bash
python csvcdc.py products_old.csv products_new.csv --primary-key 0
```

**Output:**
```diff
# Additions (1)
+ P005,Monitor Stand,89.99,Electronics,25

# Modifications (3)
- P001,Wireless Mouse,29.99,Electronics,45
+ P001,Wireless Mouse,24.99,Electronics,50
- P002,USB Keyboard,49.99,Electronics,23
+ P002,USB Keyboard,49.99,Electronics,18
- P004,Desk Lamp,75.00,Furniture,15
+ P004,Desk Lamp,69.99,Furniture,12

# Deletions (1)
- P003,Office Chair,199.99,Furniture,8
```

### Example 2: Employee Database Changes

**Scenario:** Track changes in employee records between payroll periods.

**Data Setup:**
```bash
# Create employee base data
cat > employees_base.csv << EOF
emp_id,first_name,last_name,department,salary,hire_date
E001,John,Smith,Engineering,75000,2023-01-15
E002,Jane,Doe,Marketing,65000,2023-02-01
E003,Bob,Johnson,Sales,55000,2023-01-20
E004,Alice,Brown,Engineering,80000,2023-03-01
EOF

# Create updated employee data
cat > employees_new.csv << EOF
emp_id,first_name,last_name,department,salary,hire_date
E001,John,Smith,Engineering,78000,2023-01-15
E002,Jane,Doe,Marketing,67000,2023-02-01
E004,Alice,Brown,Engineering,82000,2023-03-01
E005,Charlie,Wilson,Sales,58000,2024-01-15
EOF
```

**Commands:**
```bash
# Basic comparison
python csvcdc.py employees_base.csv employees_new.csv --primary-key 0

# Focus only on salary changes (ignore hire_date)
python csvcdc.py employees_base.csv employees_new.csv \
  --primary-key 0 \
  --ignore-columns 5

# JSON output for further processing
python csvcdc.py employees_base.csv employees_new.csv \
  --primary-key 0 \
  --format json > employee_changes.json
```

## Advanced Configuration

### Example 3: Composite Primary Keys

**Scenario:** Inventory tracking across multiple stores where items are identified by store_id + product_id.

**Data Setup:**
```bash
cat > inventory_old.csv << EOF
store_id,product_id,product_name,quantity,last_restocked
S001,P101,Laptop,5,2024-01-01
S001,P102,Mouse,50,2024-01-02
S002,P101,Laptop,3,2024-01-01
S002,P103,Keyboard,20,2024-01-03
S003,P101,Laptop,8,2024-01-01
EOF

cat > inventory_new.csv << EOF
store_id,product_id,product_name,quantity,last_restocked
S001,P101,Laptop,2,2024-01-15
S001,P102,Mouse,45,2024-01-02
S001,P104,Monitor,10,2024-01-15
S002,P101,Laptop,5,2024-01-15
S002,P103,Keyboard,15,2024-01-03
S003,P105,Tablet,12,2024-01-15
EOF
```

**Command:**
```bash
# Use composite primary key (store_id + product_id)
python csvcdc.py inventory_old.csv inventory_new.csv \
  --primary-key 0,1 \
  --format diff
```

### Example 4: Auto Primary Key Detection

**Scenario:** Working with unfamiliar data structure where you want the tool to find the best primary key.

**Command:**
```bash
# Let the tool analyze and detect the best primary key
python csvcdc.py unknown_data_old.csv unknown_data_new.csv \
  --autopk 1 \
  --progressbar 1
```

**Output includes detection info:**
```
Auto-detecting primary key...
Testing single columns: 100%|██████████| 8/8
Testing column combinations: 100%|███| 3/3  
Auto-detected primary key: columns [0, 1] (score: 0.943)
```

### Example 5: Custom Separators

**Scenario:** Working with tab-separated or pipe-separated files.

**Tab-separated example:**
```bash
# Create tab-separated file
printf "id\tname\tvalue\n1\tItem1\t100\n2\tItem2\t200" > data_old.tsv
printf "id\tname\tvalue\n1\tItem1\t150\n3\tItem3\t300" > data_new.tsv

# Compare with tab separator
python csvcdc.py data_old.tsv data_new.tsv --separator '\t'
```

**Pipe-separated example:**
```bash
# Compare pipe-separated files
python csvcdc.py data_old.psv data_new.psv --separator '|'
```

## Large File Processing

### Example 6: Processing Very Large Files

**Scenario:** Processing multi-gigabyte CSV files that cause memory allocation errors.

**Memory Error Example:**
```bash
# This might fail with memory error for very large files
python csvcdc.py huge_base.csv huge_delta.csv --time -o json
# Error: Unable to allocate 203. GiB for an array...
```

**Solution - Use Large File Mode:**
```bash
# Enable large file processing with chunked mode
python csvcdc.py huge_base.csv huge_delta.csv \
  --largefiles 1 \
  --time \
  -o json

# With custom chunk size (default is 500,000 rows)
python csvcdc.py huge_base.csv huge_delta.csv \
  --largefiles 1 \
  --chunk-size 250000 \
  --time \
  -o json

# For extremely large files, use smaller chunks
python csvcdc.py huge_base.csv huge_delta.csv \
  --largefiles 1 \
  --chunk-size 100000 \
  --progressbar 1 \
  --time
```

### Example 7: Large File Processing with Auto Primary Key

**Scenario:** Large file with unknown structure that needs primary key detection.

**Command:**
```bash
# Auto-detect primary key on large files (uses sample from first chunk)
python csvcdc.py large_unknown_base.csv large_unknown_delta.csv \
  --largefiles 1 \
  --autopk 1 \
  --chunk-size 200000 \
  --progressbar 1
```

### Example 8: Memory-Efficient Processing Script

**Script: `large_file_processor.py`**
```python
#!/usr/bin/env python3
import os
import time
import psutil
from csvcdc import CSVCDC, OutputFormatter

def estimate_file_size(filepath):
    """Get file size in GB"""
    size_bytes = os.path.getsize(filepath)
    return size_bytes / (1024 ** 3)  # Convert to GB

def process_large_csv_files(base_file, delta_file, output_file=None):
    """Process large CSV files with automatic configuration"""
    
    base_size = estimate_file_size(base_file)
    delta_size = estimate_file_size(delta_file)
    
    print(f"📁 File sizes: Base={base_size:.2f}GB, Delta={delta_size:.2f}GB")
    
    # Determine if we need large file processing
    use_large_mode = (base_size > 1.0 or delta_size > 1.0)  # > 1GB
    
    if use_large_mode:
        print("🔧 Using large file processing mode")
        
        # Calculate appropriate chunk size based on available memory
        available_memory_gb = psutil.virtual_memory().available / (1024 ** 3)
        suggested_chunk_size = min(500000, int(available_memory_gb * 50000))  # Conservative estimate
        
        print(f"📊 Available RAM: {available_memory_gb:.1f}GB")
        print(f"🔢 Using chunk size: {suggested_chunk_size:,} rows")
        
        cdc = CSVCDC(
            largefiles=1,
            chunk_size=suggested_chunk_size,
            autopk=1,
            progressbar=1
        )
    else:
        print("🔧 Using standard processing mode")
        cdc = CSVCDC(autopk=1, progressbar=1)
    
    # Monitor performance
    start_time = time.time()
    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024 ** 2)  # MB
    
    print("🚀 Starting comparison...")
    result = cdc.compare(base_file, delta_file)
    
    # Performance metrics
    end_time = time.time()
    final_memory = process.memory_info().rss / (1024 ** 2)  # MB
    processing_time = end_time - start_time
    
    print(f"\n📊 Performance Metrics:")
    print(f"   Processing time: {processing_time:.2f} seconds")
    print(f"   Peak memory usage: {final_memory:.1f} MB")
    print(f"   Memory increase: {final_memory - initial_memory:.1f} MB")
    
    print(f"\n📈 Results Summary:")
    print(f"   Additions: {len(result.additions):,}")
    print(f"   Modifications: {len(result.modifications):,}")
    print(f"   Deletions: {len(result.deletions):,}")
    
    # Save results if output file specified
    if output_file:
        with open(output_file, 'w') as f:
            f.write(OutputFormatter.format_json(result))
        print(f"💾 Results saved to: {output_file}")
    
    return result

if __name__ == '__main__':
    import sys
    if len(sys.argv) not in [3, 4]:
        print("Usage: python large_file_processor.py <base_file> <delta_file> [output_file]")
        sys.exit(1)
    
    output_file = sys.argv[3] if len(sys.argv) == 4 else None
    
    try:
        result = process_large_csv_files(sys.argv[1], sys.argv[2], output_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
```

**Usage:**
```bash
# Process large files with automatic configuration
python large_file_processor.py huge_base.csv huge_delta.csv results.json
```

### Example 9: Chunk Size Optimization

**Script: `optimize_chunk_size.py`**
```python
#!/usr/bin/env python3
import time
import psutil
from csvcdc import CSVCDC

def test_chunk_sizes(base_file, delta_file, chunk_sizes=[100000, 250000, 500000, 750000]):
    """Test different chunk sizes to find optimal performance"""
    
    print("🧪 Testing different chunk sizes for optimal performance...\n")
    
    results = []
    
    for chunk_size in chunk_sizes:
        print(f"Testing chunk size: {chunk_size:,}")
        
        # Monitor memory and time
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024 ** 2)  # MB
        start_time = time.time()
        
        try:
            cdc = CSVCDC(
                largefiles=1,
                chunk_size=chunk_size,
                progressbar=0,  # Disable for cleaner output
                autopk=0,
                primary_key=[0]
            )
            
            result = cdc.compare(base_file, delta_file)
            
            end_time = time.time()
            final_memory = process.memory_info().rss / (1024 ** 2)  # MB
            
            processing_time = end_time - start_time
            memory_used = final_memory - initial_memory
            
            total_changes = len(result.additions) + len(result.modifications) + len(result.deletions)
            
            results.append({
                'chunk_size': chunk_size,
                'processing_time': processing_time,
                'memory_used': memory_used,
                'peak_memory': final_memory,
                'total_changes': total_changes,
                'success': True
            })
            
            print(f"  ✅ Time: {processing_time:.1f}s, Memory: {memory_used:.1f}MB, Changes: {total_changes:,}")
            
        except Exception as e:
            results.append({
                'chunk_size': chunk_size,
                'error': str(e),
                'success': False
            })
            print(f"  ❌ Failed: {e}")
        
        print()
    
    # Find optimal chunk size
    successful_results = [r for r in results if r['success']]
    
    if successful_results:
        # Sort by processing time (primary) and memory usage (secondary)
        optimal = min(successful_results, key=lambda x: (x['processing_time'], x['memory_used']))
        
        print("🎯 Optimization Results:")
        print(f"   Optimal chunk size: {optimal['chunk_size']:,}")
        print(f"   Processing time: {optimal['processing_time']:.1f}s")
        print(f"   Memory usage: {optimal['memory_used']:.1f}MB")
        print(f"   Total changes: {optimal['total_changes']:,}")
        
        return optimal['chunk_size']
    
    else:
        print("❌ No chunk size worked successfully")
        return None

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python optimize_chunk_size.py <base_file> <delta_file>")
        sys.exit(1)
    
    optimal_chunk_size = test_chunk_sizes(sys.argv[1], sys.argv[2])
    
    if optimal_chunk_size:
        print(f"\n💡 Recommended command:")
        print(f"python csvcdc.py {sys.argv[1]} {sys.argv[2]} --largefiles 1 --chunk-size {optimal_chunk_size}")
```

## Real-World Scenarios

### Example 10: E-commerce Price Monitoring

**Scenario:** Daily price monitoring for competitive analysis.

**Script: `price_monitor.py`**
```python
#!/usr/bin/env python3
import sys
import json
import datetime
import os
from csvcdc import CSVCDC, OutputFormatter

def monitor_prices(yesterday_file, today_file, output_dir, use_large_mode=False):
    """Monitor price changes and generate reports"""
    
    # Determine if we need large file processing
    if use_large_mode or os.path.getsize(yesterday_file) > 1e9:  # > 1GB
        print("🔧 Using large file mode for price monitoring")
        cdc = CSVCDC(
            primary_key=[0],  # SKU as primary key
            ignore_columns=[5, 6],  # Ignore timestamp and stock columns
            progressbar=1,
            largefiles=1,
            chunk_size=300000
        )
    else:
        cdc = CSVCDC(
            primary_key=[0],  # SKU as primary key
            ignore_columns=[5, 6],  # Ignore timestamp and stock columns
            progressbar=1
        )
    
    result = cdc.compare(yesterday_file, today_file)
    
    # Analyze price changes specifically
    price_increases = []
    price_decreases = []
    
    for mod in result.modifications:
        old_parts = mod['Original'].split(',')
        new_parts = mod['Current'].split(',')
        
        if len(old_parts) >= 3 and len(new_parts) >= 3:
            try:
                old_price = float(old_parts[2])
                new_price = float(new_parts[2])
                
                if new_price > old_price:
                    price_increases.append({
                        'sku': old_parts[0],
                        'name': old_parts[1],
                        'old_price': old_price,
                        'new_price': new_price,
                        'increase': new_price - old_price,
                        'percent_increase': ((new_price - old_price) / old_price) * 100
                    })
                elif new_price < old_price:
                    price_decreases.append({
                        'sku': old_parts[0],
                        'name': old_parts[1],
                        'old_price': old_price,
                        'new_price': new_price,
                        'decrease': old_price - new_price,
                        'percent_decrease': ((old_price - new_price) / old_price) * 100
                    })
            except ValueError:
                continue
    
    # Generate report
    report = {
        'date': datetime.datetime.now().isoformat(),
        'summary': {
            'new_products': len(result.additions),
            'discontinued_products': len(result.deletions),
            'total_changes': len(result.modifications),
            'price_increases': len(price_increases),
            'price_decreases': len(price_decreases)
        },
        'price_increases': price_increases,
        'price_decreases': price_decreases
    }
    
    # Save detailed report
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/price_report_{datetime.date.today()}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    # Save raw changes
    with open(f"{output_dir}/raw_changes_{datetime.date.today()}.json", 'w') as f:
        f.write(OutputFormatter.format_json(result))
    
    return report

if __name__ == '__main__':
    if len(sys.argv) not in [4, 5]:
        print("Usage: python price_monitor.py <yesterday.csv> <today.csv> <output_dir> [--large]")
        sys.exit(1)
    
    use_large_mode = len(sys.argv) == 5 and sys.argv[4] == '--large'
    
    report = monitor_prices(sys.argv[1], sys.argv[2], sys.argv[3], use_large_mode)
    
    print(f"📊 Price Monitoring Report - {datetime.date.today()}")
    print(f"New products: {report['summary']['new_products']:,}")
    print(f"Discontinued: {report['summary']['discontinued_products']:,}")  
    print(f"Price increases: {report['summary']['price_increases']:,}")
    print(f"Price decreases: {report['summary']['price_decreases']:,}")
```

**Usage:**
```bash
# Regular mode
python price_monitor.py prices_yesterday.csv prices_today.csv reports/

# Large file mode
python price_monitor.py huge_prices_yesterday.csv huge_prices_today.csv reports/ --large
```

### Example 11: Database Synchronization Validation

**Scenario:** Validate that database exports match between environments, handling large exports.

**Script: `db_sync_validator.py`**
```python
#!/usr/bin/env python3
import argparse
import os
from csvcdc import CSVCDC, OutputFormatter

def validate_db_sync(prod_export, staging_export, table_config):
    """Validate database synchronization between environments"""
    
    primary_key = table_config.get('primary_key', [0])
    ignore_cols = table_config.get('ignore_columns', [])
    
    # Determine if large file processing is needed
    prod_size = os.path.getsize(prod_export) / (1024 ** 3)  # GB
    staging_size = os.path.getsize(staging_export) / (1024 ** 3)  # GB
    
    use_large_mode = prod_size > 0.5 or staging_size > 0.5  # > 500MB
    
    if use_large_mode:
        print(f"🔧 Large files detected (Prod: {prod_size:.2f}GB, Staging: {staging_size:.2f}GB)")
        print("Using large file processing mode...")
        
        cdc = CSVCDC(
            primary_key=primary_key,
            ignore_columns=ignore_cols,
            progressbar=1,
            largefiles=1,
            chunk_size=400000
        )
    else:
        cdc = CSVCDC(
            primary_key=primary_key,
            ignore_columns=ignore_cols,
            progressbar=1
        )
    
    result = cdc.compare(prod_export, staging_export)
    
    # Check if environments are in sync
    total_differences = len(result.additions) + len(result.modifications) + len(result.deletions)
    
    if total_differences == 0:
        print("✅ Environments are in sync!")
        return True
    else:
        print(f"❌ Found {total_differences:,} differences:")
        print(f"   Missing in staging: {len(result.deletions):,}")
        print(f"   Extra in staging: {len(result.additions):,}")
        print(f"   Data mismatches: {len(result.modifications):,}")
        
        # For large result sets, save to file instead of printing
        if total_differences > 1000:
            output_file = f"sync_differences_{os.path.basename(prod_export)}.json"
            with open(output_file, 'w') as f:
                f.write(OutputFormatter.format_json(result))
            print(f"💾 Detailed differences saved to: {output_file}")
        else:
            print("\nDetailed differences:")
            print(OutputFormatter.format_diff(result))
        
        return False

# Configuration for different tables
TABLE_CONFIGS = {
    'users': {
        'primary_key': [0],  # user_id
        'ignore_columns': [6, 7]  # last_login, created_at
    },
    'products': {
        'primary_key': [0],  # product_id
        'ignore_columns': [5]  # last_updated
    },
    'orders': {
        'primary_key': [0],  # order_id
        'ignore_columns': [4, 5]  # created_at, updated_at
    },
    'transactions': {
        'primary_key': [0],  # transaction_id
        'ignore_columns': [8, 9]  # created_at, updated_at
    }
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate database synchronization')
    parser.add_argument('table', choices=TABLE_CONFIGS.keys())
    parser.add_argument('prod_file', help='Production export file')
    parser.add_argument('staging_file', help='Staging export file')
    
    args = parser.parse_args()
    
    config = TABLE_CONFIGS[args.table]
    is_synced = validate_db_sync(args.prod_file, args.staging_file, config)
    
    exit(0 if is_synced else 1)
```

## Integration Examples

### Example 12: Git Hook Integration with Large File Support

**Script: `git-hooks/pre-commit`**
```bash
#!/bin/bash
# Git pre-commit hook to validate CSV changes with large file support

# Find all staged CSV files
staged_csvs=$(git diff --cached --name-only --diff-filter=M | grep '\.csv$')

if [ -z "$staged_csvs" ]; then
    echo "No CSV files to validate"
    exit 0
fi

echo "🔍 Validating CSV changes..."

for csv_file in $staged_csvs; do
    echo "Checking $csv_file..."
    
    # Check file size to determine processing mode
    file_size=$(stat -f%z "$csv_file" 2>/dev/null || stat -c%s "$csv_file" 2>/dev/null || echo "0")
    large_mode=""
    
    if [ "$file_size" -gt 104857600 ]; then  # > 100MB
        echo "  📁 Large file detected ($(($file_size / 1024 / 1024))MB), using chunked processing"
        large_mode="--largefiles 1 --chunk-size 200000"
    fi
    
    # Get the previous version
    git show HEAD:$csv_file > /tmp/old_$csv_file 2>/dev/null
    
    if [ $? -eq 0 ]; then
        # Compare versions
        python csvcdc.py /tmp/old_$csv_file $csv_file \
            --autopk 1 \
            --format json \
            $large_mode > /tmp/changes_$csv_file.json
        
        # Check if changes are significant
        changes=$(python -c "
import json
with open('/tmp/changes_${csv_file}.json') as f:
    data = json.load(f)
    total = len(data['Additions']) + len(data['Modifications']) + len(data['Deletions'])
    print(total)
")
        
        if [ $changes -gt 1000 ]; then
            echo "⚠️  Warning: $changes changes detected in $csv_file"
            echo "   This seems like a large change. Please verify."
            
            # Optionally require confirmation
            read -p "Continue with commit? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Commit aborted"
                exit 1
            fi
        else
            echo "✅ $changes changes validated in $csv_file"
        fi
        
        # Cleanup
        rm -f /tmp/old_$csv_file /tmp/changes_$csv_file.json
    else
        echo "📄 New file: $csv_file (skipping validation)"
    fi
done

echo "✅ CSV validation complete"
```

### Example 13: Automated Reporting with Large File Support

**Script: `daily_report.sh`**
```bash
#!/bin/bash
# Daily CSV comparison report with large file support

REPORT_DIR="/var/reports/csv-cdc"
DATA_DIR="/var/data"
DATE=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)

mkdir -p $REPORT_DIR/$DATE

echo "📊 Daily CSV CDC Report - $DATE" > $REPORT_DIR/$DATE/summary.txt

# Function to get file size in MB
get_file_size_mb() {
    if [ -f "$1" ]; then
        stat -f%z "$1" 2>/dev/null | awk '{print int($1/1024/1024)}' || \
        stat -c%s "$1" 2>/dev/null | awk '{print int($1/1024/1024)}' || \
        echo "0"
    else
        echo "0"
    fi
}

# Compare each dataset
for dataset in products customers orders transactions; do
    echo "Processing $dataset..." >> $REPORT_DIR/$DATE/summary.txt
    
    yesterday_file="$DATA_DIR/${dataset}_$YESTERDAY.csv"
    today_file="$DATA_DIR/${dataset}_$DATE.csv"
    
    if [ -f "$yesterday_file" ] && [ -f "$today_file" ]; then
        # Check file sizes to determine processing mode
        yesterday_size=$(get_file_size_mb "$yesterday_file")
        today_size=$(get_file_size_mb "$today_file")
        
        large_mode=""
        if [ "$yesterday_size" -gt 100 ] || [ "$today_size" -gt 100 ]; then
            echo "  Large files detected (${yesterday_size}MB, ${today_size}MB)" >> $REPORT_DIR/$DATE/summary.txt
            large_mode="--largefiles 1 --chunk-size 300000"
        fi
        
        # Run comparison
        python csvcdc.py \
            "$yesterday_file" \
            "$today_file" \
            --autopk 1 \
            --format json \
            --progressbar 0 \
            $large_mode > $REPORT_DIR/$DATE/${dataset}_changes.json
        
        python csvcdc.py \
            "$yesterday_file" \
            "$today_file" \
            --autopk 1 \
            --format diff \
            --progressbar 0 \
            $large_mode > $REPORT_DIR/$DATE/${dataset}_changes.diff
        
        # Extract summary
        changes=$(python -c "
import json
try:
    with open('$REPORT_DIR/$DATE/${dataset}_changes.json') as f:
        data = json.load(f)
        print(f'  Additions: {len(data[\"Additions\"]):,}')
        print(f'  Modifications: {len(data[\"Modifications\"]):,}')
        print(f'  Deletions: {len(data[\"Deletions\"]):,}')
except Exception as e:
    print(f'  Error processing results: {e}')
")
        
        echo "$changes" >> $REPORT_DIR/$DATE/summary.txt
    else
        echo "  Missing data files for $dataset" >> $REPORT_DIR/$DATE/summary.txt
    fi
    
    echo "" >> $REPORT_DIR/$DATE/summary.txt
done

# Email report (optional)
if command -v mail &> /dev/null; then
    mail -s "Daily CSV CDC Report - $DATE" admin@company.com < $REPORT_DIR/$DATE/summary.txt
fi

echo "Report generated: $REPORT_DIR/$DATE/"
```

## Performance Examples

### Example 14: Benchmarking Large File Performance

**Script: `benchmark.py`**
```python
#!/usr/bin/env python3
import time
import psutil
import os
from csvcdc import CSVCDC

def benchmark_processing_modes(base_file, delta_file):
    """Benchmark different processing modes"""
    
    file_size_gb = (os.path.getsize(base_file) + os.path.getsize(delta_file)) / (1024 ** 3)
    print(f"📊 Benchmarking files totaling {file_size_gb:.2f}GB\n")
    
    results = []
    
    # Test configurations
    configs = [
        {
            'name': 'Standard Mode',
            'params': {'largefiles': 0, 'progressbar': 0}
        },
        {
            'name': 'Large File Mode (500K chunks)',
            'params': {'largefiles': 1, 'chunk_size': 500000, 'progressbar': 0}
        },
        {
            'name': 'Large File Mode (250K chunks)',
            'params': {'largefiles': 1, 'chunk_size': 250000, 'progressbar': 0}
        },
        {
            'name': 'Large File Mode (100K chunks)',
            'params': {'largefiles': 1, 'chunk_size': 100000, 'progressbar': 0}
        }
    ]
    
    for config in configs:
        print(f"🧪 Testing: {config['name']}")
        
        try:
            # Monitor system resources
            process = psutil.Process()
            initial_memory = process.memory_info().rss / (1024 ** 2)  # MB
            start_time = time.time()
            
            # Create CDC instance
            cdc = CSVCDC(autopk=0, primary_key=[0], **config['params'])
            
            # Perform comparison
            result = cdc.compare(base_file, delta_file)
            
            # Calculate metrics
            end_time = time.time()
            final_memory = process.memory_info().rss / (1024 ** 2)  # MB
            
            processing_time = end_time - start_time
            memory_used = final_memory - initial_memory
            total_changes = len(result.additions) + len(result.modifications) + len(result.deletions)
            throughput = file_size_gb / processing_time if processing_time > 0 else 0
            
            result_data = {
                'name': config['name'],
                'processing_time': processing_time,
                'memory_used': memory_used,
                'peak_memory': final_memory,
                'total_changes': total_changes,
                'throughput_gb_s': throughput,
                'success': True
            }
            
            results.append(result_data)
            
            print(f"  ✅ Success!")
            print(f"     Time: {processing_time:.1f}s")
            print(f"     Memory: {memory_used:.1f}MB (peak: {final_memory:.1f}MB)")
            print(f"     Throughput: {throughput:.2f} GB/s")
            print(f"     Changes: {total_changes:,}")
            
        except Exception as e:
            results.append({
                'name': config['name'],
                'error': str(e),
                'success': False
            })
            print(f"  ❌ Failed: {e}")
        
        print()
    
    # Summary
    successful_results = [r for r in results if r['success']]
    
    if successful_results:
        print("🏆 Performance Summary:")
        print("=" * 60)
        
        # Sort by processing time
        by_time = sorted(successful_results, key=lambda x: x['processing_time'])
        print(f"Fastest: {by_time[0]['name']} ({by_time[0]['processing_time']:.1f}s)")
        
        # Sort by memory usage
        by_memory = sorted(successful_results, key=lambda x: x['memory_used'])
        print(f"Most memory efficient: {by_memory[0]['name']} ({by_memory[0]['memory_used']:.1f}MB)")
        
        # Sort by throughput
        by_throughput = sorted(successful_results, key=lambda x: x['throughput_gb_s'], reverse=True)
        print(f"Highest throughput: {by_throughput[0]['name']} ({by_throughput[0]['throughput_gb_s']:.2f} GB/s)")
        
        print("\n💡 Recommendation:")
        # Simple scoring: balance time and memory
        scored = [(r['name'], r['processing_time'] * 0.6 + r['memory_used'] * 0.4 / 1000) 
                 for r in successful_results]
        best = min(scored, key=lambda x: x[1])
        print(f"Best overall: {best[0]}")
    
    return results

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python benchmark.py <base_file> <delta_file>")
        sys.exit(1)
    
    results = benchmark_processing_modes(sys.argv[1], sys.argv[2])
```

## Troubleshooting Examples

### Example 15: Memory Issues Debugging

**Script: `debug_memory.py`**
```python
#!/usr/bin/env python3
import psutil
import os
import gc
from csvcdc import CSVCDC

def debug_memory_usage(base_file, delta_file):
    """Debug memory usage patterns"""
    
    def get_memory_info():
        process = psutil.Process()
        return {
            'rss': process.memory_info().rss / (1024 ** 2),  # MB
            'vms': process.memory_info().vms / (1024 ** 2),  # MB
            'available': psutil.virtual_memory().available / (1024 ** 2),  # MB
        }
    
    print("🔍 Memory Usage Analysis")
    print("=" * 40)
    
    # Initial state
    initial = get_memory_info()
    print(f"Initial memory: {initial['rss']:.1f}MB RSS, {initial['available']:.1f}MB available")
    
    # File size analysis
    base_size = os.path.getsize(base_file) / (1024 ** 2)  # MB
    delta_size = os.path.getsize(delta_file) / (1024 ** 2)  # MB
    total_size = base_size + delta_size
    
    print(f"File sizes: Base={base_size:.1f}MB, Delta={delta_size:.1f}MB, Total={total_size:.1f}MB")
    
    # Memory recommendations
    estimated_memory_needed = total_size * 3  # Rough estimate
    print(f"Estimated memory needed: {estimated_memory_needed:.1f}MB")
    
    if estimated_memory_needed > initial['available']:
        print("⚠️  WARNING: Estimated memory requirement exceeds available memory!")
        print("🔧 Recommendations:")
        print(f"   1. Use --largefiles 1 to enable chunked processing")
        
        # Calculate recommended chunk size
        available_for_processing = initial['available'] * 0.8  # Use 80% of available
        recommended_chunk = int(available_for_processing * 1000 / 3)  # Conservative estimate
        print(f"   2. Use --chunk-size {recommended_chunk} or smaller")
        print(f"   3. Close other applications to free memory")
        print(f"   4. Consider processing on a machine with more RAM")
        
        return False  # Don't proceed with memory-intensive test
    
    # Test different approaches
    print(f"\n🧪 Testing memory usage patterns:")
    
    # Test 1: Standard mode (if file is small enough)
    if total_size < 500:  # Only test if < 500MB
        print(f"\nTest 1: Standard Mode")
        gc.collect()
        before = get_memory_info()
        
        try:
            cdc = CSVCDC(progressbar=0, autopk=0, primary_key=[0])
            result = cdc.compare(base_file, delta_file)
            
            after = get_memory_info()
            memory_increase = after['rss'] - before['rss']
            
            print(f"  Memory increase: {memory_increase:.1f}MB")
            print(f"  Peak memory: {after['rss']:.1f}MB")
            print(f"  Result: {len(result.additions) + len(result.modifications) + len(result.deletions)} changes")
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    # Test 2: Large file mode
    print(f"\nTest 2: Large File Mode")
    gc.collect()
    before = get_memory_info()
    
    try:
        cdc = CSVCDC(
            largefiles=1,
            chunk_size=100000,
            progressbar=0,
            autopk=0,
            primary_key=[0]
        )
        result = cdc.compare(base_file, delta_file)
        
        after = get_memory_info()
        memory_increase = after['rss'] - before['rss']
        
        print(f"  Memory increase: {memory_increase:.1f}MB")
        print(f"  Peak memory: {after['rss']:.1f}MB")
        print(f"  Result: {len(result.additions) + len(result.modifications) + len(result.deletions)} changes")
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    
    print(f"\n✅ Memory analysis complete")
    return True

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python debug_memory.py <base_file> <delta_file>")
        sys.exit(1)
    
    debug_memory_usage(sys.argv[1], sys.argv[2])
```

### Example 16: Complete Large File Processing Guide

**Commands for different file sizes:**

```bash
# Small files (< 100MB) - Standard processing
python csvcdc.py small_base.csv small_delta.csv --autopk 1

# Medium files (100MB - 1GB) - Standard with progress monitoring
python csvcdc.py medium_base.csv medium_delta.csv --autopk 1 --time --progressbar 1

# Large files (1GB - 10GB) - Enable large file mode
python csvcdc.py large_base.csv large_delta.csv \
  --largefiles 1 \
  --autopk 1 \
  --time \
  --progressbar 1

# Very large files (10GB+) - Smaller chunks and specific primary key
python csvcdc.py huge_base.csv huge_delta.csv \
  --largefiles 1 \
  --chunk-size 250000 \
  --primary-key 0 \
  --time \
  --progressbar 1

# Extremely large files (50GB+) - Minimal chunks and JSON output
python csvcdc.py massive_base.csv massive_delta.csv \
  --largefiles 1 \
  --chunk-size 100000 \
  --primary-key 0 \
  --format json \
  --progressbar 1 \
  --time > results.json

# Memory-constrained environments - Ultra-conservative settings
python csvcdc.py constrained_base.csv constrained_delta.csv \
  --largefiles 1 \
  --chunk-size 50000 \
  --primary-key 0 \
  --progressbar 0 \
  --format json > results.json 2> processing.log