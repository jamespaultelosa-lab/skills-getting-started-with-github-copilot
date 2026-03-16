"""
Pytest configuration and fixtures for API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Reset activities to a known state before and after each test.
    This ensures test isolation and prevents state leakage between tests.
    """
    # Store original state
    original_activities = {
        key: {
            **value,
            "participants": value["participants"].copy()
        }
        for key, value in activities.items()
    }
    
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)
