# Changelog

All notable changes to the MockFlow package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial PyPI publishing infrastructure
- Comprehensive CI/CD pipeline with GitHub Actions
- Enhanced documentation and examples

## [0.1.0] - 2024-08-20

### Added
- Initial release of MockFlow package
- Core financial time series generation functionality
- Market scenarios: bull, bear, sideways, and auto-selection
- Multiple timeframe support (15m to 1w)
- Seed-based reproducibility for consistent testing
- OHLCV data generation with realistic volume patterns
- Advanced volatility modeling with GARCH-like clustering
- Volume correlation with price movements
- Comprehensive test suite with 69 tests
- Full API contract validation
- Professional-grade documentation

### Features
- `generate_mock_data()` main API function
- Support for date ranges, custom limits, and scenarios
- Realistic market patterns and microstructure
- Type hints and comprehensive error handling
- Development tools integration (ruff, mypy, pytest)

### Documentation
- Complete README with installation and usage examples
- API contract specification
- Development setup and contribution guidelines
- Integration examples and performance testing

[Unreleased]: https://github.com/stefan-mcf/conflux-ml-engine/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/stefan-mcf/conflux-ml-engine/releases/tag/v0.1.0