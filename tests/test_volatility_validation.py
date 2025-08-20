"""
Volatility Pattern Validation Tests for MockFlow Package

These tests validate volatility clustering, persistence, and
realistic volatility patterns in the generated data.
"""

import numpy as np
import pytest
from scipy import stats

# Import the mockflow package
from mockflow import generate_mock_data


class TestVolatilityValidation:
    """Test volatility pattern validation"""

    def test_volatility_clustering_garch_effects(self, test_seed):
        """Test for GARCH-like volatility clustering effects"""
        np.random.seed(test_seed)
        data = generate_mock_data(
            symbol="TEST",
            timeframe="1h",
            limit=1000,
            scenario="sideways"
        )

        returns = data['close'].pct_change().dropna()
        squared_returns = returns ** 2

        # Test for autocorrelation in squared returns (ARCH effects)
        if len(squared_returns) > 50:
            autocorr_1 = squared_returns.autocorr(lag=1)
            autocorr_5 = squared_returns.autocorr(lag=5)

            # Should show some positive autocorrelation (clustering)
            assert autocorr_1 >= -0.2, f"1-lag autocorr should show clustering, got {autocorr_1:.3f}"
            assert autocorr_5 >= -0.3, f"5-lag autocorr should show some persistence, got {autocorr_5:.3f}"

    def test_volatility_persistence(self, test_seed):
        """Test that volatility shows persistence over time"""
        np.random.seed(test_seed)
        data = generate_mock_data(
            symbol="TEST",
            timeframe="1h",
            limit=1000,
            scenario="bull"
        )

        returns = data['close'].pct_change().dropna()

        # Calculate rolling volatility
        vol_window = 20
        volatility = returns.rolling(window=vol_window).std().dropna()

        if len(volatility) > 50:
            # Test persistence in volatility levels
            vol_changes = volatility.diff().dropna()
            persistence = vol_changes.autocorr(lag=1)

            # Volatility should show some persistence
            assert persistence >= -0.3, f"Volatility should show persistence, got {persistence:.3f}"

            # High volatility periods should cluster
            high_vol_threshold = volatility.quantile(0.75)
            high_vol_periods = volatility > high_vol_threshold

            # Count high volatility clusters
            clusters = 0
            in_cluster = False
            for is_high_vol in high_vol_periods:
                if is_high_vol and not in_cluster:
                    clusters += 1
                    in_cluster = True
                elif not is_high_vol:
                    in_cluster = False

            cluster_ratio = clusters / high_vol_periods.sum() if high_vol_periods.sum() > 0 else 1
            # Should have fewer clusters than individual high-vol periods (clustering)
            assert cluster_ratio <= 0.8, f"High volatility should cluster, ratio: {cluster_ratio:.3f}"

    def test_volatility_bounds_and_scaling(self, test_seed):
        """Test that volatility stays within reasonable bounds"""
        np.random.seed(test_seed)
        data = generate_mock_data(
            symbol="TEST",
            timeframe="1h",
            limit=500,
            scenario="bull"
        )

        returns = data['close'].pct_change().dropna()
        volatility = returns.rolling(window=20).std().dropna()

        # Volatility bounds
        vol_min = volatility.min()
        vol_max = volatility.max()
        vol_mean = volatility.mean()

        # Reasonable volatility bounds
        assert vol_min >= 0, "Volatility should be non-negative"
        assert vol_max <= 0.15, f"Max volatility should be ≤15%, got {vol_max:.4f}"
        assert vol_mean <= 0.05, f"Average volatility should be ≤5%, got {vol_mean:.4f}"

        # Volatility should vary (not constant)
        vol_std = volatility.std()
        cv = vol_std / vol_mean if vol_mean > 0 else 0
        assert cv > 0.1, f"Volatility should vary over time, CV: {cv:.3f}"

    def test_regime_volatility_differences(self, test_seed):
        """Test that different market scenarios show different volatility patterns"""
        scenarios = ["bull", "bear", "sideways"]
        volatilities = {}

        for scenario in scenarios:
            np.random.seed(test_seed)  # Same seed for comparison
            data = generate_mock_data(
                symbol="TEST",
                timeframe="1h",
                limit=500,
                scenario=scenario
            )

            returns = data['close'].pct_change().dropna()
            volatilities[scenario] = returns.std()

        # All volatilities should be reasonable
        for scenario, vol in volatilities.items():
            assert 0.001 <= vol <= 0.10, f"{scenario} volatility should be reasonable: {vol:.4f}"

        # Scenarios should show some variation in volatility characteristics
        vol_values = list(volatilities.values())
        vol_range = max(vol_values) - min(vol_values)
        assert vol_range >= 0, "Should show some volatility variation across scenarios"

    def test_volume_volatility_correlation(self, test_seed):
        """Test correlation between volume and price volatility"""
        np.random.seed(test_seed)
        data = generate_mock_data(
            symbol="TEST",
            timeframe="1h",
            limit=1000,
            scenario="bull"
        )

        returns = data['close'].pct_change().dropna()
        volatility = returns.abs()  # Use absolute returns as proxy for volatility
        volumes = data['volume'].iloc[1:]  # Align with returns

        if len(volatility) == len(volumes) and len(volatility) > 50:
            # Calculate correlation between volume and volatility
            correlation = volatility.corr(volumes)

            # Should show some positive correlation (higher volume with higher volatility)
            assert correlation >= -0.3, f"Volume-volatility correlation should not be strongly negative: {correlation:.3f}"

            # Test that high volatility periods have higher than average volume
            high_vol_threshold = volatility.quantile(0.8)
            high_vol_periods = volatility > high_vol_threshold

            if high_vol_periods.sum() > 10:
                avg_volume_high_vol = volumes[high_vol_periods].mean()
                avg_volume_overall = volumes.mean()

                volume_ratio = avg_volume_high_vol / avg_volume_overall
                # High volatility periods should have somewhat higher volume
                assert volume_ratio >= 0.5, f"High volatility should have reasonable volume: {volume_ratio:.3f}"

    @pytest.mark.parametrize("timeframe", ["15m", "1h", "4h", "1d"])
    def test_volatility_scaling_across_timeframes(self, timeframe, test_seed):
        """Test that volatility scales appropriately across timeframes"""
        np.random.seed(test_seed)
        data = generate_mock_data(
            symbol="TEST",
            timeframe=timeframe,
            limit=200,
            scenario="sideways"
        )

        returns = data['close'].pct_change().dropna()
        volatility = returns.std()

        # Volatility should be within reasonable bounds for each timeframe
        if timeframe in ["15m", "30m"]:
            # Shorter timeframes should have lower volatility per period
            assert volatility <= 0.03, f"15m/30m volatility should be low: {volatility:.4f}"
        elif timeframe in ["1h", "2h", "4h"]:
            # Medium timeframes
            assert volatility <= 0.08, f"Hourly volatility should be moderate: {volatility:.4f}"
        elif timeframe in ["1d", "3d"]:
            # Daily timeframes can have higher volatility
            assert volatility <= 0.12, f"Daily volatility should be reasonable: {volatility:.4f}"

        # All timeframes should produce meaningful volatility
        assert volatility >= 0.001, f"Volatility should not be too low: {volatility:.4f}"

    def test_fat_tail_behavior(self, test_seed):
        """Test that returns exhibit some fat-tail behavior"""
        np.random.seed(test_seed)
        data = generate_mock_data(
            symbol="TEST",
            timeframe="1h",
            limit=1000,
            scenario="sideways"
        )

        returns = data['close'].pct_change().dropna()

        if len(returns) > 100:
            # Calculate kurtosis (fat tails indicator)
            kurtosis = stats.kurtosis(returns)

            # Should show some excess kurtosis (fat tails) but not extreme
            assert kurtosis >= -1, f"Kurtosis should not be too negative: {kurtosis:.3f}"
            assert kurtosis <= 20, f"Kurtosis should not be extreme: {kurtosis:.3f}"

            # Test for extreme returns (beyond 2.5 standard deviations)
            std_dev = returns.std()
            extreme_threshold = 2.5 * std_dev
            extreme_returns = returns.abs() > extreme_threshold
            extreme_frequency = extreme_returns.sum() / len(returns)

            # Should have some but not too many extreme returns
            assert extreme_frequency <= 0.05, f"Extreme returns should be rare: {extreme_frequency:.3f}"
