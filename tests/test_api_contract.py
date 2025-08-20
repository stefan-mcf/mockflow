"""
API Contract Validation Tests for MockFlow Package

These tests ensure that the MockFlow package maintains API compatibility
and produces valid OHLCV data according to the defined contracts.
"""


import numpy as np
import pandas as pd
import pytest

# Import the mockflow package
from mockflow import generate_mock_data


class TestAPIContract:
    """Test API contract compliance for mockflow package"""

    def test_generate_mock_data_signature(self, test_symbol, test_timeframe):
        """Test that generate_mock_data maintains expected signature"""
        # Basic generation with required parameters
        data1 = generate_mock_data(
            symbol=test_symbol,
            timeframe=test_timeframe,
            limit=100
        )
        assert len(data1) == 100

        # With scenario parameter
        data2 = generate_mock_data(
            symbol="ETH",
            timeframe="15m",
            limit=50,
            scenario="bull"
        )
        assert len(data2) == 50

        # With days parameter
        data3 = generate_mock_data(
            symbol="SOL",
            timeframe="1h",
            days=7,
            scenario="bear"
        )
        assert len(data3) > 0

        # All generations must return valid DataFrame
        assert isinstance(data1, pd.DataFrame)
        assert isinstance(data2, pd.DataFrame)
        assert isinstance(data3, pd.DataFrame)

    def test_ohlcv_schema_contract(self):
        """Test that OHLCV schema contract is maintained"""
        # Generate test data
        data = generate_mock_data(
            symbol="TEST",
            timeframe="1h",
            limit=100,
            scenario="bull"
        )

        # Required columns must be present
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            assert col in data.columns, f"Missing required column: {col}"

        # Data types must be numeric
        for col in required_columns:
            assert pd.api.types.is_numeric_dtype(data[col]), f"Column {col} must be numeric"

        # No NaN values permitted
        for col in required_columns:
            assert not data[col].isna().any(), f"Column {col} contains NaN values"
            assert not np.isinf(data[col]).any(), f"Column {col} contains infinite values"

        # Valid OHLC relationships
        assert (data['high'] >= data['open']).all(), "High must be >= Open"
        assert (data['high'] >= data['close']).all(), "High must be >= Close"
        assert (data['high'] >= data['low']).all(), "High must be >= Low"
        assert (data['low'] <= data['open']).all(), "Low must be <= Open"
        assert (data['low'] <= data['close']).all(), "Low must be <= Close"

        # Positive values
        assert (data['open'] > 0).all(), "Open prices must be positive"
        assert (data['high'] > 0).all(), "High prices must be positive"
        assert (data['low'] > 0).all(), "Low prices must be positive"
        assert (data['close'] > 0).all(), "Close prices must be positive"
        assert (data['volume'] >= 0).all(), "Volume must be non-negative"

    @pytest.mark.parametrize("scenario", ["bull", "bear", "sideways", "auto"])
    def test_scenario_contract(self, scenario):
        """Test that all market scenarios work correctly"""
        data = generate_mock_data(
            symbol="BTC",
            timeframe="1h",
            limit=50,
            scenario=scenario
        )

        assert len(data) == 50
        assert isinstance(data, pd.DataFrame)

        # Check basic data validity for each scenario
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            assert col in data.columns
            assert not data[col].isna().any()

    @pytest.mark.parametrize("timeframe", ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w"])
    def test_timeframe_support_contract(self, timeframe):
        """Test that all standard timeframes are supported"""
        data = generate_mock_data(
            symbol="BTC",
            timeframe=timeframe,
            limit=20,
            scenario="bull"
        )

        assert len(data) == 20
        assert isinstance(data, pd.DataFrame)

        # Check that timestamps are properly spaced
        if len(data) > 1:
            timestamp_diffs = data.index.to_series().diff().dropna()
            # All intervals should be consistent (within small tolerance)
            unique_intervals = timestamp_diffs.unique()
            assert len(unique_intervals) == 1, f"Inconsistent intervals for {timeframe}"

    def test_date_range_contract(self, test_start_date, test_end_date):
        """Test that date range generation works correctly"""
        data = generate_mock_data(
            symbol="BTC",
            timeframe="1h",
            start_date=test_start_date,
            end_date=test_end_date
        )

        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0

        # Check that data falls within specified range
        assert data.index[0] >= test_start_date
        assert data.index[-1] <= test_end_date

    def test_reproducibility_contract(self, test_seed):
        """Test that generation is reproducible with same parameters"""
        # Set seed and generate data
        np.random.seed(test_seed)
        data1 = generate_mock_data(
            symbol="BTC",
            timeframe="1h",
            limit=50,
            scenario="bull"
        )

        # Reset seed and generate again
        np.random.seed(test_seed)
        data2 = generate_mock_data(
            symbol="BTC",
            timeframe="1h",
            limit=50,
            scenario="bull"
        )

        # Data should be identical
        pd.testing.assert_frame_equal(data1, data2)

    def test_data_bounds_contract(self):
        """Test that generated data stays within reasonable bounds"""
        data = generate_mock_data(
            symbol="BTC",
            timeframe="1h",
            limit=100,
            scenario="bull"
        )

        # Price bounds (should be reasonable for BTC-like asset)
        assert data['close'].min() >= 1, "Prices should not be too low"
        assert data['close'].max() <= 1_000_000, "Prices should not be too high"

        # Volume bounds
        assert data['volume'].min() >= 0, "Volume should be non-negative"
        assert data['volume'].max() < 1e12, "Volume should not be unrealistically high"

        # Volatility bounds (daily returns should be reasonable)
        returns = data['close'].pct_change().dropna()
        assert abs(returns).max() < 0.5, "Single-period returns should not exceed 50%"

    def test_edge_case_handling(self):
        """Test handling of edge cases and boundary conditions"""
        # Minimum limit
        data = generate_mock_data(
            symbol="BTC",
            timeframe="1h",
            limit=1
        )
        assert len(data) == 1

        # Very small days parameter
        data = generate_mock_data(
            symbol="BTC",
            timeframe="1d",
            days=1
        )
        assert len(data) >= 1

    def test_market_scenario_type_contract(self):
        """Test that MarketScenario type is properly exported"""
        # Test that we can use the MarketScenario type
        scenarios = ["bull", "bear", "sideways", "auto"]

        for scenario in scenarios:
            data = generate_mock_data(
                symbol="BTC",
                timeframe="1h",
                limit=10,
                scenario=scenario  # type: ignore
            )
            assert len(data) == 10
