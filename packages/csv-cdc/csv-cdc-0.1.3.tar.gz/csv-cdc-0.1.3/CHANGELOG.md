# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-06-03

### Added
- **Large File Support**: New `--largefiles` parameter for processing very large CSV files
  - Enables chunked processing to handle files that exceed available memory
  - Default value: 0 (disabled), set to 1 to enable
- **Chunk Size Control**: New `--chunk-size` parameter to control memory usage
  - Configurable chunk size for large file processing
  - Default value: 500,000 rows per chunk
  - Allows fine-tuning based on available system memory

### Enhanced
- **Memory Optimization**: Chunked processing prevents memory allocation errors on large datasets
- **Garbage Collection**: Automatic memory cleanup after each chunk processing
- **Auto Primary Key Detection**: Now works efficiently with large files using sample-based analysis
- **Progress Tracking**: Enhanced progress bars for chunked processing with per-chunk indicators

### Technical Improvements
- Low-memory mode integration with Polars library
- Fallback mechanisms for chunked vs. regular processing
- File size estimation for better memory planning
- Generator-based chunk reading for memory efficiency

## [1.0.0] - 2025-06-03

### Added
- Initial release of CSV CDC tool
- High-performance CSV comparison using Polars and xxHash
- Support for single and composite primary keys
- Auto primary key detection algorithm
- Multiple output formats (diff, JSON, rowmark, word-diff)
- Column selection and filtering options
- Progress bar support for large files
- Cross-platform colored output
- Comprehensive test suite
- Detailed documentation and examples

### Features
- **Performance**: Optimized for large CSV files using vectorized operations
- **Flexibility**: Support for custom separators and column configurations
- **Usability**: Intuitive command-line interface with helpful error messages
- **Extensibility**: Clean Python API for programmatic usage