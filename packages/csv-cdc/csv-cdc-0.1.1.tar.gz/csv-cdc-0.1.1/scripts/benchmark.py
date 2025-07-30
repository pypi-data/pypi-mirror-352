"""
Benchmark script for CSV CDC performance testing
"""

import time
import tempfile
import os
import csv
import psutil
import argparse
from pathlib import Path
import json

# Add parent directory to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from csvcdc import CSVCDC

def generate_test_data(rows, cols, output_file, change_rate=0.1):
    """Generate test CSV data"""
    print(f"Generating {rows} rows x {cols} columns -> {output_file}")
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        headers = ['id'] + [f'col_{i}' for i in range(1, cols)]
        writer.writerow(headers)
        
        # Data rows
        for i in range(rows):
            row = [i] + [f'value_{i}_{j}' for j in range(1, cols)]
            writer.writerow(row)

def generate_delta_data(base_file, delta_file, change_rate=0.1, addition_rate=0.05, deletion_rate=0.05):
    """Generate delta file with specified change rates"""
    print(f"Generating delta file with {change_rate*100}% changes")
    
    with open(base_file, 'r') as f_base, open(delta_file, 'w', newline='') as f_delta:
        reader = csv.reader(f_base)
        writer = csv.writer(f_delta)
        
        # Copy header
        headers = next(reader)
        writer.writerow(headers)
        
        rows = list(reader)
        total_rows = len(rows)
        
        # Determine which rows to change/delete
        import random
        random.seed(42)  # For reproducible results
        
        rows_to_change = set(random.sample(range(total_rows), int(total_rows * change_rate)))
        rows_to_delete = set(random.sample(range(total_rows), int(total_rows * deletion_rate)))
        
        # Write modified data
        for i, row in enumerate(rows):
            if i in rows_to_delete:
                continue  # Skip deleted rows
            
            if i in rows_to_change:
                # Modify the row
                row[1] = f"CHANGED_{row[1]}"  # Change second column
            
            writer.writerow(row)
        
        # Add new rows
        new_rows = int(total_rows * addition_rate)
        for i in range(new_rows):
            new_id = total_rows + i
            new_row = [new_id] + [f'new_value_{new_id}_{j}' for j in range(1, len(headers))]
            writer.writerow(new_row)

def measure_performance(base_file, delta_file, config):
    """Measure CDC performance"""
    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
    
    start_time = time.time()
    
    # Create CDC instance
    cdc = CSVCDC(**config)
    
    # Perform comparison
    result = cdc.compare(base_file, delta_file)
    
    end_time = time.time()
    final_memory = process.memory_info().rss / (1024 * 1024)  # MB
    
    # Calculate metrics
    base_size = os.path.getsize(base_file) / (1024 * 1024)  # MB
    delta_size = os.path.getsize(delta_file) / (1024 * 1024)  # MB
    total_size = base_size + delta_size
    
    execution_time = end_time - start_time
    memory_used = final_memory - initial_memory
    throughput = total_size / execution_time  # MB/s
    
    return {
        'execution_time': execution_time,
        'memory_used': memory_used,
        'peak_memory': final_memory,
        'throughput': throughput,
        'base_file_size': base_size,
        'delta_file_size': delta_size,
        'total_file_size': total_size,
        'additions': len(result.additions),
        'modifications': len(result.modifications),
        'deletions': len(result.deletions),
        'total_changes': len(result.additions) + len(result.modifications) + len(result.deletions)
    }

