# 🔍 SourceSense

**Database Metadata Extraction & Analysis**

This App is a data source application built using Atlan's application-sdk framework. It connects to SQL databases and demonstrates intelligent metadata extraction, providing deep insights into database schemas, data quality, and potential sensitive data.

## 🚀 Features

### Core Capabilities

- **SQL DBs Support**: PostgreSQL, MySQL
- **Schema Discovery**: Comprehensive table, column, and relationship mapping
- **Metadata Extraction**:
  - Column names, data types, constraints
  - Primary keys and foreign key relationships
  - Index information and table statistics

### Advanced Analytics

- **Data Quality Metrics**: Null counts, uniqueness ratios, and quality scoring
- **Sensitive Data Detection**: identify PII, authentication data, and other sensitive information
- **Relationship Mapping**: Foreign key relationships and data lineage insights

## 📋 Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [Dapr CLI](https://docs.dapr.io/getting-started/install-dapr-cli/)
- [Temporal CLI](https://docs.temporal.io/cli)

## 🛠️ Setup Instructions

### 1. Clone and Install

```bash
git clone <repository-url>
cd metadata-extract
uv sync
```

### 2. Download Required Components

```bash
uv run poe download-components
```

### 3. Start Dependencies

```bash
# Start Dapr and Temporal (run in separate terminal)
uv run poe start-deps
```

### 4. Run the Application

```bash
uv run main.py
```

### 5. Access the Application

- **Web Interface**: http://localhost:8000
- **Temporal UI**: http://localhost:8233

## 🎯 Quick Start

1. **Configure Database Connection**

   - Select your database type (PostgreSQL, MySQL, SQLite, SQL Server)
   - Enter connection details (host, port, database name, credentials)
   - Test the connection before proceeding

2. **Choose Analysis Options**

   - **Data Quality Analysis**: Enable comprehensive quality metrics
   - **Sensitive Data Detection**: Identify potentially sensitive columns

3. **Extract Metadata**

   - Click "Extract Metadata" to start the workflow
   - Monitor real-time progress in the dashboard

4. **Analyze Results**
   - **Schema Overview**: Explore database structure and relationships
   - **Data Quality**: Assess data completeness and uniqueness
   - **Sensitive Data**: Review detected sensitive information

## 🎨 Supported Database Types

| Database   | Connection String Example                | Default Port |
| ---------- | ---------------------------------------- | ------------ |
| PostgreSQL | `postgresql://user:pass@host:5432/db`    | 5432         |
| MySQL      | `mysql+pymysql://user:pass@host:3306/db` | 3306         |

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html
```

## 📚 Documentation

- [Architecture Notes](docs/ARCHITECTURE.md) - High-level design decisions
- [Framework Notes](docs/FRAMEWORK_NOTES.md) - Atlan Apps Framework challenges and patterns
- [Demo Instructions](docs/DEMO.md) - Step-by-step testing guide
- [Test Documentation](tests/README.md) - Test suite overview

---

**Built using Atlan's application-sdk Framework**
