"""
Pytest configuration and fixtures for the Sudoku application.

This file sets up the Flask test client and other shared test fixtures.
"""
import pytest
import sys
import os

# Add starter directory to path so we can import app and sudoku_logic
sys.path.insert(0, os.path.dirname(__file__))

import app as app_module


@pytest.fixture
def flask_app():
    """Create and configure a Flask app instance for testing."""
    app_module.app.config['TESTING'] = True
    return app_module.app


@pytest.fixture
def client(flask_app):
    """Create a test client for the Flask app."""
    with flask_app.app_context():
        # Reset the global CURRENT state before each test
        app_module.CURRENT['puzzle'] = None
        app_module.CURRENT['solution'] = None
    
    return flask_app.test_client()


@pytest.fixture
def app_context(flask_app):
    """Create an application context for testing."""
    with flask_app.app_context():
        # Reset the global CURRENT state
        app_module.CURRENT['puzzle'] = None
        app_module.CURRENT['solution'] = None
        yield flask_app
