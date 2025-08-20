# MockFlow API Reference

Complete API documentation for the MockFlow package.

## Core Module (`mockflow.core`)

### `generate_mock_data()`

The main function for generating financial time series mock data.

```python
def generate_mock_data(
    symbol: str,
    timeframe: str,
    days: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: Optional[int] = None,
    scenario: str = "auto"
) -> pd.DataFrame
```

#### Parameters

**`symbol`** *(str)*
- Trading pair symbol identifier
- Examples: `"BTCUSDT"`, `"ETHUSD"`, `"AAPL"`, `"EURUSD"`
- Case-insensitive, but uppercase recommended
- Used for scenario auto-selection logic

**`timeframe`** *(str)*
- Candle/bar timeframe for data generation
- Supported values:
  - Minutes: `"1m"`, `"5m"`, `"15m"`, `"30m"`
  - Hours: `"1h"`, `"2h"`, `"4h"`, `"6h"`, `"8h"`, `"12h"`
  - Days: `"1d"`, `"3d"`
  - Weeks: `"1w"`
- Case-insensitive
- Affects generation patterns and realistic characteristics

**`days`** *(int, optional)*
- Number of days of data to generate
- Mutually exclusive with `start_date`/`end_date` and `limit`
- Must be positive integer
- Calculates actual candle count based on timeframe
- Examples:
  - `days=30` with `timeframe="1h"` → 720 hourly candles
  - `days=7` with `timeframe="1d"` → 7 daily candles

**`start_date`** *(datetime, optional)*
- Start timestamp for data generation
- Must be used together with `end_date`
- Mutually exclusive with `days` and `limit`
- Timezone-aware datetime recommended
- Example: `datetime(2024, 1, 1, tzinfo=timezone.utc)`

**`end_date`** *(datetime, optional)*
- End timestamp for data generation
- Must be used together with `start_date`
- Must be after `start_date`
- Generates data up to but not including end_date

**`limit`** *(int, optional)*
- Exact number of candles to generate
- Mutually exclusive with other quantity parameters
- Must be positive integer
- Most efficient for fixed-size datasets
- Maximum recommended: 50,000 candles

**`scenario`** *(str, default="auto")*
- Market scenario/pattern for generation
- Supported values:
  - `"auto"`: Intelligent selection based on symbol/timeframe
  - `"bull"`: Sustained upward trend with pullbacks
  - `"bear"`: Sustained downward trend with rallies
  - `"sideways"`: Range-bound horizontal movement
- Case-insensitive
- Affects trend direction and volatility patterns

#### Returns

**`pd.DataFrame`**
- Pandas DataFrame with datetime index
- Columns: `['open', 'high', 'low', 'close', 'volume']`
- Data types:
  - OHLC: `float64` (prices)
  - Volume: `int64` (integer volume)
- Index: `DatetimeIndex` with regular intervals
- Guaranteed OHLC relationships (high ≥ open,close,low ≤ open,close)

#### Raises

**`ValueError`**
- Invalid or unsupported timeframe
- Negative or zero days/limit
- Invalid parameter combinations
- start_date >= end_date
- Unsupported scenario value

**`TypeError`**
- Incorrect parameter types
- Non-datetime start_date/end_date

#### Examples

```python
# Basic usage
data = generate_mock_data("BTCUSDT", "1h", days=30)

# Date range
from datetime import datetime
data = generate_mock_data(
    "ETHUSD", 
    "4h", 
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 2, 1)
)

# Fixed limit
data = generate_mock_data("DOTUSD", "15m", limit=1000)

# Specific scenario
data = generate_mock_data("ADAUSDT", "1d", days=90, scenario="bull")
```

## Enums and Constants

### `MarketScenario`

Enumeration of available market scenarios.

```python
from enum import Enum

class MarketScenario(Enum):
    AUTO = "auto"
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
```

#### Usage

```python
from mockflow import MarketScenario, generate_mock_data

# Using enum
data = generate_mock_data("BTC", "1h", days=30, scenario=MarketScenario.BULL.value)

# Using string (equivalent)
data = generate_mock_data("BTC", "1h", days=30, scenario="bull")
```

### Supported Timeframes

```python
SUPPORTED_TIMEFRAMES = [
    "1m", "5m", "15m", "30m",            # Minutes
    "1h", "2h", "4h", "6h", "8h", "12h",  # Hours
    "1d", "3d",                          # Days
    "1w"                                 # Weeks
]
```

## Data Schema

### DataFrame Structure

```python
# Returned DataFrame structure
pd.DataFrame({
    'open': float64,     # Opening price
    'high': float64,     # Highest price
    'low': float64,      # Lowest price  
    'close': float64,    # Closing price
    'volume': int64      # Trading volume
}, index=pd.DatetimeIndex)
```

### Data Constraints

- **OHLC Relationships**: `low ≤ open,close ≤ high`
- **Volume**: Always positive integers
- **Timestamps**: Regular intervals based on timeframe
- **Price Precision**: Realistic tick sizes
- **Volume Range**: Market-appropriate volume levels

### Index Properties

