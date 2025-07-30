# CSV CDC API Documentation

This document provides detailed information about the CSV CDC Python API.

## Table of Contents

- [Classes](#classes)
  - [CSVCDC](#csvcdc)
  - [CSVCDCResult](#csvcdcresult)
  - [OutputFormatter](#outputformatter)
- [Methods](#methods)
- [Examples](#examples)
- [Error Handling](#error-handling)

## Classes

### CSVCDC

The main class for performing CSV change data capture operations.

#### Constructor

```python
CSVCDC(separator=',', primary_key=None, columns=None, ignore_columns=None, 
       include_columns=None, progressbar=1, autopk=0)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `separator` | str | `','` | Field separator character |
| `primary_key` | List[int] | `[0]` | Column indices for primary key |
| `columns` | List[int] | `None` | Specific columns to compare |
| `ignore_columns` | List[int] | `None` | Columns to ignore in comparison |
| `include_columns` | List[int] | `None` | Columns to include in output |
| `progressbar` | int | `1` | Show progress bars (0 or 1) |
| `autopk` | int | `0` | Auto-detect primary key (0 or 1) |

**Example:**
```python
from csvcdc import CSVCDC

# Basic usage
cdc = CSVCDC()

# Advanced configuration
cdc = CSVCDC(
    separator='\t',
    primary_key=[0, 1],
    ignore_columns=[5, 6],
    progressbar=1,
    autopk=0
)
```

#### Methods

##### compare(base_file, delta_file)

Compare two CSV files and return differences.

**Parameters:**
- `base_file` (str): Path to the base CSV file
- `delta_file` (str): Path to the delta CSV file

**Returns:**
- `CSVCDCResult`: Object containing additions, modifications, and deletions

**Example:**
```python
cdc = CSVCDC(primary_key=[0])
result = cdc.compare('old_data.csv', 'new_data.csv')

print(f"Found {len(result.additions)} additions")
print(f"Found {len(result.modifications)} modifications")
print(f"Found {len(result.deletions)} deletions")
```

##### _detect_primary_key(base_df, delta_df, sample_size=100)

Automatically detect the best primary key columns.

**Parameters:**
- `base_df` (pl.DataFrame): Base dataframe
- `delta_df` (pl.DataFrame): Delta dataframe
- `sample_size` (int): Number of rows to sample for analysis

**Returns:**
- `List[int]`: List of column indices for the detected primary key

**Example:**
```python
cdc = CSVCDC(autopk=1)
# Primary key will be automatically detected during comparison
result = cdc.compare('file1.csv', 'file2.csv')
print(f"Detected primary key: {cdc.primary_key}")
```

### CSVCDCResult

Container class for storing comparison results.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `additions` | List[str] | List of added rows |
| `modifications` | List[Dict[str, str]] | List of modified rows with original and current values |
| `deletions` | List[str] | List of deleted rows |

**Example:**
```python
result = cdc.compare('base.csv', 'delta.csv')

# Access additions
for addition in result.additions:
    print(f"Added: {addition}")

# Access modifications
for mod in result.modifications:
    print(f"Original: {mod['Original']}")
    print(f"Current: {mod['Current']}")

# Access deletions
for deletion in result.deletions:
    print(f"Deleted: {deletion}")
```

### OutputFormatter

Static class for formatting output in different formats.

#### Methods

##### format_diff(result)

Format results in Git-style diff format with colors.

**Parameters:**
- `result` (CSVCDCResult): Comparison result

**Returns:**
- `str`: Formatted diff output

**Example:**
```python
from csvcdc import OutputFormatter

result = cdc.compare('base.csv', 'delta.csv')
diff_output = OutputFormatter.format_diff(result)
print(diff_output)
```

##### format_json(result)

Format results as JSON.

**Parameters:**
- `result` (CSVCDCResult): Comparison result

**Returns:**
- `str`: JSON formatted output

**Example:**
```python
json_output = OutputFormatter.format_json(result)
with open('changes.json', 'w') as f:
    f.write(json_output)
```

##### format_rowmark(result)

Format results in rowmark format.

**Parameters:**
- `result` (CSVCDCResult): Comparison result

**Returns:**
- `str`: Rowmark formatted output

**Example:**
```python
rowmark_output = OutputFormatter.format_rowmark(result)
print(rowmark_output)
```

##### format_word_diff(result)

Format results showing word-level differences.

**Parameters:**
- `result` (CSVCDCResult): Comparison result

**Returns:**
- `str`: Word diff formatted output

**Example:**
```python
word_diff_output = OutputFormatter.format_word_diff(result)
print(word_diff_output)
```

## Advanced Usage Examples

### Custom Processing Pipeline

```python
from csvcdc import CSVCDC, OutputFormatter
import json

class CustomCDCProcessor:
    def __init__(self, config):
        self.cdc = CSVCDC(**config)
        self.results_history = []
    
    def process_files(self, base_file, delta_file, output_file=None):
        """Process files and optionally save results"""
        result = self.cdc.compare(base_file, delta_file)
        
        # Custom analysis
        analysis = self._analyze_changes(result)
        
        # Store in history
        self.results_history.append({
            'base_file': base_file,
            'delta_file': delta_file,
            'timestamp': time.time(),
            'analysis': analysis
        })
        
        # Save if requested
        if output_file:
            self._save_results(result, analysis, output_file)
        
        return result, analysis
    
    def _analyze_changes(self, result):
        """Perform custom analysis on changes"""
        return {
            'total_changes': len(result.additions) + len(result.modifications) + len(result.deletions),
            'addition_rate': len(result.additions) / max(1, len(result.additions) + len(result.modifications) + len(result.deletions)),
            'modification_rate': len(result.modifications) / max(1, len(result.additions) + len(result.modifications) + len(result.deletions)),
            'deletion_rate': len(result.deletions) / max(1, len(result.additions) + len(result.modifications) + len(result.deletions))
        }
    
    def _save_results(self, result, analysis, output_file):
        """Save results in multiple formats"""
        base_name = output_file.rsplit('.', 1)[0]
        
        # Save JSON
        with open(f"{base_name}.json", 'w') as f:
            f.write(OutputFormatter.format_json(result))
        
        # Save diff
        with open(f"{base_name}.diff", 'w') as f:
            f.write(OutputFormatter.format_diff(result))
        
        # Save analysis
        with open(f"{base_name}_analysis.json", 'w') as f:
            json.dump(analysis, f, indent=2)

# Usage
processor = CustomCDCProcessor({
    'primary_key': [0],
    'autopk': 1,
    'progressbar': 1
})

result, analysis = processor.process_files('old.csv', 'new.csv', 'changes')
```

### Batch Processing

```python
import os
from pathlib import Path
from csvcdc import CSVCDC

def batch_compare_directory(base_dir, delta_dir, output_dir):
    """Compare all CSV files in two directories"""
    
    cdc = CSVCDC(autopk=1, progressbar=1)
    results = {}
    
    base_files = Path(base_dir).glob('*.csv')
    
    for base_file in base_files:
        delta_file = Path(delta_dir) / base_file.name
        
        if delta_file.exists():
            print(f"Comparing {base_file.name}...")
            
            try:
                result = cdc.compare(str(base_file), str(delta_file))
                results[base_file.name] = {
                    'additions': len(result.additions),
                    'modifications': len(result.modifications),
                    'deletions': len(result.deletions),
                    'success': True
                }
                
                # Save individual results
                output_file = Path(output_dir) / f"{base_file.stem}_changes.json"
                with open(output_file, 'w') as f:
                    f.write(OutputFormatter.format_json(result))
                    
            except Exception as e:
                results[base_file.name] = {
                    'error': str(e),
                    'success': False
                }
    
    # Save summary
    summary_file = Path(output_dir) / 'batch_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

# Usage
results = batch_compare_directory('data/old/', 'data/new/', 'output/')
```

### Streaming Large Files

```python
import tempfile
from csvcdc import CSVCDC

def compare_large_files_streaming(base_file, delta_file, chunk_size=10000):
    """Compare large files by processing in chunks"""
    
    # For very large files, you might want to implement
    # a streaming approach or use external sorting
    
    cdc = CSVCDC(
        progressbar=1,
        autopk=1  # Let it detect the best primary key
    )
    
    # Use temporary files for processing if needed
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_base, \
         tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_delta:
        
        # Pre-process files if needed (sorting, filtering, etc.)
        # This is where you could implement chunked processing
        
        result = cdc.compare(base_file, delta_file)
        
        # Clean up temporary files
        os.unlink(temp_base.name)
        os.unlink(temp_delta.name)
        
        return result
```

## Error Handling

### Common Exceptions

| Exception | Cause | Solution |
|-----------|-------|----------|
| `FileNotFoundError` | Input file doesn't exist | Check file paths |
| `PermissionError` | No read permission | Check file permissions |
| `ValueError` | Invalid column indices | Verify column indices exist |
| `MemoryError` | File too large for memory | Use streaming approach |
| `UnicodeDecodeError` | File encoding issues | Specify correct encoding |

### Best Practices

```python
from csvcdc import CSVCDC
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_compare(base_file, delta_file, **kwargs):
    """Safely compare files with proper error handling"""
    
    try:
        # Validate inputs
        if not os.path.exists(base_file):
            raise FileNotFoundError(f"Base file not found: {base_file}")
        
        if not os.path.exists(delta_file):
            raise FileNotFoundError(f"Delta file not found: {delta_file}")
        
        # Create CDC instance
        cdc = CSVCDC(**kwargs)
        
        # Perform comparison
        logger.info(f"Comparing {base_file} with {delta_file}")
        result = cdc.compare(base_file, delta_file)
        
        logger.info(f"Comparison completed: {len(result.additions)} additions, "
                   f"{len(result.modifications)} modifications, "
                   f"{len(result.deletions)} deletions")
        
        return result
        
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        raise
    
    except PermissionError as e:
        logger.error(f"Permission error: {e}")
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error during comparison: {e}")
        raise

# Usage with error handling
try:
    result = safe_compare('base.csv', 'delta.csv', autopk=1)
    print("Comparison successful!")
except Exception as e:
    print(f"Comparison failed: {e}")
```

## Performance Considerations

### Memory Usage

- The tool loads entire files into memory
- For very large files (>1GB), consider splitting them
- Use `progressbar=0` to reduce memory overhead slightly

### Speed Optimization

- Use `autopk=0` if you know the primary key (saves detection time)
- Use `progressbar=0` for faster processing in scripts
- Consider using SSD storage for large files

### Recommended Limits

| File Size | Recommended RAM | Processing Time (approx) |
|-----------|----------------|--------------------------|
| < 100MB | 4GB | < 10 seconds |
| 100MB - 500MB | 8GB | 10-60 seconds |
| 500MB - 1GB | 16GB | 1-5 minutes |
| > 1GB | 32GB+ | 5+ minutes |

```python
# Example: Monitor memory usage
import psutil
import os

def monitor_comparison(base_file, delta_file):
    """Compare files while monitoring resource usage"""
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    start_time = time.time()
    
    cdc = CSVCDC(progressbar=1)
    result = cdc.compare(base_file, delta_file)
    
    end_time = time.time()
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"Processing time: {end_time - start_time:.2f} seconds")
    print(f"Memory used: {final_memory - initial_memory:.2f} MB")
    print(f"Peak memory: {final_memory:.2f} MB")
    
    return result
```
```