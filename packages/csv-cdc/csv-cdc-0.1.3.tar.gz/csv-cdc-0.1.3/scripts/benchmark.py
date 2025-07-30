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

def get_file_size_mb(filepath):
    """Get file size in MB"""
    return os.path.getsize(filepath) / (1024 * 1024)

def should_use_large_files(base_file, delta_file, threshold_mb=100):
    """Determine if large file mode should be used based on file sizes"""
    total_size = get_file_size_mb(base_file) + get_file_size_mb(delta_file)
    return total_size > threshold_mb

def measure_performance(base_file, delta_file, config):
    """Measure CDC performance"""
    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
    peak_memory = initial_memory
    
    # Monitor memory usage during execution
    def monitor_memory():
        nonlocal peak_memory
        current_memory = process.memory_info().rss / (1024 * 1024)
        peak_memory = max(peak_memory, current_memory)
    
    start_time = time.time()
    
    # Create CDC instance
    cdc = CSVCDC(**config)
    monitor_memory()
    
    # Perform comparison
    result = cdc.compare(base_file, delta_file)
    monitor_memory()
    
    end_time = time.time()
    final_memory = process.memory_info().rss / (1024 * 1024)  # MB
    
    # Calculate metrics
    base_size = get_file_size_mb(base_file)
    delta_size = get_file_size_mb(delta_file)
    total_size = base_size + delta_size
    
    execution_time = end_time - start_time
    memory_used = final_memory - initial_memory
    throughput = total_size / execution_time if execution_time > 0 else 0
    
    return {
        'execution_time': execution_time,
        'memory_used': memory_used,
        'peak_memory': peak_memory,
        'throughput': throughput,
        'base_file_size': base_size,
        'delta_file_size': delta_size,
        'total_file_size': total_size,
        'additions': len(result.additions),
        'modifications': len(result.modifications),
        'deletions': len(result.deletions),
        'total_changes': len(result.additions) + len(result.modifications) + len(result.deletions),
        'large_files_mode': config.get('largefiles', 0),
        'chunk_size': config.get('chunk_size', 500000)
    }

