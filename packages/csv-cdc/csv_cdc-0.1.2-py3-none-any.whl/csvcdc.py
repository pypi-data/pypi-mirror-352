import argparse
import sys
import json
import time
from typing import Dict, List, Tuple, Set, Any, Optional, Union
from collections import defaultdict
import csv
from io import StringIO

# High-performance libraries
import pandas as pd
import numpy as np
import xxhash
from colorama import init, Fore, Back, Style
import polars as pl
from tqdm import tqdm

# Initialize colorama for cross-platform colored output
init()

class CSVCDCResult:
    """Container for diff results"""
    def __init__(self):
        self.additions: List[str] = []
        self.modifications: List[Dict[str, str]] = []
        self.deletions: List[str] = []

class CSVCDC:
    """High-performance CSV CDC implementation"""
    
    def __init__(self, separator: str = ',', primary_key: List[int] = None, 
                 columns: List[int] = None, ignore_columns: List[int] = None,
                 include_columns: List[int] = None, progressbar: int = 1, autopk: int = 0):
        self.separator = separator if separator != '\\t' else '\t'
        self.primary_key = primary_key or [0]
        self.columns = columns
        self.ignore_columns = ignore_columns
        self.include_columns = include_columns
        self.progressbar = progressbar
        self.autopk = autopk
        
    def _read_csv_optimized(self, filepath: str) -> pl.DataFrame:
        """Read CSV using Polars for maximum performance"""
        try:
            # Use Polars for fastest CSV reading
            df = pl.read_csv(
                filepath,
                separator=self.separator,
                has_header=False,  # Treat all rows as data
                ignore_errors=True,
                low_memory=False
            )
            return df
        except Exception:
            # Fallback to pandas if Polars fails
            df_pandas = pd.read_csv(
                filepath, 
                sep=self.separator, 
                header=None, 
                dtype=str,
                na_filter=False,
                engine='c'  # Use C engine for speed
            )
            return pl.from_pandas(df_pandas)
    
    def _detect_primary_key(self, base_df: pl.DataFrame, delta_df: pl.DataFrame, sample_size: int = 100) -> List[int]:
        """Automatically detect primary key by analyzing column uniqueness and matching rates"""
        if self.progressbar:
            print("Auto-detecting primary key...", file=sys.stderr)
        
        base_sample_size = min(sample_size, len(base_df))
        delta_sample_size = min(sample_size, len(delta_df))
        
        # Sample data for analysis
        base_sample = base_df.head(base_sample_size).to_numpy().astype(str)
        delta_sample = delta_df.head(delta_sample_size).to_numpy().astype(str)
        
        total_columns = base_df.width
        best_pk = [0]  # default fallback
        best_score = 0
        
        # Test single columns first
        progress_iter = range(total_columns)
        if self.progressbar:
            progress_iter = tqdm(progress_iter, desc="Testing single columns", file=sys.stderr)
            
        for col_idx in progress_iter:
            if col_idx >= base_sample.shape[1] or col_idx >= delta_sample.shape[1]:
                continue
                
            # Check uniqueness in base sample
            base_values = set(base_sample[:, col_idx])
            base_uniqueness = len(base_values) / len(base_sample)
            
            # Check uniqueness in delta sample
            delta_values = set(delta_sample[:, col_idx])
            delta_uniqueness = len(delta_values) / len(delta_sample)
            
            # Check matching rate between files
            common_values = base_values.intersection(delta_values)
            match_rate = len(common_values) / max(len(base_values), len(delta_values))
            
            # Score calculation: favor high uniqueness and good match rate
            score = (base_uniqueness + delta_uniqueness) / 2 * 0.7 + match_rate * 0.3
            
            if score > best_score:
                best_score = score
                best_pk = [col_idx]
        
        # Test combination of first few columns if single column score is low
        if best_score < 0.8 and total_columns > 1:
            combinations_to_test = [
                [0, 1],
                [0, 1, 2] if total_columns > 2 else [0, 1],
                list(range(min(4, total_columns)))
            ]
            
            combo_progress = combinations_to_test
            if self.progressbar:
                combo_progress = tqdm(combinations_to_test, desc="Testing column combinations", file=sys.stderr)
            
            for combo in combo_progress:
                if any(col >= base_sample.shape[1] or col >= delta_sample.shape[1] for col in combo):
                    continue
                
                # Create composite keys
                base_composite = set()
                delta_composite = set()
                
                for row in base_sample:
                    key = self.separator.join([row[col] for col in combo])
                    base_composite.add(key)
                    
                for row in delta_sample:
                    key = self.separator.join([row[col] for col in combo])
                    delta_composite.add(key)
                
                base_uniqueness = len(base_composite) / len(base_sample)
                delta_uniqueness = len(delta_composite) / len(delta_sample)
                
                common_keys = base_composite.intersection(delta_composite)
                match_rate = len(common_keys) / max(len(base_composite), len(delta_composite))
                
                score = (base_uniqueness + delta_uniqueness) / 2 * 0.7 + match_rate * 0.3
                
                if score > best_score:
                    best_score = score
                    best_pk = combo
        
        if self.progressbar:
            print(f"Auto-detected primary key: columns {best_pk} (score: {best_score:.3f})", file=sys.stderr)
        
        return best_pk
    
    def _get_effective_columns(self, total_columns: int) -> List[int]:
        """Determine which columns to use for comparison"""
        if self.columns is not None:
            return self.columns
        elif self.ignore_columns is not None:
            return [i for i in range(total_columns) if i not in self.ignore_columns]
        else:
            return list(range(total_columns))
    
    def _create_hash_map(self, df: pl.DataFrame, desc: str = "Processing") -> Dict[int, Tuple[int, str]]:
        """Create optimized hash map using xxhash for speed"""
        hash_map = {}
        total_columns = df.width
        compare_columns = self._get_effective_columns(total_columns)
        
        # Convert to numpy for vectorized operations
        data = df.to_numpy().astype(str)
        
        # Setup progress bar
        progress_iter = range(len(data))
        if self.progressbar:
            progress_iter = tqdm(progress_iter, desc=desc, file=sys.stderr)
        
        for i in progress_iter:
            row = data[i]
            
            # Create primary key hash
            pk_values = [row[j] for j in self.primary_key if j < len(row)]
            pk_string = self.separator.join(pk_values)
            pk_hash = xxhash.xxh64(pk_string.encode('utf-8')).intdigest()
            
            # Create row hash for comparison columns
            compare_values = [row[j] for j in compare_columns if j < len(row)]
            row_string = self.separator.join(compare_values)
            row_hash = xxhash.xxh64(row_string.encode('utf-8')).intdigest()
            
            # Store full row string
            full_row = self.separator.join(row)
            hash_map[pk_hash] = (row_hash, full_row)
            
        return hash_map
    
    def compare(self, base_file: str, delta_file: str) -> CSVCDCResult:
        """Compare two CSV files and return differences"""
        # Read files with optimized method
        if self.progressbar:
            print("Reading base file...", file=sys.stderr)
        base_df = self._read_csv_optimized(base_file)
        
        if self.progressbar:
            print("Reading delta file...", file=sys.stderr)
        delta_df = self._read_csv_optimized(delta_file)
        
        # Auto-detect primary key if requested
        if self.autopk:
            self.primary_key = self._detect_primary_key(base_df, delta_df)
        
        # Create hash maps
        base_map = self._create_hash_map(base_df, "Processing base file")
        delta_map = self._create_hash_map(delta_df, "Processing delta file")
        
        result = CSVCDCResult()
        
        # Find additions and modifications
        if self.progressbar:
            print("Comparing files...", file=sys.stderr)
            
        delta_items = list(delta_map.items())
        progress_iter = delta_items
        if self.progressbar:
            progress_iter = tqdm(delta_items, desc="Finding additions/modifications", file=sys.stderr)
        
        for pk_hash, (delta_row_hash, delta_row) in progress_iter:
            if pk_hash not in base_map:
                # Addition: primary key doesn't exist in base
                result.additions.append(delta_row)
            else:
                base_row_hash, base_row = base_map[pk_hash]
                if base_row_hash != delta_row_hash:
                    # Modification: same primary key, different content
                    result.modifications.append({
                        'Original': base_row,
                        'Current': delta_row
                    })
        
        # Find deletions
        base_items = list(base_map.items())
        progress_iter = base_items
        if self.progressbar:
            progress_iter = tqdm(base_items, desc="Finding deletions", file=sys.stderr)
            
        for pk_hash, (base_row_hash, base_row) in progress_iter:
            if pk_hash not in delta_map:
                result.deletions.append(base_row)
        
        return result

