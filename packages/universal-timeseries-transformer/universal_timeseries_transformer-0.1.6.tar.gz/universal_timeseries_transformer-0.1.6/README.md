# Universal Timeseries Transformer

A Python package that provides a universal interface for transforming and manipulating time series data. This package offers flexible and efficient tools for handling various types of time series data transformations.

## Version Updates

### v0.1.6 (2025-06-01)
- Added timeseries_slicer module with date-based and index-based slicing functions
- Added timeseries_extender module with enhanced date extension functionality
- Improved .gitignore to exclude Jupyter notebook files

### v0.1.5 (2025-05-30)
- Added TimeseriesMatrix class for matrix representation of time series data
- Enhanced data access with row, column, and component selection methods
- Added format conversion methods (datetime, unixtime, string)

### v0.1.4 (2025-05-28)
- Added verbose option to control log output
- Enhanced timeseries extension functionality
- Improved code readability and documentation

### v0.1.3 (2025-05-19)
- Added new timeseries_application module with financial calculations
- Added functions for returns and cumulative returns calculation

### v0.1.2 (2025-05-19)
- Improved stability and performance optimization
- Enhanced type checking functionality
- Documentation improvements

## Features

- Index Transformer
  - Flexible time index manipulation
  - Date range operations
  - Frequency conversion
- DataFrame Transformer
  - Universal interface for time series operations
  - Data alignment and merging
  - Efficient data transformation
- Timeseries Basis
  - Core functionality for time series manipulation
  - Common time series operations

## Installation

You can install the package using pip:

```bash
pip install universal-timeseries-transformer
```

## Requirements

- Python >= 3.8
- Dependencies:
  - pandas
  - numpy

## Usage Examples

### 1. Basic Time Series Transformation

```python
from universal_timeseries_transformer import IndexTransformer, DataFrameTransformer
import pandas as pd

# Create sample time series data
df = pd.DataFrame({'value': [1, 2, 3, 4]},
                  index=pd.date_range('2025-01-01', periods=4))

# Transform time series index
index_transformer = IndexTransformer(df)
weekly_data = index_transformer.to_weekly()

# Apply data transformations
df_transformer = DataFrameTransformer(weekly_data)
result = df_transformer.rolling_mean(window=2)
```

### 2. Advanced Time Series Operations

```python
from universal_timeseries_transformer import TimeseriesBasis

# Initialize time series basis
ts_basis = TimeseriesBasis(df)

# Perform complex transformations
transformed_data = ts_basis.transform()
```
)

# Find funds with borrowings
funds_with_borrowings = search_funds_having_borrowings(date_ref='2025-02-21')

# Get borrowing details
fund_code = '100075'
borrowing_details = get_borriwings_by_fund(fund_code=fund_code, date_ref='2025-02-21')
```

### 3. Check Repo Agreements

```python
from financial_dataset_preprocessor import (
    search_funds_having_repos,
    get_repos_by_fund
)

# Find funds with repos
funds_with_repos = search_funds_having_repos(date_ref='2025-02-21')

# Get repo details for a specific fund
fund_code = '100075'
repo_details = get_repos_by_fund(fund_code=fund_code, date_ref='2025-02-21')
```

## Development

To set up the development environment:

1. Clone the repository
2. Create a virtual environment
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## License

This project is licensed under a proprietary license. All rights reserved.

### Terms of Use

- Source code viewing and forking is allowed
- Commercial use is prohibited without explicit permission
- Redistribution or modification of the code is prohibited
- Academic and research use is allowed with proper attribution

## Author

**June Young Park**  
AI Management Development Team Lead & Quant Strategist at LIFE Asset Management

LIFE Asset Management is a hedge fund management firm that integrates value investing and engagement strategies with quantitative approaches and financial technology, headquartered in Seoul, South Korea.

### Contact

- Email: juneyoungpaak@gmail.com
- Location: TWO IFC, Yeouido, Seoul