```python
# DatetimeIndex properties
data.index.freq          # Inferred frequency (e.g., '1H')
data.index.tz           # Timezone (UTC by default)
data.index.is_monotonic # Always True (chronological order)
```

## Statistical Properties

### Price Movement Characteristics

- **Returns Distribution**: Fat-tailed (realistic kurtosis)
- **Volatility Clustering**: GARCH-like patterns
- **Serial Correlation**: Minimal in returns, significant in squared returns
- **Drift**: Scenario-dependent trend component

### Volume Characteristics

- **Volume-Price Correlation**: Positive correlation with volatility
- **Volume-Return Correlation**: Higher volume on large price moves
- **Cyclical Patterns**: Realistic intraday/weekly patterns
- **Outliers**: Occasional volume spikes

### Market Scenarios

#### Bull Market (`scenario="bull"`)
- **Trend**: Positive drift with occasional pullbacks
- **Volatility**: Moderate, with trend-following patterns
- **Volume**: Higher on upward moves
- **Patterns**: Higher highs, higher lows

#### Bear Market (`scenario="bear"`)
- **Trend**: Negative drift with occasional rallies
- **Volatility**: Elevated, with panic selling patterns
- **Volume**: Higher on downward moves
- **Patterns**: Lower highs, lower lows

#### Sideways Market (`scenario="sideways"`)
- **Trend**: Minimal drift, range-bound
- **Volatility**: Mean-reverting patterns
- **Volume**: Balanced, cyclical
- **Patterns**: Support/resistance levels

#### Auto Selection (`scenario="auto"`)
- **Logic**: Based on symbol type and timeframe
- **Crypto**: Mixed scenarios with higher volatility
- **Forex**: More sideways with occasional trends
- **Stocks**: Scenario rotation based on symbol

## Performance Characteristics

### Generation Speed

- **Typical Performance**: 10,000+ candles/second
- **Memory Usage**: ~1MB per 10,000 candles
- **Scalability**: Linear with data size
- **Optimization**: Vectorized NumPy operations

### Recommended Limits

- **Single Generation**: ≤50,000 candles
- **Memory Efficiency**: Use `limit` parameter for fixed sizes
- **Batch Processing**: Generate multiple smaller datasets
- **Storage**: Consider HDF5/Parquet for large datasets

## Error Handling

### Common Exceptions

```python
# Invalid timeframe
try:
    data = generate_mock_data("BTC", "10m", days=30)
except ValueError as e:
    print(f"Error: {e}")
    # Error: Unsupported timeframe: 10m

# Invalid parameter combination
try:
    data = generate_mock_data("BTC", "1h", days=30, limit=1000)
except ValueError as e:
    print(f"Error: {e}")
    # Error: Cannot specify both 'days' and 'limit'

# Invalid date range
try:
    data = generate_mock_data(
        "BTC", "1h",
        start_date=datetime(2024, 2, 1),
        end_date=datetime(2024, 1, 1)
    )
except ValueError as e:
    print(f"Error: {e}")
    # Error: start_date must be before end_date
```

### Best Practices

1. **Parameter Validation**: Always validate inputs before processing
2. **Resource Management**: Use appropriate limits for memory/time
3. **Error Recovery**: Implement try/except blocks for robust applications
4. **Logging**: Log generation parameters for reproducibility

## Integration Examples

### With Technical Analysis Libraries

```python
import mockflow
import talib
import numpy as np

# Generate data
data = mockflow.generate_mock_data("BTCUSDT", "1h", days=90)

# Calculate indicators
data['sma_20'] = talib.SMA(data['close'], timeperiod=20)
data['rsi'] = talib.RSI(data['close'], timeperiod=14)
data['macd'], data['macd_signal'], data['macd_hist'] = talib.MACD(data['close'])
```

### With Backtesting Frameworks

```python
import mockflow
import backtrader as bt

# Create data feed
data = mockflow.generate_mock_data("ETHUSD", "4h", days=365)

# Convert to backtrader format
bt_data = bt.feeds.PandasData(dataname=data)

# Add to cerebro
cerebro = bt.Cerebro()
cerebro.adddata(bt_data)
```

### With Visualization Libraries

```python
import mockflow
import plotly.graph_objects as go

# Generate data
data = mockflow.generate_mock_data("ADAUSDT", "1d", days=180)

# Create candlestick chart
fig = go.Figure(data=go.Candlestick(
    x=data.index,
    open=data['open'],
    high=data['high'],
    low=data['low'],
    close=data['close']
))

fig.show()
```

## Version Compatibility

### Python Version Support

- **Minimum**: Python 3.8
- **Recommended**: Python 3.10+
- **Tested**: Python 3.8, 3.9, 3.10, 3.11
- **Future**: Python 3.12 support planned

### Dependency Requirements

```python
# Core dependencies
numpy >= 1.20.0
pandas >= 1.3.0

# Development dependencies
pytest >= 7.0
ruff >= 0.1.0
mypy >= 1.0
```

### Breaking Changes

#### Version 0.1.0
- Initial API establishment
- No breaking changes (initial release)

#### Future Versions
- API stability guaranteed for 0.x series
- Breaking changes only in major version bumps
- Deprecation warnings for API changes