class OutputFormatter:
    """Handle different output formats"""
    
    @staticmethod
    def format_diff(result: CSVCDCResult) -> str:
        """Git-style diff format with colors"""
        output = []
        
        if result.additions:
            output.append(f"{Fore.GREEN}# Additions ({len(result.additions)}){Style.RESET_ALL}")
            for addition in result.additions:
                output.append(f"{Fore.GREEN}+ {addition}{Style.RESET_ALL}")
        
        if result.modifications:
            output.append(f"{Fore.YELLOW}# Modifications ({len(result.modifications)}){Style.RESET_ALL}")
            for mod in result.modifications:
                output.append(f"{Fore.RED}- {mod['Original']}{Style.RESET_ALL}")
                output.append(f"{Fore.GREEN}+ {mod['Current']}{Style.RESET_ALL}")
        
        if result.deletions:
            output.append(f"{Fore.RED}# Deletions ({len(result.deletions)}){Style.RESET_ALL}")
            for deletion in result.deletions:
                output.append(f"{Fore.RED}- {deletion}{Style.RESET_ALL}")
        
        return '\n'.join(output)
    
    @staticmethod
    def format_json(result: CSVCDCResult) -> str:
        """JSON format"""
        return json.dumps({
            'Additions': result.additions,
            'Modifications': result.modifications,
            'Deletions': result.deletions
        }, indent=2)
    
    @staticmethod
    def format_rowmark(result: CSVCDCResult) -> str:
        """Rowmark format"""
        output = []
        for addition in result.additions:
            output.append(f"ADDED,{addition}")
        for mod in result.modifications:
            output.append(f"MODIFIED,{mod['Current']}")
        return '\n'.join(output)
    
    @staticmethod
    def format_word_diff(result: CSVCDCResult) -> str:
        """Word diff format"""
        output = []
        for mod in result.modifications:
            orig_parts = mod['Original'].split(',')
            curr_parts = mod['Current'].split(',')
            diff_parts = []
            
            max_len = max(len(orig_parts), len(curr_parts))
            for i in range(max_len):
                orig_val = orig_parts[i] if i < len(orig_parts) else ''
                curr_val = curr_parts[i] if i < len(curr_parts) else ''
                
                if orig_val != curr_val:
                    diff_parts.append(f"{Fore.RED}[-{orig_val}-]{Style.RESET_ALL}{Fore.GREEN}{{+{curr_val}+}}{Style.RESET_ALL}")
                else:
                    diff_parts.append(orig_val)
            
            output.append(','.join(diff_parts))
        
        return '\n'.join(output)

