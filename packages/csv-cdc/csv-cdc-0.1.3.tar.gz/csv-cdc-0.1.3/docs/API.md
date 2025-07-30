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
- [Large Files Processing](#large-files-processing)

## Classes

### CSVCDC

The main class for performing CSV change data capture operations.

#### Constructor

```python
CSVCDC(separator=',', primary_key=None, columns=None, ignore_columns=None, 
       include_columns=None, progressbar=1, autopk=0, largefiles=0, chunk_size=500000)
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
| `largefiles` | int | `0` | Enable large file optimization (0 or 1) |
| `chunk_size` | int | `500000` | Chunk size for large file processing |

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

# Large files configuration
cdc = CSVCDC(
    primary_key=[0],
    largefiles=1,
    chunk_size=250000,
    progressbar=1
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

##### _detect_primary_key(base_file, delta_file, sample_size=1000)

Automatically detect the best primary key columns.

**Parameters:**
- `base_file` (str): Path to base CSV file (for large files mode)
- `delta_file` (str): Path to delta CSV file (for large files mode)
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

## Large Files Processing

### Overview

The `largefiles` parameter enables memory-optimized processing for very large CSV files that cannot fit entirely in memory. When enabled, the tool processes files in configurable chunks, significantly reducing memory usage.

### When to Use Large Files Mode

| File Size | Memory Available | Recommended Mode | Settings |
|-----------|------------------|------------------|----------|
| < 500MB | Any | Standard (`largefiles=0`) | Default settings |
| 500MB - 2GB | 8GB+ | Standard or Large | Consider `largefiles=1` |
| 2GB - 10GB | Any | Large (`largefiles=1`) | `chunk_size=250000` |
| 10GB+ | Any | Large (`largefiles=1`) | `chunk_size=100000` or lower |

### Configuration Examples

```python
# For very large files (10GB+)
cdc = CSVCDC(
    primary_key=[0],
    largefiles=1,
    chunk_size=100000,
    progressbar=1
)

# For moderately large files (2-10GB)
cdc = CSVCDC(
    primary_key=[0],
    largefiles=1,
    chunk_size=250000,
    progressbar=1
)

# For huge files with limited memory
cdc = CSVCDC(
    primary_key=[0],
    largefiles=1,
    chunk_size=50000,
    progressbar=1
)
```

### Memory Usage Comparison

| Mode | 5GB File | 50GB File | 500GB File |
|------|----------|-----------|------------|
| Standard | ~25GB RAM | ~250GB RAM | Not feasible |
| Large (chunk_size=500000) | ~2GB RAM | ~2GB RAM | ~2GB RAM |
| Large (chunk_size=100000) | ~500MB RAM | ~500MB RAM | ~500MB RAM |

## Advanced Usage Examples

### Large File Processing

```python
from csvcdc import CSVCDC, OutputFormatter
import time
import psutil
import os

def process_large_files(base_file, delta_file, output_file=None):
    """Process very large CSV files with memory monitoring"""
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Configure for large files
    cdc = CSVCDC(
        primary_key=[0],
        largefiles=1,
        chunk_size=250000,  # Adjust based on available memory
        progressbar=1,
        autopk=0  # Disable for performance if PK is known
    )
    
    start_time = time.time()
    
    try:
        print(f"Processing large files...")
        print(f"Base file: {base_file}")
        print(f"Delta file: {delta_file}")
        print(f"Initial memory usage: {initial_memory:.2f} MB")
        
        result = cdc.compare(base_file, delta_file)
        
        end_time = time.time()
        final_memory = process.memory_info().rss / 1024 / 1024
        
        print(f"\nProcessing completed!")
        print(f"Time elapsed: {end_time - start_time:.2f} seconds")
        print(f"Peak memory usage: {final_memory:.2f} MB")
        print(f"Memory increase: {final_memory - initial_memory:.2f} MB")
        
        print(f"\nResults:")
        print(f"  Additions: {len(result.additions)}")
        print(f"  Modifications: {len(result.modifications)}")
        print(f"  Deletions: {len(result.deletions)}")
        
        # Save results if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(OutputFormatter.format_json(result))
            print(f"Results saved to: {output_file}")
        
        return result
        
    except MemoryError:
        print("Memory error encountered. Try reducing chunk_size.")
        raise
    except Exception as e:
        print(f"Error processing files: {e}")
        raise

# Usage
result = process_large_files(
    'huge_base_file.csv', 
    'huge_delta_file.csv', 
    'changes.json'
)
```

### Adaptive Chunk Size

```python
import os
from csvcdc import CSVCDC

def get_optimal_chunk_size(file_path, available_memory_gb=4):
    """Calculate optimal chunk size based on file size and available memory"""
    
    file_size_gb = os.path.getsize(file_path) / (1024**3)
    
    if file_size_gb < 0.5:
        return None  # Use standard mode
    elif file_size_gb < 2:
        return 500000
    elif file_size_gb < 10:
        return 250000
    elif file_size_gb < 50:
        return 100000
    else:
        # For very large files, calculate based on available memory
        return max(10000, int(available_memory_gb * 50000))

def adaptive_compare(base_file, delta_file):
    """Compare files with adaptive chunk sizing"""
    
    # Determine optimal settings
    base_size = os.path.getsize(base_file) / (1024**3)  # GB
    delta_size = os.path.getsize(delta_file) / (1024**3)  # GB
    max_size = max(base_size, delta_size)
    
    chunk_size = get_optimal_chunk_size(base_file if base_size > delta_size else delta_file)
    use_large_mode = chunk_size is not None
    
    print(f"File sizes: Base={base_size:.2f}GB, Delta={delta_size:.2f}GB")
    print(f"Using {'large file' if use_large_mode else 'standard'} mode")
    if use_large_mode:
        print(f"Chunk size: {chunk_size:,} rows")
    
    # Configure CDC
    config = {
        'primary_key': [0],
        'progressbar': 1,
        'autopk': 0
    }
    
    if use_large_mode:
        config.update({
            'largefiles': 1,
            'chunk_size': chunk_size
        })
    
    cdc = CSVCDC(**config)
    return cdc.compare(base_file, delta_file)

# Usage
result = adaptive_compare('file1.csv', 'file2.csv')
```

### Custom Processing Pipeline

```python
from csvcdc import CSVCDC, OutputFormatter
import json

class LargeFileCDCProcessor:
    def __init__(self, config):
        self.cdc = CSVCDC(**config)
        self.results_history = []
    
    def process_files(self, base_file, delta_file, output_file=None):
        """Process files optimized for large datasets"""
        
        # Get file info
        base_size = os.path.getsize(base_file) / (1024**3)
        delta_size = os.path.getsize(delta_file) / (1024**3)
        
        print(f"Processing files: {base_size:.2f}GB + {delta_size:.2f}GB")
        
        # Perform comparison
        start_time = time.time()
        result = self.cdc.compare(base_file, delta_file)
        end_time = time.time()
        
        # Custom analysis
        analysis = self._analyze_changes(result, end_time - start_time, base_size + delta_size)
        
        # Store in history
        self.results_history.append({
            'base_file': base_file,
            'delta_file': delta_file,
            'timestamp': time.time(),
            'analysis': analysis,
            'file_sizes_gb': {'base': base_size, 'delta': delta_size},
            'processing_time': end_time - start_time
        })
        
        # Save if requested
        if output_file:
            self._save_results(result, analysis, output_file)
        
        return result, analysis
    
    def _analyze_changes(self, result, processing_time, total_size_gb):
        """Perform custom analysis on changes"""
        total_changes = len(result.additions) + len(result.modifications) + len(result.deletions)
        
        return {
            'total_changes': total_changes,
            'addition_rate': len(result.additions) / max(1, total_changes),
            'modification_rate': len(result.modifications) / max(1, total_changes),
            'deletion_rate': len(result.deletions) / max(1, total_changes),
            'processing_time_seconds': processing_time,
            'processing_rate_gb_per_minute': (total_size_gb / processing_time) * 60 if processing_time > 0 else 0,
            'changes_per_gb': total_changes / max(0.001, total_size_gb)
        }
    
    def _save_results(self, result, analysis, output_file):
        """Save results in multiple formats"""
        base_name = output_file.rsplit('.', 1)[0]
        
        # Save JSON
        with open(f"{base_name}.json", 'w') as f:
            f.write(OutputFormatter.format_json(result))
        
        # Save analysis
        with open(f"{base_name}_analysis.json", 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Save summary
        summary = {
            'file_info': f"Processed {analysis.get('processing_time_seconds', 0):.1f}s",
            'changes_summary': f"{len(result.additions)}A/{len(result.modifications)}M/{len(result.deletions)}D",
            'performance': f"{analysis.get('processing_rate_gb_per_minute', 0):.2f} GB/min"
        }
        
        with open(f"{base_name}_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

# Usage for large files
processor = LargeFileCDCProcessor({
    'primary_key': [0],
    'largefiles': 1,
    'chunk_size': 250000,
    'progressbar': 1,
    'autopk': 0
})

result, analysis = processor.process_files('huge_old.csv', 'huge_new.csv', 'changes')
print(f"Processing rate: {analysis['processing_rate_gb_per_minute']:.2f} GB/min")
```

## Error Handling

### Common Exceptions

| Exception | Cause | Solution |
|-----------|-------|----------|
| `FileNotFoundError` | Input file doesn't exist | Check file paths |
| `PermissionError` | No read permission | Check file permissions |
| `ValueError` | Invalid column indices | Verify column indices exist |
| `MemoryError` | File too large for memory | Enable `largefiles=1` or reduce `chunk_size` |
| `UnicodeDecodeError` | File encoding issues | Specify correct encoding |

### Best Practices for Large Files

```python
from csvcdc import CSVCDC
import logging
import psutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_large_file_compare(base_file, delta_file, **kwargs):
    """Safely compare large files with proper error handling and memory monitoring"""
    
    # Check available memory
    available_memory_gb = psutil.virtual_memory().available / (1024**3)
    logger.info(f"Available memory: {available_memory_gb:.2f} GB")
    
    # Get file sizes
    base_size_gb = os.path.getsize(base_file) / (1024**3)
    delta_size_gb = os.path.getsize(delta_file) / (1024**3)
    total_size_gb = base_size_gb + delta_size_gb
    
    logger.info(f"File sizes: Base={base_size_gb:.2f}GB, Delta={delta_size_gb:.2f}GB")
    
    # Determine if large file mode is needed
    if total_size_gb > available_memory_gb * 0.5:  # Use large mode if files are > 50% of available memory
        logger.info("Enabling large file mode due to memory constraints")
        kwargs.setdefault('largefiles', 1)
        
        # Adjust chunk size based on available memory
        suggested_chunk_size = max(10000, int(available_memory_gb * 50000))
        kwargs.setdefault('chunk_size', suggested_chunk_size)
        logger.info(f"Using chunk size: {kwargs['chunk_size']:,}")
    
    try:
        # Validate inputs
        if not os.path.exists(base_file):
            raise FileNotFoundError(f"Base file not found: {base_file}")
        
        if not os.path.exists(delta_file):
            raise FileNotFoundError(f"Delta file not found: {delta_file}")
        
        # Create CDC instance
        cdc = CSVCDC(**kwargs)
        
        # Monitor memory during processing
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024**2)  # MB
        
        # Perform comparison
        logger.info(f"Starting comparison (initial memory: {initial_memory:.1f} MB)")
        result = cdc.compare(base_file, delta_file)
        
        final_memory = process.memory_info().rss / (1024**2)  # MB
        logger.info(f"Comparison completed (final memory: {final_memory:.1f} MB, "
                   f"increase: {final_memory - initial_memory:.1f} MB)")
        
        logger.info(f"Results: {len(result.additions)} additions, "
                   f"{len(result.modifications)} modifications, "
                   f"{len(result.deletions)} deletions")
        
        return result
        
    except MemoryError as e:
        logger.error(f"Memory error: {e}. Try enabling largefiles=1 or reducing chunk_size")
        raise
    
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error during comparison: {e}")
        raise

# Usage with automatic large file handling
try:
    result = safe_large_file_compare(
        'huge_base.csv', 
        'huge_delta.csv', 
        primary_key=[0],
        progressbar=1
    )
    print("Comparison successful!")
except Exception as e:
    print(f"Comparison failed: {e}")
```

## Performance Considerations

### Memory Usage

| Mode | Small Files (<500MB) | Large Files (>2GB) | Huge Files (>50GB) |
|------|---------------------|-------------------|-------------------|
| Standard | Efficient | May cause memory issues | Not recommended |
| Large Files | Slight overhead | Recommended | Required |

### Speed vs Memory Trade-offs

| Chunk Size | Memory Usage | Processing Speed | Best For |
|------------|--------------|------------------|----------|
| 1,000,000+ | High | Fastest | Small-medium files |
| 500,000 | Medium-High | Fast | Medium-large files |
| 250,000 | Medium | Good | Large files |
| 100,000 | Low | Slower | Very large files |
| 50,000 | Very Low | Slowest | Huge files with limited memory |

### Recommended Settings by Use Case

```python
# Development/Testing (speed priority)
cdc = CSVCDC(largefiles=0, progressbar=1)

# Production small files (efficiency)
cdc = CSVCDC(largefiles=0, progressbar=0, autopk=0)

# Production large files (memory optimization)
cdc = CSVCDC(largefiles=1, chunk_size=250000, progressbar=1, autopk=0)

# Extreme large files (maximum memory efficiency)
cdc = CSVCDC(largefiles=1, chunk_size=50000, progressbar=1, autopk=0)

# Balanced approach (automatic adaptation)
def create_adaptive_cdc(base_file, delta_file):
    total_size = os.path.getsize(base_file) + os.path.getsize(delta_file)
    size_gb = total_size / (1024**3)
    
    if size_gb < 1:
        return CSVCDC(progressbar=1)
    elif size_gb < 10:
        return CSVCDC(largefiles=1, chunk_size=250000, progressbar=1)
    else:
        return CSVCDC(largefiles=1, chunk_size=100000, progressbar=1)
```
