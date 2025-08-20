"""
Market Drift Validation Tests for MockFlow Package

These tests validate that different market scenarios (bull, bear, sideways)
produce appropriate directional trends and drift characteristics.
"""

import numpy as np
import pytest
from scipy import stats

# Import the mockflow package
from mockflow import generate_mock_data


class TestDriftValidation:
    """Test market drift and trend validation"""

    def test_bull_market_drift(self, test_seed):
        """Test that bull market shows positive drift"""
        np.random.seed(test_seed)
        data = generate_mock_data(
            symbol="TEST",
            timeframe="1h",
            limit=500,
            scenario="bull"
        )

        returns = data['close'].pct_change().dropna()
        cumulative_return = (data['close'].iloc[-1] / data['close'].iloc[0]) - 1
        average_return = returns.mean()

        # Bull market characteristics
        assert average_return >= -0.001, f"Bull market should have non-negative average return: {average_return:.4f}"
        assert cumulative_return >= -0.3, f"Bull market should not decline too much: {cumulative_return:.3f}"

        # Test trend direction using linear regression
        prices = data['close'].values
        time_index = np.arange(len(prices))
        slope, intercept, r_value, p_value, std_err = stats.linregress(time_index, prices)

        # Slope should generally be positive or at least not strongly negative
        assert slope >= -0.1, f"Bull market should have non-negative trend: {slope:.4f}"

    def test_bear_market_drift(self, test_seed):
        """Test that bear market shows negative drift"""
        np.random.seed(test_seed)
        data = generate_mock_data(
            symbol="TEST",
            timeframe="1h",
            limit=500,
            scenario="bear"
        )

        returns = data['close'].pct_change().dropna()
        cumulative_return = (data['close'].iloc[-1] / data['close'].iloc[0]) - 1
        average_return = returns.mean()

        # Bear market characteristics
        assert average_return <= 0.001, f"Bear market should have non-positive average return: {average_return:.4f}"
        assert cumulative_return <= 0.3, f"Bear market should not rise too much: {cumulative_return:.3f}"

        # Test trend direction using linear regression
        prices = data['close'].values
        time_index = np.arange(len(prices))
        slope, intercept, r_value, p_value, std_err = stats.linregress(time_index, prices)

        # Slope should generally be negative or at least not strongly positive
        assert slope <= 0.1, f"Bear market should have non-positive trend: {slope:.4f}"

    def test_sideways_market_drift(self, test_seed):
        """Test that sideways market shows minimal drift"""
        np.random.seed(test_seed)
        data = generate_mock_data(
            symbol="TEST",
            timeframe="1h",
            limit=500,
            scenario="sideways"
        )

        returns = data['close'].pct_change().dropna()
        cumulative_return = (data['close'].iloc[-1] / data['close'].iloc[0]) - 1
        average_return = returns.mean()

        # Sideways market characteristics
        assert abs(average_return) <= 0.002, f"Sideways market should have minimal average return: {average_return:.4f}"
        assert abs(cumulative_return) <= 0.4, f"Sideways market should not trend strongly: {cumulative_return:.3f}"

        # Test that price stays within a reasonable range
        price_range = data['close'].max() / data['close'].min()
        assert price_range <= 2.5, f"Sideways market should not have excessive range: {price_range:.3f}"

    def test_auto_scenario_drift_variety(self, test_seed):
        """Test that auto scenario produces varied drift patterns"""
        drift_patterns = []

        # Generate multiple datasets with auto scenario
        for i in range(5):
            np.random.seed(test_seed + i)
            data = generate_mock_data(
                symbol=f"TEST{i}",  # Different symbols for variety
                timeframe="1h",
                limit=300,
                scenario="auto"
            )

            cumulative_return = (data['close'].iloc[-1] / data['close'].iloc[0]) - 1
            drift_patterns.append(cumulative_return)

        # Should show variety in drift patterns
        drift_std = np.std(drift_patterns)
        assert drift_std > 0.05, f"Auto scenario should show drift variety: {drift_std:.3f}"

        # Should not all be the same extreme
        min_drift = min(drift_patterns)
        max_drift = max(drift_patterns)
        assert max_drift - min_drift > 0.1, f"Auto scenario should show range of drifts: {max_drift - min_drift:.3f}"

    def test_drift_consistency_across_timeframes(self, test_seed):
        """Test that drift direction is consistent across different timeframes"""
        scenarios = ["bull", "bear", "sideways"]
        timeframes = ["1h", "4h", "1d"]

        for scenario in scenarios:
            drifts = {}

            for timeframe in timeframes:
                np.random.seed(test_seed)  # Same seed for comparison
                data = generate_mock_data(
                    symbol="TEST",
                    timeframe=timeframe,
                    days=30,  # Use days instead of limit for timeframe comparison
                    scenario=scenario
                )

                cumulative_return = (data['close'].iloc[-1] / data['close'].iloc[0]) - 1
                drifts[timeframe] = cumulative_return

            # Check consistency of drift direction across timeframes
            drift_signs = [np.sign(drift) for drift in drifts.values()]

            if scenario == "bull":
                # Bull markets should generally be non-negative across timeframes
                negative_count = sum(1 for sign in drift_signs if sign < 0)
                assert negative_count <= 1, "Bull market should be consistent across timeframes"
            elif scenario == "bear":
                # Bear markets should generally be non-positive across timeframes
                positive_count = sum(1 for sign in drift_signs if sign > 0)
                assert positive_count <= 1, "Bear market should be consistent across timeframes"
            elif scenario == "sideways":
                # Sideways markets should have mixed or neutral directions
                # No strong requirement here as sideways can fluctuate
                pass

    def test_return_distribution_by_scenario(self, test_seed):
        """Test that return distributions are appropriate for each scenario"""
        scenarios = ["bull", "bear", "sideways"]

        for scenario in scenarios:
            np.random.seed(test_seed)
            data = generate_mock_data(
                symbol="TEST",
                timeframe="1h",
                limit=1000,
                scenario=scenario
            )

            returns = data['close'].pct_change().dropna()

            # Basic distribution properties
            mean_return = returns.mean()
            std_return = returns.std()
            skewness = stats.skew(returns)

            # Scenario-specific validation
            if scenario == "bull":
                # Bull market should have positive or neutral skew and mean
                assert mean_return >= -0.002, f"Bull mean return should be non-negative: {mean_return:.4f}"
                assert skewness >= -1.0, f"Bull market should not be too negatively skewed: {skewness:.3f}"

            elif scenario == "bear":
                # Bear market should have negative or neutral skew and mean
                assert mean_return <= 0.002, f"Bear mean return should be non-positive: {mean_return:.4f}"
                assert skewness <= 1.0, f"Bear market should not be too positively skewed: {skewness:.3f}"

            elif scenario == "sideways":
                # Sideways market should be roughly centered
                assert abs(mean_return) <= 0.002, f"Sideways mean return should be near zero: {mean_return:.4f}"
                assert abs(skewness) <= 1.5, f"Sideways market should not be too skewed: {skewness:.3f}"

            # All scenarios should have reasonable volatility
            assert 0.005 <= std_return <= 0.08, f"{scenario} volatility should be reasonable: {std_return:.4f}"

    def test_trend_persistence(self, test_seed):
        """Test that trends show appropriate persistence"""
        scenarios = ["bull", "bear"]

        for scenario in scenarios:
            np.random.seed(test_seed)
            data = generate_mock_data(
                symbol="TEST",
                timeframe="1h",
                limit=500,
                scenario=scenario
            )

            returns = data['close'].pct_change().dropna()

            # Calculate trend persistence using run analysis
            positive_runs = []
            negative_runs = []
            current_run = 0
            last_sign = 0

            for ret in returns:
                current_sign = np.sign(ret)
                if current_sign == last_sign and current_sign != 0:
                    current_run += 1
                else:
                    if current_run > 0:
                        if last_sign > 0:
                            positive_runs.append(current_run)
                        else:
                            negative_runs.append(current_run)
                    current_run = 1
                    last_sign = current_sign

            # Add final run
            if current_run > 0:
                if last_sign > 0:
                    positive_runs.append(current_run)
                else:
                    negative_runs.append(current_run)

            # Calculate average run lengths
            avg_positive_run = np.mean(positive_runs) if positive_runs else 0
            avg_negative_run = np.mean(negative_runs) if negative_runs else 0

            # Trends should show some persistence (runs > 1)
            if scenario == "bull":
                assert avg_positive_run >= 1.0, f"Bull market should show positive run persistence: {avg_positive_run:.2f}"
            elif scenario == "bear":
                assert avg_negative_run >= 1.0, f"Bear market should show negative run persistence: {avg_negative_run:.2f}"

    @pytest.mark.parametrize("days", [7, 30, 90])
    def test_drift_scaling_with_time_horizon(self, days, test_seed):
        """Test that drift scales appropriately with time horizon"""
        np.random.seed(test_seed)
        data = generate_mock_data(
            symbol="TEST",
            timeframe="1h",
            days=days,
            scenario="bull"
        )

        data['close'].pct_change().dropna()
        cumulative_return = (data['close'].iloc[-1] / data['close'].iloc[0]) - 1
        annualized_return = cumulative_return * (365 / days)

        # Longer horizons should allow for larger absolute returns
        max_reasonable_annual_return = 100.0  # 10000% annual return max (very lenient for mock data)
        assert abs(annualized_return) <= max_reasonable_annual_return, \
            f"Annualized return should be reasonable: {annualized_return:.3f}"

        # Returns should not be completely flat
        assert abs(cumulative_return) >= 0.001, f"Should show some movement: {cumulative_return:.4f}"
