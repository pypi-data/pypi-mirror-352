# CSV CDC Examples

This document provides comprehensive examples of using the CSV CDC tool for various scenarios.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Advanced Configuration](#advanced-configuration)
3. [Real-World Scenarios](#real-world-scenarios)
4. [Integration Examples](#integration-examples)
5. [Performance Examples](#performance-examples)
6. [Troubleshooting Examples](#troubleshooting-examples)

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

## Real-World Scenarios

### Example 6: E-commerce Price Monitoring

**Scenario:** Daily price monitoring for competitive analysis.

**Script: `price_monitor.py`**
```python
#!/usr/bin/env python3
import sys
import json
import datetime
from csvcdc import CSVCDC, OutputFormatter

def monitor_prices(yesterday_file, today_file, output_dir):
    """Monitor price changes and generate reports"""
    
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
    with open(f"{output_dir}/price_report_{datetime.date.today()}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    # Save raw changes
    with open(f"{output_dir}/raw_changes_{datetime.date.today()}.json", 'w') as f:
        f.write(OutputFormatter.format_json(result))
    
    return report

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python price_monitor.py <yesterday.csv> <today.csv> <output_dir>")
        sys.exit(1)
    
    report = monitor_prices(sys.argv[1], sys.argv[2], sys.argv[3])
    
    print(f"📊 Price Monitoring Report - {datetime.date.today()}")
    print(f"New products: {report['summary']['new_products']}")
    print(f"Discontinued: {report['summary']['discontinued_products']}")  
    print(f"Price increases: {report['summary']['price_increases']}")
    print(f"Price decreases: {report['summary']['price_decreases']}")
```

**Usage:**
```bash
python price_monitor.py prices_yesterday.csv prices_today.csv reports/
```

### Example 7: Database Synchronization Validation

**Scenario:** Validate that database exports match between environments.

**Script: `db_sync_validator.py`**
```python
#!/usr/bin/env python3
import argparse
from csvcdc import CSVCDC, OutputFormatter

def validate_db_sync(prod_export, staging_export, table_config):
    """Validate database synchronization between environments"""
    
    primary_key = table_config.get('primary_key', [0])
    ignore_cols = table_config.get('ignore_columns', [])
    
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
        print(f"❌ Found {total_differences} differences:")
        print(f"   Missing in staging: {len(result.deletions)}")
        print(f"   Extra in staging: {len(result.additions)}")
        print(f"   Data mismatches: {len(result.modifications)}")
        
        # Output detailed differences
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

**Usage:**
```bash
# Validate user table sync
python db_sync_validator.py users prod_users.csv staging_users.csv

# Validate product table sync
python db_sync_validator.py products prod_products.csv staging_products.csv
```

### Example 8: Data Quality Monitoring

**Scenario:** Monitor data quality by tracking changes in key metrics.

**Script: `quality_monitor.py`**
```python
#!/usr/bin/env python3
import json
import statistics
from csvcdc import CSVCDC

def analyze_data_quality(old_file, new_file):
    """Analyze data quality changes between datasets"""
    
    cdc = CSVCDC(autopk=1, progressbar=1)
    result = cdc.compare(old_file, new_file)
    
    # Analyze patterns in changes
    quality_metrics = {
        'completeness': analyze_completeness_changes(result),
        'consistency': analyze_consistency_changes(result),
        'accuracy': analyze_accuracy_changes(result)
    }
    
    return quality_metrics

def analyze_completeness_changes(result):
    """Analyze changes in data completeness (null/empty values)"""
    empty_to_filled = 0
    filled_to_empty = 0
    
    for mod in result.modifications:
        old_values = mod['Original'].split(',')
        new_values = mod['Current'].split(',')
        
        for old_val, new_val in zip(old_values, new_values):
            if not old_val.strip() and new_val.strip():
                empty_to_filled += 1
            elif old_val.strip() and not new_val.strip():
                filled_to_empty += 1
    
    return {
        'empty_to_filled': empty_to_filled,
        'filled_to_empty': filled_to_empty,
        'net_improvement': empty_to_filled - filled_to_empty
    }

def analyze_consistency_changes(result):
    """Analyze changes in data consistency"""
    # This is a simplified example - you'd implement domain-specific rules
    format_fixes = 0
    format_breaks = 0
    
    for mod in result.modifications:
        # Example: phone number format consistency
        old_phone = extract_phone(mod['Original'])
        new_phone = extract_phone(mod['Current'])
        
        if old_phone and new_phone:
            if is_well_formatted(new_phone) and not is_well_formatted(old_phone):
                format_fixes += 1
            elif not is_well_formatted(new_phone) and is_well_formatted(old_phone):
                format_breaks += 1
    
    return {
        'format_fixes': format_fixes,
        'format_breaks': format_breaks,
        'net_improvement': format_fixes - format_breaks
    }

def analyze_accuracy_changes(result):
    """Analyze changes that might indicate accuracy improvements"""
    # Example: email validation improvements
    valid_emails_added = 0
    valid_emails_removed = 0
    
    for mod in result.modifications:
        old_email = extract_email(mod['Original'])
        new_email = extract_email(mod['Current'])
        
        if old_email and new_email:
            if is_valid_email(new_email) and not is_valid_email(old_email):
                valid_emails_added += 1
            elif not is_valid_email(new_email) and is_valid_email(old_email):
                valid_emails_removed += 1
    
    return {
        'valid_emails_added': valid_emails_added,
        'valid_emails_removed': valid_emails_removed,
        'net_improvement': valid_emails_added - valid_emails_removed
    }

# Helper functions (simplified examples)
def extract_phone(row):
    parts = row.split(',')
    return parts[3] if len(parts) > 3 else None

def extract_email(row):
    parts = row.split(',')
    return parts[2] if len(parts) > 2 else None

def is_well_formatted(phone):
    return len(phone.replace('-', '').replace(' ', '')) == 10

def is_valid_email(email):
    return '@' in email and '.' in email.split('@')[-1]

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python quality_monitor.py <old_file> <new_file>")
        sys.exit(1)
    
    metrics = analyze_data_quality(sys.argv[1], sys.argv[2])
    
    print("📈 Data Quality Analysis:")
    print(f"Completeness net improvement: {metrics['completeness']['net_improvement']}")
    print(f"Consistency net improvement: {metrics['consistency']['net_improvement']}")
    print(f"Accuracy net improvement: {metrics['accuracy']['net_improvement']}")
    
    # Save detailed metrics
    with open('quality_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
```

## Integration Examples

### Example 9: Git Hook Integration

**Scenario:** Automatically compare CSV files when they're committed to git.

**Script: `git-hooks/pre-commit`**
```bash
#!/bin/bash
# Git pre-commit hook to validate CSV changes

# Find all staged CSV files
staged_csvs=$(git diff --cached --name-only --diff-filter=M | grep '\.csv$')

if [ -z "$staged_csvs" ]; then
    echo "No CSV files to validate"
    exit 0
fi

echo "🔍 Validating CSV changes..."

for csv_file in $staged_csvs; do
    echo "Checking $csv_file..."
    
    # Get the previous version
    git show HEAD:$csv_file > /tmp/old_$csv_file 2>/dev/null
    
    if [ $? -eq 0 ]; then
        # Compare versions
        python csvcdc.py /tmp/old_$csv_file $csv_file \
            --autopk 1 \
            --format json > /tmp/changes_$csv_file.json
        
        # Check if changes are significant
        changes=$(python -c "
import json
with open('/tmp/changes_${csv_file}.json') as f:
    data = json.load(f)
    total = len(data['Additions']) + len(data['Modifications']) + len(data['Deletions'])
    print(total)
")
        
        if [ $changes -gt 100 ]; then
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

### Example 10: Automated Reporting with Cron

**Scenario:** Daily automated comparison reports.

**Script: `daily_report.sh`**
```bash
#!/bin/bash
# Daily CSV comparison report

REPORT_DIR="/var/reports/csv-cdc"
DATA_DIR="/var/data"
DATE=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)

mkdir -p $REPORT_DIR/$DATE

echo "📊 Daily CSV CDC Report - $DATE" > $REPORT_DIR/$DATE/summary.txt

# Compare each dataset
for dataset in products customers orders; do
    echo "Processing $dataset..." >> $REPORT_DIR/$DATE/summary.txt
    
    if [ -f "$DATA_DIR/${dataset}_$YESTERDAY.csv" ] && [ -f "$DATA_DIR/${dataset}_$DATE.csv" ]; then
        python csvcdc.py \
            $DATA_DIR/${dataset}_$YESTERDAY.csv \
            $DATA_DIR/${dataset}_$DATE.csv \
            --autopk 1 \
            --format json > $REPORT_DIR/$DATE/${dataset}_changes.json
        
        python csvcdc.py \
            $DATA_DIR/${dataset}_$YESTERDAY.csv \
            $DATA_DIR/${dataset}_$DATE.csv \
            --autopk 1 \
            --format diff > $REPORT_DIR/$DATE/${dataset}_changes.diff
        
        # Extract summary
        changes=$(python -c "
import json
with open('$REPORT_DIR/$DATE/${dataset}_changes.json') as f:
    data = json.load(f)
    print(f'  Additions: {len(data[\"Additions\"])}')
    print(f'  Modifications: {len(data[\"Modifications\"])}')
    print(f'  Deletions: {len(data[\"Deletions\"])}')
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

**Crontab entry:**
```bash
# Run daily at 6 AM
0 6 * * * /path/to/daily_report.sh
```

## Performance Examples

### Example 11: Large File Processing

**Scenario:** Processing multi-gigabyte CSV files efficiently.

**Script: `large_file_processor.py`**
```python
#!/usr/bin/env python3
import time
import psutil
import os
from csvcdc import CSVCDC

def process_large_files(base_file, delta_file, chunk_size=None):
    """Process large files with performance monitoring"""
    
    # Get file sizes
    base_size = os.path.getsize(base_file) / (1024 * 1024)  # MB
    delta_size = os.path.getsize(delta_file) / (1024 * 1024)  # MB
    
    print(f"📁 File sizes: Base={base_size:.1f}MB, Delta={delta_size:.1f}MB")
    
    # Monitor system resources
    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
    
    start_time = time.time()
    
    # Configure for large files
    cdc = CSVCDC(
        autopk=1,  # Auto-detect primary key
        progressbar=1  # Show progress
    )
    
    print("🚀 Starting comparison...")
    result = cdc.compare(base_file, delta_file)
    
    end_time = time.time()
    final_memory = process.memory_info().rss / (1024 * 1024)  # MB
    
    # Performance metrics
    processing_time = end_time - start_time
    memory_used = final_memory - initial_memory
    throughput = (base_size + delta_size) / processing_time  # MB/s
    
    print(f"\n📊 Performance Metrics:")
    print(f"   Processing time: {processing_time:.2f} seconds")
    print(f"   Memory used: {memory_used:.1f} MB")
    print(f"   Peak memory: {final_memory:.1f} MB")
    print(f"   Throughput: {throughput:.1f} MB/s")
    
    print(f"\n📈 Results:")
    print(f"   Additions: {len(result.additions)}")
    print(f"   Modifications: {len(result.modifications)}")
    print(f"   Deletions: {len(result.deletions)}")
    
    return result

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python large_file_processor.py <base_file> <delta_file>")
        sys.exit(1)
    
    result = process_large_files(sys.argv[1], sys.argv[2])
```

### Example 12: Parallel Processing Multiple Files

**Scenario:** Compare multiple file pairs in parallel.

**Script: `parallel_processor.py`**
```python
#!/usr/bin/env python3
import concurrent.futures
import os
import time
from pathlib import Path
from csvcdc import CSVCDC, OutputFormatter

def compare_file_pair(file_pair):
    """Compare a single pair of files"""
    base_file, delta_file, output_prefix = file_pair
    
    try:
        cdc = CSVCDC(autopk=1, progressbar=0)  # Disable progress for parallel processing
        result = cdc.compare(base_file, delta_file)
        
        # Save results
        with open(f"{output_prefix}_changes.json", 'w') as f:
            f.write(OutputFormatter.format_json(result))
        
        return {
            'base_file': base_file,
            'delta_file': delta_file,
            'additions': len(result.additions),
            'modifications': len(result.modifications),
            'deletions': len(result.deletions),
            'success': True
        }
        
    except Exception as e:
        return {
            'base_file': base_file,
            'delta_file': delta_file,
            'error': str(e),
            'success': False
        }

def parallel_compare(base_dir, delta_dir, output_dir, max_workers=None):
    """Compare all CSV files in parallel"""
    
    if max_workers is None:
        max_workers = min(32, (os.cpu_count() or 1) + 4)
    
    # Find all CSV file pairs
    base_files = list(Path(base_dir).glob('*.csv'))
    file_pairs = []
    
    for base_file in base_files:
        delta_file = Path(delta_dir) / base_file.name
        if delta_file.exists():
            output_prefix = Path(output_dir) / base_file.stem
            file_pairs.append((str(base_file), str(delta_file), str(output_prefix)))
    
    print(f"🔄 Processing {len(file_pairs)} file pairs with {max_workers} workers...")
    
    start_time = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_pair = {executor.submit(compare_file_pair, pair): pair for pair in file_pairs}
        
        for future in concurrent.futures.as_completed(future_to_pair):
            result = future.result()
            results.append(result)
            
            if result['success']:
                print(f"✅ {Path(result['base_file']).name}: "
                      f"{result['additions']}A {result['modifications']}M {result['deletions']}D")
            else:
                print(f"❌ {Path(result['base_file']).name}: {result['error']}")
    
    end_time = time.time()
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    total_changes = sum(r.get('additions', 0) + r.get('modifications', 0) + r.get('deletions', 0) 
                       for r in results if r['success'])
    
    print(f"\n📊 Summary:")
    print(f"   Processed: {len(file_pairs)} file pairs")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Total changes: {total_changes}")
    print(f"   Processing time: {end_time - start_time:.2f} seconds")
    
    return results

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 4:
        print("Usage: python parallel_processor.py <base_dir> <delta_dir> <output_dir>")
        sys.exit(1)
    
    os.makedirs(sys.argv[3], exist_ok=True)
    results = parallel_compare(sys.argv[1], sys.argv[2], sys.argv[3])
```

## Troubleshooting Examples

### Example 13: Debugging Primary Key Issues

**Script: `debug_primary_key.py`**
```python
#!/usr/bin/env python3
from csvcdc import CSVCDC
import pandas as pd

def debug_primary_key_selection(base_file, delta_file):
    """Debug primary key selection issues"""
    
    print("🔍 Analyzing primary key options...")
    
    # Load data for analysis
    base_df = pd.read_csv(base_file, dtype=str)
    delta_df = pd.read_csv(delta_file, dtype=str)
    
    print(f"Base file: {len(base_df)} rows, {len(base_df.columns)} columns")
    print(f"Delta file: {len(delta_df)} rows, {len(delta_df.columns)} columns")
    
    # Analyze each column for uniqueness
    print(f"\nColumn analysis:")
    for i, col in enumerate(base_df.columns):
        base_unique = base_df[col].nunique()
        base_unique_pct = (base_unique / len(base_df)) * 100
        
        delta_unique = delta_df[col].nunique() if col in delta_df.columns else 0
        delta_unique_pct = (delta_unique / len(delta_df)) * 100 if len(delta_df) > 0 else 0
        
        print(f"  Column {i} ({col}):")
        print(f"    Base uniqueness: {base_unique}/{len(base_df)} ({base_unique_pct:.1f}%)")
        print(f"    Delta uniqueness: {delta_unique}/{len(delta_df)} ({delta_unique_pct:.1f}%)")
        
        if base_unique_pct > 95:
            print(f"    ✅ Good primary key candidate")
        elif base_unique_pct > 80:
            print(f"    ⚠️  Possible primary key candidate")
        else:
            print(f"    ❌ Poor primary key candidate")
    
    # Test different primary key options
    primary_key_options = [
        [0],           # First column only
        [0, 1],        # First two columns
        list(range(min(3, len(base_df.columns))))  # First three columns
    ]
    
    print(f"\nTesting primary key options:")
    
    for pk_option in primary_key_options:
        if max(pk_option) < len(base_df.columns):
            try:
                cdc = CSVCDC(primary_key=pk_option, progressbar=0)
                result = cdc.compare(base_file, delta_file)
                
                total_changes = len(result.additions) + len(result.modifications) + len(result.deletions)
                
                print(f"  Primary key {pk_option}: {total_changes} total changes")
                print(f"    Additions: {len(result.additions)}")
                print(f"    Modifications: {len(result.modifications)}")
                print(f"    Deletions: {len(result.deletions)}")
                
            except Exception as e:
                print(f"  Primary key {pk_option}: Error - {e}")
    
    # Test auto-detection
    print(f"\nTesting auto-detection:")
    try:
        cdc = CSVCDC(autopk=1, progressbar=0)
        result = cdc.compare(base_file, delta_file)
        
        print(f"  Auto-detected primary key: {cdc.primary_key}")
        total_changes = len(result.additions) + len(result.modifications) + len(result.deletions)
        print(f"  Total changes: {total_changes}")
        
    except Exception as e:
        print(f"  Auto-detection failed: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python debug_primary_key.py <base_file> <delta_file>")
        sys.exit(1)
    
    debug_primary_key_selection(sys.argv[1], sys.argv[2])
```

### Example 14: Memory Usage Optimization

**Script: `memory_optimizer.py`**
```python
#!/usr/bin/env python3
import gc
import psutil
import os
from csvcdc import CSVCDC

def memory_optimized_comparison(base_file, delta_file):
    """Perform memory-optimized comparison for large files"""
    
    def get_memory_usage():
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)  # MB
    
    print(f"Initial memory: {get_memory_usage():.1f} MB")
    
    # Configuration for memory optimization
    cdc = CSVCDC(
        progressbar=0,  # Reduce memory overhead
        autopk=0,       # Specify primary key to avoid detection overhead
        primary_key=[0]
    )
    
    print(f"After CDC creation: {get_memory_usage():.1f} MB")
    
    # Force garbage collection before comparison
    gc.collect()
    print(f"After garbage collection: {get_memory_usage():.1f} MB")
    
    # Perform comparison
    result = cdc.compare(base_file, delta_file)
    print(f"After comparison: {get_memory_usage():.1f} MB")
    
    # Process results in chunks to avoid memory spikes
    def process_results_in_chunks(items, chunk_size=1000):
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            # Process chunk
            yield chunk
    
    # Process additions in chunks
    addition_count = 0
    for chunk in process_results_in_chunks(result.additions):
        addition_count += len(chunk)
        # Process chunk here
    
    print(f"Processed {addition_count} additions")
    print(f"Final memory: {get_memory_usage():.1f} MB")
    
    return result

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python memory_optimizer.py <base_file> <delta_file>")
        sys.exit(1)
    
    result = memory_optimized_comparison(sys.argv[1], sys.argv[2])
```