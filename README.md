# 🔍 SourceSense

**Database Metadata Extraction & Analysis**

SourceSense is a comprehensive data source application built using Atlan's Apps Framework. It connects to SQL databases and demonstrates intelligent metadata extraction, providing deep insights into database schemas, data quality, and potential sensitive data.


## 🚀 Features

### Core Capabilities
- **Multi-Database Support**: PostgreSQL, MySQL, SQLite, SQL Server
- **Schema Discovery**: Comprehensive table, column, and relationship mapping
- **Metadata Extraction**: 
  - Column names, data types, constraints
  - Primary keys and foreign key relationships
  - Index information and table statistics

### Advanced Analytics
- **Data Quality Metrics**: Null counts, uniqueness ratios, and quality scoring
- **Relationship Mapping**: Foreign key relationships and data lineage insights

## 📋 Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [Dapr CLI](https://docs.dapr.io/getting-started/install-dapr-cli/)
- [Temporal CLI](https://docs.temporal.io/cli)

## 🛠️ Quick Start

1. **Download required components:**
   ```bash
   uv run poe download-components
   ```

2. **Start dependencies (in separate terminal):**
   ```bash
   uv run poe start-deps
   ```

3. **Run SourceSense:**
   ```bash
   uv run main.py
   ```

4. **Access the application:**
   - **Web Interface**: http://localhost:8000
   - **Temporal UI**: http://localhost:8233

## 🎯 How to Use SourceSense

### 1. Configure Database Connection
- Select your database type (PostgreSQL, MySQL, SQLite, SQL Server)
- Enter connection details (host, port, database name, credentials)
- Test the connection before proceeding

### 2. Choose Analysis Options
- **Data Quality Analysis**: Enable comprehensive quality metrics
- **Sensitive Data Detection**: Identify potentially sensitive columns

### 3. Extract Metadata
- Click "Extract Metadata" to start the workflow
- Monitor real-time progress in the dashboard

### 4. Analyze Results
- **Schema Overview**: Explore database structure and relationships
- **Data Quality**: Assess data completeness and uniqueness
- **Relationships**: Understand foreign key dependencies

## 🏗️ Architecture

SourceSense follows Atlan's Apps Framework architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │    │   Workflow       │    │   Activities    │
│   (FastAPI)     │───▶│   (Temporal)     │───▶│   (SQLAlchemy)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Dapr Sidecar   │
                       │   (State Store)  │
                       └──────────────────┘
```

### Key Components
- **Frontend**: Modern responsive web interface with real-time updates
- **Workflow Engine**: Temporal-based orchestration for reliable metadata extraction
- **Database Connectors**: SQLAlchemy-powered multi-database connectivity
- **State Management**: Dapr-based distributed state store
- **Observability**: Comprehensive logging, metrics, and tracing

## 🔧 Development

### Stop Dependencies
```bash
uv run poe stop-deps
```

### Run Tests
```bash
uv run pytest
```

### Project Structure
```
sourcesense/
├── app/                    # Core application logic
│   ├── activities.py       # Database extraction activities
│   └── workflow.py         # Metadata extraction workflow
├── frontend/               # Web interface
│   ├── static/            # CSS, JavaScript, assets
│   └── templates/         # HTML templates
├── components/            # Dapr components configuration
├── deploy/               # Deployment configurations
├── tests/                # Test files
├── main.py              # Application entry point
├── pyproject.toml       # Dependencies and configuration
└── README.md           # This file
```

## 🎨 Supported Database Types

| Database | Connection String Example | Default Port |
|----------|---------------------------|--------------|
| PostgreSQL | `postgresql://user:pass@host:5432/db` | 5432 |
| MySQL | `mysql+pymysql://user:pass@host:3306/db` | 3306 |
| SQLite | `sqlite:///path/to/database.db` | N/A |
| SQL Server | `mssql+pyodbc://user:pass@host:1433/db` | 1433 |

---

**Built with ❤️ using Atlan's application-sdk Framework**
