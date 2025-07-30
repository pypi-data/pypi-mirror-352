# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.2] - 2025-06-04

### Fixed

- Fixed type handling for log_dir parameter in init_logger function
- Improved string to Path conversion for better compatibility

### Changed

- Updated GitHub Actions workflow to use uv instead of pip
- Enhanced CI/CD pipeline for automated testing and publishing

## [0.0.1] - 2025-06-04

### Added

- Initial release of Superyngo Logger
- Basic logging initialization with `init_logger()` function
- File rotation and management capabilities
- Log cleanup functionality with `clean_logs()` function
- Colored console output formatter
- Multiton pattern for logger instance management
- Support for custom configuration files
- Automatic log directory creation
- Timestamp-based log file naming
- MIT License

### Features

- Simple one-line logger initialization
- Automatic file rotation and cleanup
- Colored console output for better readability
- Flexible configuration options
- Python 3.8+ compatibility
- No external dependencies required

[Unreleased]: https://github.com/superyngo/my_logger/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/superyngo/my_logger/releases/tag/v0.0.1
