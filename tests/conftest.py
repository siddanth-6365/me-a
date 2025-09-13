"""
Test fixtures and configuration for SourceSense core functionality tests.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime
from typing import Dict, Any


@pytest.fixture
def sample_connection_config() -> Dict[str, Any]:
    """Sample database connection configuration for testing."""
    return {
        "database_type": "postgresql",
        "host": "localhost",
        "port": "5432",
        "database": "test_db",
        "username": "test_user",
        "password": "test_password"
    }


@pytest.fixture
def sample_mysql_connection_config() -> Dict[str, Any]:
    """Sample MySQL database connection configuration for testing."""
    return {
        "database_type": "mysql",
        "host": "localhost",
        "port": "3306",
        "database": "test_db",
        "username": "test_user",
        "password": "test_password"
    }


@pytest.fixture
def sample_sqlite_connection_config() -> Dict[str, Any]:
    """Sample SQLite database connection configuration for testing."""
    return {
        "database_type": "sqlite",
        "database": "/path/to/test.db"
    }


@pytest.fixture
def sample_schema_metadata() -> Dict[str, Any]:
    """Sample schema metadata for testing."""
    return {
        "database_info": {
            "database_type": "postgresql",
            "database_name": "test_db",
            "extraction_timestamp": "2024-01-01T00:00:00"
        },
        "schemas": [
            {
                "schema_name": "public",
                "tables": [
                    {
                        "table_name": "users",
                        "columns": [
                            {
                                "column_name": "id",
                                "data_type": "INTEGER",
                                "nullable": False,
                                "default": None,
                                "comment": "Primary key"
                            },
                            {
                                "column_name": "email",
                                "data_type": "VARCHAR",
                                "nullable": False,
                                "default": None,
                                "comment": "User email address"
                            },
                            {
                                "column_name": "password",
                                "data_type": "VARCHAR",
                                "nullable": False,
                                "default": None,
                                "comment": "Hashed password"
                            }
                        ]
                    }
                ]
            }
        ],
        "statistics": {
            "total_schemas": 1,
            "total_tables": 1,
            "total_columns": 3
        }
    }


@pytest.fixture
def sample_sensitive_data_result() -> Dict[str, Any]:
    """Sample sensitive data detection result for testing."""
    return {
        "detection_timestamp": "2024-01-01T00:00:00",
        "sensitive_columns": [
            {
                "schema_name": "public",
                "table_name": "users",
                "column_name": "email",
                "data_type": "VARCHAR",
                "category": "PII",
                "pattern_matched": "email",
                "confidence": "medium"
            },
            {
                "schema_name": "public",
                "table_name": "users",
                "column_name": "password",
                "data_type": "VARCHAR",
                "category": "Authentication",
                "pattern_matched": "password",
                "confidence": "medium"
            }
        ],
        "summary": {
            "PII": 1,
            "Financial": 0,
            "Health": 0,
            "Authentication": 1
        }
    }


@pytest.fixture
def sample_connection_test_success() -> Dict[str, Any]:
    """Sample successful connection test result."""
    return {
        "status": "success",
        "message": "Database connection successful",
        "timestamp": "2024-01-01T00:00:00"
    }


@pytest.fixture
def sample_connection_test_failure() -> Dict[str, Any]:
    """Sample failed connection test result."""
    return {
        "status": "error",
        "message": "Database connection failed: Connection refused",
        "timestamp": "2024-01-01T00:00:00"
    }


@pytest.fixture
def mock_sqlalchemy_engine():
    """Mock SQLAlchemy engine for testing."""
    mock_engine = Mock()
    mock_conn = Mock()
    mock_result = Mock()
    mock_result.fetchone.return_value = (1,)
    mock_conn.execute.return_value = mock_result
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    return mock_engine


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    logger = Mock()
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    return logger


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "core: mark test as core functionality test"
    )
    config.addinivalue_line(
        "markers", "connection: mark test as database connection test"
    )
    config.addinivalue_line(
        "markers", "metadata: mark test as metadata extraction test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        if "connection" in item.nodeid:
            item.add_marker(pytest.mark.connection)
        elif "metadata" in item.nodeid or "sensitive" in item.nodeid:
            item.add_marker(pytest.mark.metadata)
        else:
            item.add_marker(pytest.mark.core)