def parse_int_list(value: str) -> List[int]:
    """Parse comma-separated integers"""
    if not value:
        return []
    return [int(x.strip()) for x in value.split(',')]

def main():
    parser = argparse.ArgumentParser(
        description='A fast CDC tool for comparing CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('base_csv', help='Base CSV file')
    parser.add_argument('delta_csv', help='Delta CSV file')
    parser.add_argument('-p', '--primary-key', type=parse_int_list, default=[0],
                        help='Primary key positions as comma separated values (default: 0)')
    parser.add_argument('-s', '--separator', default=',',
                        help='Field separator (default: ,)')
    parser.add_argument('--columns', type=parse_int_list,
                        help='Selectively compare positions in CSV')
    parser.add_argument('--ignore-columns', type=parse_int_list,
                        help='Ignore these positions in CSV')
    parser.add_argument('--include', type=parse_int_list,
                        help='Include positions in CSV to display')
    parser.add_argument('-o', '--format', default='diff',
                        choices=['diff', 'json', 'legacy-json', 'rowmark', 'word-diff', 'color-words'],
                        help='Output format (default: diff)')
    parser.add_argument('--time', action='store_true',
                        help='Measure execution time')
    parser.add_argument('--progressbar', type=int, default=1, choices=[0, 1],
                        help='Show progress bar during processing (default: 1)')
    parser.add_argument('--autopk', type=int, default=0, choices=[0, 1],
                        help='Auto-detect primary key by analyzing data (default: 0)')
    parser.add_argument('--version', action='version', version='csvcdc-python 1.0.0')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.columns and args.ignore_columns:
        print("Error: --columns and --ignore-columns cannot be used together", file=sys.stderr)
        sys.exit(1)
    
    start_time = time.time() if args.time else None
    
    try:
        # Create CDC instance
        csvcdc = CSVCDC(
            separator=args.separator,
            primary_key=args.primary_key,
            columns=args.columns,
            ignore_columns=args.ignore_columns,
            include_columns=args.include,
            progressbar=args.progressbar,
            autopk=args.autopk
        )
        
        # Perform comparison
        result = csvcdc.compare(args.base_csv, args.delta_csv)
        
        # Format output
        if args.format == 'json' or args.format == 'legacy-json':
            output = OutputFormatter.format_json(result)
        elif args.format == 'rowmark':
            output = OutputFormatter.format_rowmark(result)
        elif args.format == 'word-diff' or args.format == 'color-words':
            output = OutputFormatter.format_word_diff(result)
        else:  # diff format
            output = OutputFormatter.format_diff(result)
        
        print(output)
        
        if args.time:
            elapsed = time.time() - start_time
            print(f"\nExecution time: {elapsed:.3f} seconds", file=sys.stderr)
        
        # Exit with appropriate code
        if result.additions or result.modifications or result.deletions:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    main()