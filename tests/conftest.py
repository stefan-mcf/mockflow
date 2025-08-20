"""
MockFlow Test Configuration

Pytest configuration and shared fixtures for the mockflow test suite.
"""

from datetime import datetime

import numpy as np
import pytest


@pytest.fixture(scope="session")
def test_seed():
    """Fixed seed for reproducible test results"""
    return 42


@pytest.fixture(autouse=True)
def reset_random_state(test_seed):
    """Ensure each test starts with a clean random state"""
    np.random.seed(test_seed)


@pytest.fixture
def test_symbol():
    """Standard test symbol"""
    return "BTCUSDT"


@pytest.fixture
def test_timeframe():
    """Standard test timeframe"""
    return "1h"


@pytest.fixture
def test_start_date():
    """Standard test start date"""
    return datetime(2024, 1, 1)


@pytest.fixture
def test_end_date():
    """Standard test end date"""
    return datetime(2024, 1, 31)


@pytest.fixture
def small_dataset_params():
    """Parameters for small test datasets"""
    return {
        "symbol": "TESTCOIN",
        "timeframe": "1h",
        "days": 7,
        "scenario": "bull"
    }


@pytest.fixture
def performance_tolerance():
    """Performance tolerance for test assertions"""
    return 1.2  # 20% tolerance