def run_benchmark_suite():
    """Run comprehensive benchmark suite"""
    
    # Test configurations - expanded to include large file tests
    test_configs = [
        {'rows': 1000, 'cols': 5, 'name': 'small'},
        {'rows': 10000, 'cols': 5, 'name': 'medium'},
        {'rows': 100000, 'cols': 5, 'name': 'large'},
        {'rows': 500000, 'cols': 5, 'name': 'very_large'},
        {'rows': 10000, 'cols': 20, 'name': 'wide'},
        {'rows': 50000, 'cols': 20, 'name': 'large_wide'},
    ]
    
    # CDC configurations - now includes large file options
    cdc_configs = [
        {'primary_key': [0], 'progressbar': 0, 'autopk': 0, 'largefiles': 0, 'name': 'basic'},
        {'primary_key': [0], 'progressbar': 0, 'autopk': 1, 'largefiles': 0, 'name': 'autopk'},
        {'primary_key': [0, 1], 'progressbar': 0, 'autopk': 0, 'largefiles': 0, 'name': 'composite_pk'},
        {'primary_key': [0], 'progressbar': 0, 'autopk': 0, 'largefiles': 1, 'chunk_size': 100000, 'name': 'large_files_100k'},
        {'primary_key': [0], 'progressbar': 0, 'autopk': 0, 'largefiles': 1, 'chunk_size': 500000, 'name': 'large_files_500k'},
        {'primary_key': [0], 'progressbar': 0, 'autopk': 1, 'largefiles': 1, 'chunk_size': 500000, 'name': 'large_files_autopk'},
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
            
            # Check file sizes
            total_size_mb = get_file_size_mb(base_file) + get_file_size_mb(delta_file)
            print(f"    📁 Total file size: {total_size_mb:.1f} MB")
            
            # Determine which configs to test based on dataset size
            configs_to_test = cdc_configs.copy()
            
            # For small datasets, skip large file configs
            if total_size_mb < 50:
                configs_to_test = [c for c in configs_to_test if c.get('largefiles', 0) == 0]
                print(f"    ℹ️  Skipping large file configs for small dataset")
            
            # For very large datasets, prioritize large file configs
            elif total_size_mb > 200:
                print(f"    ⚡ Large dataset detected, testing both modes")
            
            for cdc_config in configs_to_test:
                print(f"  🔧 Testing {cdc_config['name']} configuration...")
                
                # Extract config for CDC
                config = {k: v for k, v in cdc_config.items() if k != 'name'}
                
                try:
                    # Add timeout for very long operations
                    import signal
                    
                    def timeout_handler(signum, frame):
                        raise TimeoutError("Benchmark timed out after 300 seconds")
                    
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(300)  # 5 minute timeout
                    
                    metrics = measure_performance(base_file, delta_file, config)
                    
                    signal.alarm(0)  # Cancel timeout
                    
                    result = {
                        'test_name': test_config['name'],
                        'cdc_config': cdc_config['name'],
                        'dataset': test_config,
                        'metrics': metrics
                    }
                    results.append(result)
                    
                    print(f"    ⏱️  Time: {metrics['execution_time']:.2f}s")
                    print(f"    💾 Memory: {metrics['memory_used']:.1f}MB (Peak: {metrics['peak_memory']:.1f}MB)")
                    print(f"    🚀 Throughput: {metrics['throughput']:.1f}MB/s")
                    print(f"    📝 Changes: {metrics['total_changes']}")
                    if metrics['large_files_mode']:
                        print(f"    📦 Chunk size: {metrics['chunk_size']:,}")
                    
                except TimeoutError as e:
                    print(f"    ⏰ Timeout: {e}")
                    result = {
                        'test_name': test_config['name'],
                        'cdc_config': cdc_config['name'],
                        'dataset': test_config,
                        'error': 'timeout'
                    }
                    results.append(result)
                    
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    result = {
                        'test_name': test_config['name'],
                        'cdc_config': cdc_config['name'],
                        'dataset': test_config,
                        'error': str(e)
                    }
                    results.append(result)
                
                finally:
                    try:
                        signal.alarm(0)  # Ensure timeout is cancelled
                    except:
                        pass
    
    return results

def generate_report(results, output_file):
    """Generate benchmark report"""
    
    # Save detailed results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate summary
    print(f"\n📋 Benchmark Results Summary")
    print("=" * 80)
    
    successful_results = [r for r in results if 'metrics' in r]
    failed_results = [r for r in results if 'error' in r]
    
    if failed_results:
        print(f"\n⚠️  {len(failed_results)} failed benchmark(s):")
        for result in failed_results:
            print(f"  - {result['test_name']} / {result['cdc_config']}: {result['error']}")
    
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
    print(f"\n{'Dataset':<15} {'Config':<20} {'Time(s)':<8} {'Memory(MB)':<12} {'Peak(MB)':<10} {'Throughput':<12} {'Changes':<8} {'Mode':<6}")
    print("-" * 100)
    
    for test_name, test_results in by_test.items():
        for result in test_results:
            metrics = result['metrics']
            mode = "Chunk" if metrics['large_files_mode'] else "Normal"
            print(f"{test_name:<15} {result['cdc_config']:<20} "
                  f"{metrics['execution_time']:<8.2f} {metrics['memory_used']:<12.1f} "
                  f"{metrics['peak_memory']:<10.1f} {metrics['throughput']:<12.1f} "
                  f"{metrics['total_changes']:<8} {mode:<6}")
    
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
    
    # Lowest peak memory
    best_peak_memory = min(successful_results, key=lambda x: x['metrics']['peak_memory'])
    print(f"Lowest peak memory: {best_peak_memory['metrics']['peak_memory']:.1f} MB "
          f"({best_peak_memory['test_name']} - {best_peak_memory['cdc_config']})")
    
    # Fastest execution
    fastest = min(successful_results, key=lambda x: x['metrics']['execution_time'])
    print(f"Fastest execution: {fastest['metrics']['execution_time']:.2f}s "
          f"({fastest['test_name']} - {fastest['cdc_config']})")
    
    # Large files vs normal mode comparison
    large_file_results = [r for r in successful_results if r['metrics']['large_files_mode']]
    normal_results = [r for r in successful_results if not r['metrics']['large_files_mode']]
    
    if large_file_results and normal_results:
        print(f"\n📊 Mode Comparison:")
        avg_memory_normal = sum(r['metrics']['peak_memory'] for r in normal_results) / len(normal_results)
        avg_memory_large = sum(r['metrics']['peak_memory'] for r in large_file_results) / len(large_file_results)
        print(f"Average peak memory - Normal: {avg_memory_normal:.1f}MB, Chunked: {avg_memory_large:.1f}MB")
        
        avg_throughput_normal = sum(r['metrics']['throughput'] for r in normal_results) / len(normal_results)
        avg_throughput_large = sum(r['metrics']['throughput'] for r in large_file_results) / len(large_file_results)
        print(f"Average throughput - Normal: {avg_throughput_normal:.1f}MB/s, Chunked: {avg_throughput_large:.1f}MB/s")

def main():
    parser = argparse.ArgumentParser(description='CSV CDC Benchmark Tool')
    parser.add_argument('--output', '-o', default='benchmark_results.json',
                        help='Output file for detailed results')
    parser.add_argument('--custom', action='store_true',
                        help='Run custom benchmark with specific files')
    parser.add_argument('--base-file', help='Base CSV file for custom benchmark')
    parser.add_argument('--delta-file', help='Delta CSV file for custom benchmark')
    parser.add_argument('--largefiles', type=int, default=None, choices=[0, 1],
                        help='Force large files mode (auto-detect if not specified)')
    parser.add_argument('--chunk-size', type=int, default=500000,
                        help='Chunk size for large file processing')
    parser.add_argument('--compare-modes', action='store_true',
                        help='Compare both normal and large file modes')
    
    args = parser.parse_args()
    
    if args.custom:
        if not args.base_file or not args.delta_file:
            print("Error: --base-file and --delta-file required for custom benchmark")
            sys.exit(1)
        
        print(f"🔧 Running custom benchmark")
        print(f"Base file: {args.base_file}")
        print(f"Delta file: {args.delta_file}")
        
        base_size = get_file_size_mb(args.base_file)
        delta_size = get_file_size_mb(args.delta_file)
        total_size = base_size + delta_size
        
        print(f"File sizes: Base={base_size:.1f}MB, Delta={delta_size:.1f}MB, Total={total_size:.1f}MB")
        
        # Determine large files mode
        if args.largefiles is None:
            use_large_files = should_use_large_files(args.base_file, args.delta_file)
            print(f"Auto-detected large files mode: {use_large_files}")
        else:
            use_large_files = bool(args.largefiles)
            print(f"Forced large files mode: {use_large_files}")
        
        configs_to_test = []
        
        if args.compare_modes:
            # Test both modes
            configs_to_test = [
                {'primary_key': [0], 'progressbar': 1, 'autopk': 0, 'largefiles': 0, 'name': 'normal_mode'},
                {'primary_key': [0], 'progressbar': 1, 'autopk': 0, 'largefiles': 1, 'chunk_size': args.chunk_size, 'name': 'chunked_mode'}
            ]
        else:
            # Test single mode
            config = {
                'primary_key': [0], 
                'progressbar': 1, 
                'autopk': 0, 
                'largefiles': 1 if use_large_files else 0,
                'name': 'chunked_mode' if use_large_files else 'normal_mode'
            }
            if use_large_files:
                config['chunk_size'] = args.chunk_size
            configs_to_test = [config]
        
        print(f"\n📊 Results:")
        for config in configs_to_test:
            print(f"\n🔧 Testing {config['name']}...")
            test_config = {k: v for k, v in config.items() if k != 'name'}
            
            try:
                metrics = measure_performance(args.base_file, args.delta_file, test_config)
                
                print(f"  ⏱️  Execution time: {metrics['execution_time']:.2f}s")
                print(f"  💾 Memory used: {metrics['memory_used']:.1f}MB")
                print(f"  📈 Peak memory: {metrics['peak_memory']:.1f}MB") 
                print(f"  🚀 Throughput: {metrics['throughput']:.1f}MB/s")
                print(f"  📝 Total changes: {metrics['total_changes']}")
                print(f"    - Additions: {metrics['additions']}")
                print(f"    - Modifications: {metrics['modifications']}")
                print(f"    - Deletions: {metrics['deletions']}")
                if metrics['large_files_mode']:
                    print(f"  📦 Chunk size: {metrics['chunk_size']:,}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    else:
        print("🚀 Starting CSV CDC Benchmark Suite")
        results = run_benchmark_suite()
        generate_report(results, args.output)
        print(f"\n💾 Detailed results saved to: {args.output}")

if __name__ == '__main__':
    main()