def run_benchmark_suite():
    """Run comprehensive benchmark suite"""
    
    # Test configurations
    test_configs = [
        {'rows': 1000, 'cols': 5, 'name': 'small'},
        {'rows': 10000, 'cols': 5, 'name': 'medium'},
        {'rows': 100000, 'cols': 5, 'name': 'large'},
        {'rows': 10000, 'cols': 20, 'name': 'wide'},
    ]
    
    cdc_configs = [
        {'primary_key': [0], 'progressbar': 0, 'autopk': 0, 'name': 'basic'},
        {'primary_key': [0], 'progressbar': 0, 'autopk': 1, 'name': 'autopk'},
        {'primary_key': [0, 1], 'progressbar': 0, 'autopk': 0, 'name': 'composite_pk'},
    ]
    
    results = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🧪 Running benchmark suite in {temp_dir}")
        
        for test_config in test_configs:
            print(f"\n📊 Testing {test_config['name']} dataset ({test_config['rows']} rows x {test_config['cols']} cols)")
            
            # Generate test files
            base_file = os.path.join(temp_dir, f"base_{test_config['name']}.csv")
            delta_file = os.path.join(temp_dir, f"delta_{test_config['name']}.csv")
            
            generate_test_data(test_config['rows'], test_config['cols'], base_file)
            generate_delta_data(base_file, delta_file)
            
            for cdc_config in cdc_configs:
                print(f"  🔧 Testing {cdc_config['name']} configuration...")
                
                # Extract config for CDC
                config = {k: v for k, v in cdc_config.items() if k != 'name'}
                
                try:
                    metrics = measure_performance(base_file, delta_file, config)
                    
                    result = {
                        'test_name': test_config['name'],
                        'cdc_config': cdc_config['name'],
                        'dataset': test_config,
                        'metrics': metrics
                    }
                    results.append(result)
                    
                    print(f"    ⏱️  Time: {metrics['execution_time']:.2f}s")
                    print(f"    💾 Memory: {metrics['memory_used']:.1f}MB")
                    print(f"    🚀 Throughput: {metrics['throughput']:.1f}MB/s")
                    print(f"    📝 Changes: {metrics['total_changes']}")
                    
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    result = {
                        'test_name': test_config['name'],
                        'cdc_config': cdc_config['name'],
                        'dataset': test_config,
                        'error': str(e)
                    }
                    results.append(result)
    
    return results

def generate_report(results, output_file):
    """Generate benchmark report"""
    
    # Save detailed results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate summary
    print(f"\n📋 Benchmark Results Summary")
    print("=" * 60)
    
    successful_results = [r for r in results if 'metrics' in r]
    
    if not successful_results:
        print("No successful benchmark runs")
        return
    
    # Group by test name
    by_test = {}
    for result in successful_results:
        test_name = result['test_name']
        if test_name not in by_test:
            by_test[test_name] = []
        by_test[test_name].append(result)
    
    # Print summary table
    print(f"{'Dataset':<12} {'Config':<12} {'Time(s)':<8} {'Memory(MB)':<12} {'Throughput(MB/s)':<15} {'Changes':<8}")
    print("-" * 75)
    
    for test_name, test_results in by_test.items():
        for result in test_results:
            metrics = result['metrics']
            print(f"{test_name:<12} {result['cdc_config']:<12} "
                  f"{metrics['execution_time']:<8.2f} {metrics['memory_used']:<12.1f} "
                  f"{metrics['throughput']:<15.1f} {metrics['total_changes']:<8}")
    
    # Performance insights
    print(f"\n🔍 Performance Insights:")
    
    # Best throughput
    best_throughput = max(successful_results, key=lambda x: x['metrics']['throughput'])
    print(f"Best throughput: {best_throughput['metrics']['throughput']:.1f} MB/s "
          f"({best_throughput['test_name']} - {best_throughput['cdc_config']})")
    
    # Most memory efficient
    best_memory = min(successful_results, key=lambda x: x['metrics']['memory_used'])
    print(f"Most memory efficient: {best_memory['metrics']['memory_used']:.1f} MB "
          f"({best_memory['test_name']} - {best_memory['cdc_config']})")
    
    # Fastest execution
    fastest = min(successful_results, key=lambda x: x['metrics']['execution_time'])
    print(f"Fastest execution: {fastest['metrics']['execution_time']:.2f}s "
          f"({fastest['test_name']} - {fastest['cdc_config']})")

def main():
    parser = argparse.ArgumentParser(description='CSV CDC Benchmark Tool')
    parser.add_argument('--output', '-o', default='benchmark_results.json',
                        help='Output file for detailed results')
    parser.add_argument('--custom', action='store_true',
                        help='Run custom benchmark with specific files')
    parser.add_argument('--base-file', help='Base CSV file for custom benchmark')
    parser.add_argument('--delta-file', help='Delta CSV file for custom benchmark')
    
    args = parser.parse_args()
    
    if args.custom:
        if not args.base_file or not args.delta_file:
            print("Error: --base-file and --delta-file required for custom benchmark")
            sys.exit(1)
        
        print(f"🔧 Running custom benchmark")
        print(f"Base file: {args.base_file}")
        print(f"Delta file: {args.delta_file}")
        
        config = {'primary_key': [0], 'progressbar': 1, 'autopk': 0}
        metrics = measure_performance(args.base_file, args.delta_file, config)
        
        print(f"\n📊 Results:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")
    
    else:
        print("🚀 Starting CSV CDC Benchmark Suite")
        results = run_benchmark_suite()
        generate_report(results, args.output)
        print(f"\n💾 Detailed results saved to: {args.output}")

if __name__ == '__main__':
    main()