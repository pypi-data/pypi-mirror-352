# FundamentalData

A Python package for institutional-grade SEC financial data analysis with integrated market context.

## Features ✨

- **SEC API Integration**: Direct EDGAR database access with automatic CIK resolution
- **Temporal Alignment**: Unified datetime indices across fundamental and market data
- **Advanced Normalization**: Built-in handling of XBRL discrepancies and reporting variants
- **Quant-Ready**: Pandas DataFrame outputs with NaN-aware preprocessing
- **Enterprise Features**: Type II rate limiting, configurable caching, and request retries

## Installation

```
pip install "fundamental_data"
```

## Import the package

```
from fundamental_data import FundamentalData
```

## Usage

### For single stock

```
fd = FundamentalData('myemail@email.com')

apple = fd.get_fundamentals('AAPL')
apple.QuarterlyTable #metrics organized according to quarters
apple.DatedTable #metric organized according to dates
apple.MetricStats #Statistics on the availability of metrics and related stats
apple.data #raw data
apple.CombinedTable #table combined with price data from yfinance
```

### For multiple stocks

```
fd = FundamentalData('myemail@email.com')
dataDict = fd.get_bulk_fundamentals([AAPL,TSLA])
dataDict['AAPL'].QuarterlyTable
```

### Visualizations

```
apple.visualize_data_availability()
apple.saveVisualizationTable('AAPL_vizz.xlsx')
```
