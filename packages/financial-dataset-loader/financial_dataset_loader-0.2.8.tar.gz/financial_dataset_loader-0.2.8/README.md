# Financial Dataset Loader

A Python module for efficiently loading financial datasets from various sources including local storage and AWS S3. Designed for streamlined data management in quantitative finance applications.

## Version History

### v0.2.8 (2025-06-04)
- Updated path handling for improved file access
- Enhanced directory structure for dataset organization
- Standardized path management across local and S3 storage

## Features

- Multiple data source support:
  - AWS S3 storage (`dataset_loader_s3`)
  - Local filesystem (`dataset_loader_local`)
- Flexible data source configuration and path management
- Standardized file name formatting
- Configurable dataset loading parameters

## Project Structure

```
financial_dataset_loader/
├── data_source.py          # Data source configuration
├── dataset_loader_config.py # Loader configurations
├── dataset_loader_local.py  # Local filesystem loader
├── dataset_loader_s3.py     # AWS S3 loader
├── file_name_formatter.py   # File naming utilities
└── path_director.py         # Path management
```

## Installation

```bash
pip install financial-dataset-loader
```

## Usage

### Loading Financial Data

```python
from financial_dataset_loader import dataset_loader_s3

# Load menu snapshot data
df = dataset_loader_s3.load_menu2205_snapshot(date_ref='2025-02-12')

# Load specific fund data
df = dataset_loader_s3.load_menu2205(fund_code='000123', date_ref='2025-02-12')

# Load market data
df = dataset_loader_s3.load_market(market_name='KOSPI', date_ref='2025-02-12')

# Load index data
df = dataset_loader_s3.load_index(ticker_bbg_index='KOSPI Index')

# Load currency data
df = dataset_loader_s3.load_currency(ticker_bbg_currency='USDKRW Curncy')
```

### Available Loading Functions

- `load_menu2160(fund_code)`: Load timeseries data for menu 2160
- `load_menu2160_snapshot(date_ref)`: Load snapshot data for menu 2160
- `load_menu2205(fund_code, date_ref)`: Load fund-specific data for menu 2205
- `load_menu2205_snapshot(date_ref)`: Load snapshot data for menu 2205
- `load_menu8186_snapshot(date_ref)`: Load snapshot data for menu 8186
- `load_menu4165(fund_code, date_ref)`: Load period data for menu 4165
- `load_menu4165_snapshot(fund_code, date_ref)`: Load snapshot data for menu 4165
- `load_index(ticker_bbg_index)`: Load Bloomberg index data
- `load_currency(ticker_bbg_currency)`: Load Bloomberg currency data
- `load_market(market_name, date_ref)`: Load market data

## Requirements

- Python >= 3.11
- aws-s3-controller (for S3 functionality)
- string-date-controller (for date conversion functionality)
- shining_pebbles (for pseudo database functionality)

## License

MIT License

## Author

**June Young Park**  
AI Management Development Team Lead & Quant Strategist at LIFE Asset Management

LIFE Asset Management is a hedge fund management firm that integrates value investing and engagement strategies with quantitative approaches and financial technology, headquartered in Seoul, South Korea.

### Contact

- Email: juneyoungpaak@gmail.com
- Location: TWO IFC, Yeouido, Seoul
