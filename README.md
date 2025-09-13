# 🔍 SourceSense

**Intelligent Database Metadata Extraction & Analysis**

SourceSense is a comprehensive data source application built using Atlan's Apps Framework. It connects to SQL databases and demonstrates intelligent metadata extraction, providing deep insights into database schemas, data quality, and potential sensitive data.

![SourceSense Dashboard](https://via.placeholder.com/800x400/2563eb/ffffff?text=SourceSense+Dashboard)

## 🚀 Features

### Core Capabilities
- **Multi-Database Support**: PostgreSQL, MySQL, SQLite, SQL Server
- **Schema Discovery**: Comprehensive table, column, and relationship mapping
- **Intelligent Metadata Extraction**: 
  - Column names, data types, constraints
  - Primary keys and foreign key relationships
  - Index information and table statistics

### Advanced Analytics
- **Sensitive Data Detection**: AI-powered identification of PII, financial, health, and authentication data
- **Data Quality Metrics**: Null counts, uniqueness ratios, and quality scoring
- **Relationship Mapping**: Foreign key relationships and data lineage insights

### Modern Interface
- **Interactive Dashboard**: Real-time extraction progress and results
- **Tabbed Results View**: Schema overview, sensitive data alerts, quality metrics
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 📋 Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [Dapr CLI](https://docs.dapr.io/getting-started/install-dapr-cli/)
- [Temporal CLI](https://docs.temporal.io/cli)

### Installation Guides
- [macOS Setup Guide](https://github.com/atlanhq/application-sdk/blob/main/docs/docs/setup/MAC.md)
- [Linux Setup Guide](https://github.com/atlanhq/application-sdk/blob/main/docs/docs/setup/LINUX.md)
- [Windows Setup Guide](https://github.com/atlanhq/application-sdk/blob/main/docs/docs/setup/WINDOWS.md)

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
   - **SourceSense Web Interface**: http://localhost:8000
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
- View detailed results across multiple tabs

### 4. Analyze Results
- **Schema Overview**: Explore database structure and relationships
- **Sensitive Data**: Review flagged columns with security implications
- **Data Quality**: Assess data completeness and uniqueness
- **Relationships**: Understand foreign key dependencies

## 📊 Sample Use Cases

### Enterprise Data Discovery
```bash
# Connect to production PostgreSQL
Database Type: PostgreSQL
Host: prod-db.company.com
Port: 5432
Database: enterprise_data
```

### Data Governance & Compliance
- Automatically identify PII columns for GDPR compliance
- Generate data quality reports for data stewardship
- Map data lineage for impact analysis

### Database Migration Planning
- Extract comprehensive schema information
- Identify data quality issues before migration
- Document relationships and dependencies

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

## 🔐 Security Features

### Sensitive Data Detection
SourceSense automatically identifies potentially sensitive columns based on:
- **PII Patterns**: email, ssn, phone, address, names
- **Financial Data**: credit_card, account_number, salary
- **Health Information**: medical, health, diagnosis, patient
- **Authentication**: password, token, secret, key

### Data Quality Scoring
- **Null Percentage Analysis**: Identifies incomplete data
- **Uniqueness Metrics**: Detects duplicate and inconsistent values
- **Quality Scoring**: Excellent, Good, or Needs Attention ratings

## 📚 Learning Resources

- [Atlan Application SDK Documentation](https://github.com/atlanhq/application-sdk/tree/main/docs)
- [Temporal Documentation](https://docs.temporal.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Dapr Documentation](https://docs.dapr.io/)

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the [Atlan SDK Documentation](https://github.com/atlanhq/application-sdk/tree/main/docs)
2. Open an issue in this repository
3. Contact the Atlan team at connect@atlan.com

---

**Built with ❤️ using Atlan's Apps Framework**