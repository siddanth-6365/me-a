# SourceSense Test Suite

This directory contains focused tests for the core SourceSense metadata extraction functionality.

## Test Structure

### Test Files

- **`test_core.py`** - Core functionality tests for metadata extraction and database connection
- **`test_basic.py`** - Basic unit tests for core functionality
- **`conftest.py`** - Test fixtures and configuration
- **`pytest.ini`** - Pytest configuration

## Running Tests

### Run All Tests
```bash
uv run pytest
```

### Run Specific Test Files
```bash
# Run core functionality tests
uv run pytest tests/test_core.py -v

# Run basic component tests
uv run pytest tests/test_basic.py -v
```

## Test Coverage

The test suite covers:

### Core Functionality (`test_core.py`)
- Database connection testing (success/failure)
- Connection URL building (PostgreSQL, MySQL, SQLite)
- Sensitive data detection
- Workflow execution and summary generation
- Error handling for unsupported database types

### Basic Functionality (`test_basic.py`)
- Component instantiation (Workflow and Activities)
- Activity sequence management
- Input validation and error handling
- Core method functionality

## Test Data

Test fixtures provide:
- Database connection configurations
- Sample metadata structures
- Mock database responses
- Error scenarios for testing
