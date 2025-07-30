# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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