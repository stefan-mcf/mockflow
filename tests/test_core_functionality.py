"""
Core Functionality Tests for MockFlow Package

These tests validate the basic functionality and integration
of the mockflow package components.
"""


import numpy as np
import pandas as pd
import pytest

# Import the mockflow package
from mockflow import MarketScenario, generate_mock_data


class TestCoreFunctionality:
    """Test core mockflow functionality"""

    def test_package_imports(self):
        """Test that package imports work correctly"""
        # Test that main function is available
        assert callable(generate_mock_data)

        # Test that MarketScenario type is available
        # This test just ensures the import works
        assert MarketScenario is not None

    def test_basic_data_generation(self, test_symbol, test_timeframe):
        """Test basic data generation functionality"""
        data = generate_mock_data(
            symbol=test_symbol,
            timeframe=test_timeframe,
            limit=100
        )

        # Basic structure validation
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 100
        assert data.index.name is None or isinstance(data.index, pd.DatetimeIndex)

        # Required columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            assert col in data.columns

    def test_data_generation_with_days(self, test_symbol):
        """Test data generation using days parameter"""
        data = generate_mock_data(
            symbol=test_symbol,
            timeframe="1h",
            days=7
        )

        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0

        # Should generate approximately 7 days * 24 hours = 168 periods
        expected_periods = 7 * 24
        tolerance = 0.2  # 20% tolerance
        assert abs(len(data) - expected_periods) <= expected_periods * tolerance

    def test_data_generation_with_date_range(self, test_start_date, test_end_date):
        """Test data generation using date range"""
        data = generate_mock_data(
            symbol="BTC",
            timeframe="1h",
            start_date=test_start_date,
            end_date=test_end_date
        )

        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0

        # Verify date range
        if hasattr(data.index, 'min') and hasattr(data.index, 'max'):
            assert data.index.min() >= test_start_date
            assert data.index.max() <= test_end_date

    @pytest.mark.parametrize("scenario", ["bull", "bear", "sideways", "auto"])
    def test_all_scenarios(self, scenario):
        """Test that all market scenarios work"""
        data = generate_mock_data(
            symbol="TEST",
            timeframe="1h",
            limit=50,
            scenario=scenario
        )

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 50

        # Basic data validation for each scenario
        assert (data['close'] > 0).all()
        assert (data['volume'] >= 0).all()
        assert not data.isna().any().any()

    @pytest.mark.parametrize("timeframe", ["15m", "30m", "1h", "2h", "4h", "12h", "1d"])
    def test_all_timeframes(self, timeframe):
        """Test that all supported timeframes work"""
        data = generate_mock_data(
            symbol="BTC",
            timeframe=timeframe,
            limit=20
        )

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 20

        # Validate data structure
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            assert col in data.columns
            assert not data[col].isna().any()

    def test_parameter_combinations(self):
        """Test various parameter combinations"""
        # Test with multiple parameters
        data = generate_mock_data(
            symbol="ETH",
            timeframe="4h",
            limit=100,
            scenario="bull"
        )
        assert len(data) == 100

        # Test with days and scenario
        data = generate_mock_data(
            symbol="SOL",
            timeframe="1h",
            days=3,
            scenario="bear"
        )
        assert len(data) > 0

        # Test minimal parameters
        data = generate_mock_data(symbol="BTC")
        assert len(data) > 0

    def test_data_quality_checks(self):
        """Test data quality and consistency"""
        data = generate_mock_data(
            symbol="TEST",
            timeframe="1h",
            limit=100,
            scenario="sideways"
        )

        # No missing values
        assert not data.isna().any().any()
        assert not np.isinf(data.select_dtypes(include=[np.number])).any().any()

        # Positive prices
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            assert (data[col] > 0).all()

        # Non-negative volume
        assert (data['volume'] >= 0).all()

        # OHLC relationships
        assert (data['high'] >= data['open']).all()
        assert (data['high'] >= data['close']).all()
        assert (data['high'] >= data['low']).all()
        assert (data['low'] <= data['open']).all()
        assert (data['low'] <= data['close']).all()

    def test_reproducibility(self, test_seed):
        """Test that generation is reproducible"""
        params = {
            "symbol": "BTC",
            "timeframe": "1h",
            "limit": 50,
            "scenario": "bull"
        }

        # Generate data twice with same seed
        np.random.seed(test_seed)
        data1 = generate_mock_data(**params)

        np.random.seed(test_seed)
        data2 = generate_mock_data(**params)

        # Should be identical
        pd.testing.assert_frame_equal(data1, data2)

    def test_data_types(self):
        """Test that data types are correct"""
        data = generate_mock_data(
            symbol="BTC",
            timeframe="1h",
            limit=50
        )

        # Check data types
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            assert pd.api.types.is_numeric_dtype(data[col])

        assert pd.api.types.is_numeric_dtype(data['volume'])

        # Volume should be integer-like (even if stored as float)
        volume_decimals = data['volume'] % 1
        assert (volume_decimals == 0).all()

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Minimum limit
        data = generate_mock_data(symbol="BTC", limit=1)
        assert len(data) == 1

        # Small days parameter
        data = generate_mock_data(symbol="BTC", days=1)
        assert len(data) >= 1

        # Very short timeframe
        data = generate_mock_data(symbol="BTC", timeframe="15m", limit=5)
        assert len(data) == 5

    def test_symbol_variation(self):
        """Test that different symbols produce varied results"""
        symbols = ["BTC", "ETH", "SOL", "DOGE", "ADA"]
        datasets = []

        for symbol in symbols:
            np.random.seed(42)  # Same seed for comparison
            data = generate_mock_data(
                symbol=symbol,
                timeframe="1h",
                limit=50,
                scenario="auto"  # Auto should vary by symbol
            )
            datasets.append(data['close'].iloc[-1])

        # Different symbols with auto scenario should produce different final prices
        # (due to hash-based scenario selection)
        unique_final_prices = len(set(datasets))
        assert unique_final_prices > 1, "Different symbols should produce varied results"

    def test_performance_reasonable(self):
        """Test that generation performance is reasonable"""
        import time

        start_time = time.time()
        data = generate_mock_data(
            symbol="BTC",
            timeframe="1h",
            limit=500  # Reduced to fit within performance caps
        )
        end_time = time.time()

        generation_time = end_time - start_time

        # Should generate data reasonably quickly (< 5 seconds)
        assert generation_time < 5.0, f"Generation took too long: {generation_time:.2f}s"
        assert len(data) == 500
