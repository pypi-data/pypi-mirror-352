# CSV CDC (Change Data Capture) Tool

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/maurohkcba/csv-cdc)](https://github.com/maurohkcba/csv-cdc/issues)

A high-performance Change Data Capture (CDC) tool for comparing CSV files and detecting differences. Built with Python and optimized for speed using Polars, NumPy, and xxHash.

## 🚀 Features

- **Lightning Fast**: Uses Polars for CSV reading and xxHash for efficient comparisons
- **Large File Support**: Chunked processing for files of any size with memory optimization
- **Flexible Primary Keys**: Support for single or composite primary keys
- **Auto-Detection**: Automatically detect primary keys by analyzing data patterns
- **Multiple Output Formats**: diff, JSON, rowmark, and word-diff formats
- **Column Selection**: Include/exclude specific columns from comparison
- **Progress Tracking**: Built-in progress bars for large files
- **Memory Efficient**: Optimized for handling large CSV files with configurable chunk processing
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 📦 Installation

### From PyPI
```bash
pip install csv-cdc
csvcdc old_file.csv new_file.csv
```

### From Source
```bash
git clone https://github.com/maurohkcba/csv-cdc.git
cd csv-cdc
pip install -r requirements.txt
python setup.py install
```

### Development Installation
```bash
git clone https://github.com/maurohkcba/csv-cdc.git
cd csv-cdc
pip install -e .
```

## 🏃‍♂️ Quick Start

### Basic Usage

Compare two CSV files using the first column as primary key:

```bash
python csvcdc.py old_file.csv new_file.csv
```

### Large File Usage

For very large files that cause memory issues:

```bash
python csvcdc.py huge_file1.csv huge_file2.csv --largefiles 1
```

### Example Output
```diff
# Additions (2)
+ 4,New Product,99.99,Electronics
+ 5,Another Item,45.00,Books

# Modifications (1)
- 2,Laptop,999.99,Electronics
+ 2,Laptop,899.99,Electronics

# Deletions (1)
- 3,Old Product,25.99,Discontinued
```

## 📚 Detailed Examples

### 1. Basic File Comparison

Create sample files:

**base.csv**
```csv
id,name,price,category
1,Widget,10.99,Tools
2,Gadget,25.50,Electronics
3,Book,15.99,Education
```

**delta.csv**
```csv
id,name,price,category
1,Widget,12.99,Tools
2,Gadget,25.50,Electronics
4,Magazine,8.99,Education
```

Compare the files:
```bash
python csvcdc.py base.csv delta.csv --primary-key 0
```

Output:
```diff
# Additions (1)
+ 4,Magazine,8.99,Education

# Modifications (1)
- 1,Widget,10.99,Tools
+ 1,Widget,12.99,Tools

# Deletions (1)
- 3,Book,15.99,Education
```

### 2. Large File Processing

For files that are too large to fit in memory (multi-GB files):

```bash
# Enable large file mode with default chunk size (500,000 rows)
python csvcdc.py large_base.csv large_delta.csv --largefiles 1 --time

# Custom chunk size for very large files
python csvcdc.py huge_base.csv huge_delta.csv --largefiles 1 --chunk-size 100000

# Large file with JSON output
python csvcdc.py massive_file1.csv massive_file2.csv \
  --largefiles 1 \
  --chunk-size 250000 \
  --format json \
  --time > changes.json
```

### 3. Custom Primary Key

Use multiple columns as primary key:
```bash
python csvcdc.py base.csv delta.csv --primary-key 0,1
```

### 4. Auto-Detect Primary Key

Let the tool automatically detect the best primary key:
```bash
python csvcdc.py base.csv delta.csv --autopk 1
```

For large files with auto-detection:
```bash
python csvcdc.py large_base.csv large_delta.csv --autopk 1 --largefiles 1
```

### 5. Column Selection

Compare only specific columns:
```bash
# Compare only columns 0, 1, and 2
python csvcdc.py base.csv delta.csv --columns 0,1,2

# Ignore column 3 (category) from comparison
python csvcdc.py base.csv delta.csv --ignore-columns 3
```

### 6. Different Output Formats

**JSON Format:**
```bash
python csvcdc.py base.csv delta.csv --format json
```
```json
{
  "Additions": [
    "4,Magazine,8.99,Education"
  ],
  "Modifications": [
    {
      "Original": "1,Widget,10.99,Tools",
      "Current": "1,Widget,12.99,Tools"
    }
  ],
  "Deletions": [
    "3,Book,15.99,Education"
  ]
}
```

**Rowmark Format:**
```bash
python csvcdc.py base.csv delta.csv --format rowmark
```
```
ADDED,4,Magazine,8.99,Education
MODIFIED,1,Widget,12.99,Tools
```

**Word Diff Format:**
```bash
python csvcdc.py base.csv delta.csv --format word-diff
```

### 7. Custom Separators

For tab-separated files:
```bash
python csvcdc.py base.tsv delta.tsv --separator '\t'
```

For pipe-separated files:
```bash
python csvcdc.py base.csv delta.csv --separator '|'
```

### 8. Performance Monitoring

Track execution time and show progress:
```bash
python csvcdc.py large_base.csv large_delta.csv --time --progressbar 1
```

### 9. Large File Example

For files with millions of rows:
```bash
# Auto-detect primary key, show progress, time execution, large file mode
python csvcdc.py huge_base.csv huge_delta.csv \
  --autopk 1 \
  --progressbar 1 \
  --time \
  --largefiles 1 \
  --chunk-size 200000 \
  --format json > changes.json
```

### 10. Memory Error Scenarios

If you encounter memory allocation errors like:
```
Error: Unable to allocate 203. GiB for an array with shape (5196564, 42)
```

Use large file mode:
```bash
python csvcdc.py problematic_file1.csv problematic_file2.csv \
  --largefiles 1 \
  --chunk-size 50000 \
  --progressbar 1 \
  --time
```

## 🔧 Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `base_csv` | Base CSV file path | Required |
| `delta_csv` | Delta CSV file path | Required |
| `-p, --primary-key` | Primary key column positions (comma-separated) | `0` |
| `-s, --separator` | Field separator | `,` |
| `--columns` | Columns to compare (comma-separated) | All columns |
| `--ignore-columns` | Columns to ignore (comma-separated) | None |
| `--include` | Columns to include in output | All columns |
| `-o, --format` | Output format: diff, json, rowmark, word-diff | `diff` |
| `--time` | Show execution time | False |
| `--progressbar` | Show progress bar (0 or 1) | `1` |
| `--autopk` | Auto-detect primary key (0 or 1) | `0` |
| `--largefiles` | Enable large file optimization with chunked processing (0 or 1) | `0` |
| `--chunk-size` | Chunk size for large file processing | `500000` |
| `--version` | Show version | - |

## 📏 Large File Processing

### When to Use Large File Mode

Enable `--largefiles 1` when:
- Files are larger than available RAM
- You get memory allocation errors
- Files have millions of rows
- You want to minimize memory usage

### Chunk Size Guidelines

| File Size | Recommended Chunk Size | Memory Usage |
|-----------|------------------------|--------------|
| < 100MB | Default (no chunking) | Full file in RAM |
| 100MB - 1GB | 500,000 rows | ~500MB RAM |
| 1GB - 10GB | 200,000 rows | ~200MB RAM |
| > 10GB | 50,000 - 100,000 rows | ~50-100MB RAM |

### Large File Examples

```bash
# For 5GB+ files
python csvcdc.py massive1.csv massive2.csv --largefiles 1 --chunk-size 100000

# For extreme cases (50GB+ files)
python csvcdc.py extreme1.csv extreme2.csv --largefiles 1 --chunk-size 25000

# Balanced performance and memory
python csvcdc.py large1.csv large2.csv --largefiles 1 --chunk-size 250000
```

## 🐍 Python API Usage

### Basic API Usage

```python
from csvcdc import CSVCDC

# Create CDC instance
cdc = CSVCDC(separator=',', primary_key=[0])

# Compare files
result = cdc.compare('base.csv', 'delta.csv')

# Access results
print(f"Additions: {len(result.additions)}")
print(f"Modifications: {len(result.modifications)}")
print(f"Deletions: {len(result.deletions)}")

# Process individual changes
for addition in result.additions:
    print(f"Added: {addition}")

for modification in result.modifications:
    print(f"Changed from: {modification['Original']}")
    print(f"Changed to: {modification['Current']}")

for deletion in result.deletions:
    print(f"Deleted: {deletion}")
```

### Large File API Usage

```python
from csvcdc import CSVCDC

# Large file configuration
cdc = CSVCDC(
    separator=',',
    primary_key=[0],
    largefiles=1,  # Enable chunked processing
    chunk_size=100000,  # Process 100k rows at a time
    progressbar=1
)

# Compare large files
result = cdc.compare('huge_base.csv', 'huge_delta.csv')

# Process results normally
print(f"Found {len(result.additions)} additions")
print(f"Found {len(result.modifications)} modifications")
print(f"Found {len(result.deletions)} deletions")
```

### Advanced API Usage

```python
from csvcdc import CSVCDC, OutputFormatter

# Advanced configuration with large file support
cdc = CSVCDC(
    separator=',',
    primary_key=[0, 1],  # Composite primary key
    ignore_columns=[3, 4],  # Ignore columns 3 and 4
    progressbar=1,
    autopk=0,
    largefiles=1,  # Enable for large files
    chunk_size=200000  # Custom chunk size
)

# Compare files
result = cdc.compare('data/products_old.csv', 'data/products_new.csv')

# Use different formatters
diff_output = OutputFormatter.format_diff(result)
json_output = OutputFormatter.format_json(result)
rowmark_output = OutputFormatter.format_rowmark(result)

print("Diff format:")
print(diff_output)

# Save JSON output
with open('changes.json', 'w') as f:
    f.write(json_output)
```

### Custom Processing

```python
from csvcdc import CSVCDC
import json

def process_large_changes(base_file, delta_file):
    # Optimized for large files
    cdc = CSVCDC(
        autopk=1,  # Auto-detect primary key
        largefiles=1,  # Enable chunked processing
        chunk_size=150000,  # Custom chunk size
        progressbar=1
    )
    
    result = cdc.compare(base_file, delta_file)
    
    # Custom processing
    changes_summary = {
        'total_additions': len(result.additions),
        'total_modifications': len(result.modifications),
        'total_deletions': len(result.deletions),
        'change_rate': (len(result.additions) + len(result.modifications) + len(result.deletions)) / 100
    }
    
    # Process specific types of changes
    price_changes = []
    for mod in result.modifications:
        orig_parts = mod['Original'].split(',')
        curr_parts = mod['Current'].split(',')
        
        # Assuming price is in column 2
        if len(orig_parts) > 2 and len(curr_parts) > 2:
            try:
                old_price = float(orig_parts[2])
                new_price = float(curr_parts[2])
                if old_price != new_price:
                    price_changes.append({
                        'id': orig_parts[0],
                        'old_price': old_price,
                        'new_price': new_price,
                        'change': new_price - old_price
                    })
            except ValueError:
                pass
    
    changes_summary['price_changes'] = price_changes
    return changes_summary

# Usage
summary = process_large_changes('old_products.csv', 'new_products.csv')
print(json.dumps(summary, indent=2))
```

## 🔍 Auto Primary Key Detection

The auto primary key detection feature analyzes your data to find the best column(s) to use as primary key:

```python
# Enable auto-detection
cdc = CSVCDC(autopk=1)
result = cdc.compare('file1.csv', 'file2.csv')

# Auto-detection with large files
cdc = CSVCDC(autopk=1, largefiles=1)
result = cdc.compare('large_file1.csv', 'large_file2.csv')
```

The algorithm considers:
- **Uniqueness**: How unique values are in each column
- **Match Rate**: How well values match between files
- **Composite Keys**: Tests combinations of columns

### Example of Auto-Detection Output
```
Auto-detecting primary key...
Testing single columns: 100%|██████████| 5/5
Testing column combinations: 100%|███| 3/3
Auto-detected primary key: columns [0, 1] (score: 0.943)
```

## 📊 Performance Benchmarks

Performance comparison on different file sizes:

### Small Files (< 100MB)
| Tool | Time | Memory |
|------|------|--------|
| csv-cdc | 12.3s | 150MB |
| Traditional diff | 45.2s | 400MB |
| Manual Python | 38.7s | 320MB |

### Large Files (1GB+)
| Mode | File Size | Time | Peak Memory |
|------|-----------|------|-------------|
| Regular | 1GB | 45s | 2.1GB |
| Large File Mode | 1GB | 52s | 350MB |
| Large File Mode | 10GB | 8.5min | 450MB |
| Large File Mode | 50GB | 42min | 500MB |

### Optimization Features

1. **Polars Integration**: Ultra-fast CSV reading
2. **xxHash**: High-speed hashing algorithm
3. **Vectorized Operations**: NumPy-based processing
4. **Chunked Processing**: Memory-efficient large file handling
5. **Progressive Loading**: Streaming for huge files
6. **Garbage Collection**: Automatic memory cleanup between chunks

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=csvcdc tests/

# Test large file functionality
pytest tests/test_large_files.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
git clone https://github.com/maurohkcba/csv-cdc.git
cd csv-cdc
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Running Tests

```bash
pytest tests/
```

## 📜 License

This project is licensed under the MIT License [LICENCE](LICENCE)

## 🐛 Issues and Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/maurohkcba/csv-cdc/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/maurohkcba/csv-cdc/issues)
- 📖 **Documentation**: [Wiki](https://github.com/maurohkcba/csv-cdc/wiki)

## 🚀 Roadmap

- [x] Large file chunked processing
- [x] Memory optimization for huge datasets
- [ ] Support for Excel files
- [ ] Database output integration
- [ ] Web UI interface
- [ ] Docker containerization
- [ ] Cloud storage support (S3, GCS, Azure)
- [ ] Parallel processing for multi-core systems
- [ ] Configuration file support
- [ ] Scheduled comparison jobs

## ⭐ Star History

If you find this tool useful, please consider giving it a star!

## 📈 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.