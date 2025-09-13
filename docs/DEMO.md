# 🎯 SourceSense Demo Instructions

This guide provides step-by-step instructions to test SourceSense with sample data and demonstrate its key features.

## Prerequisites

- SourceSense application running (see main README.md for setup)
- Access to a test database or ability to create one

## Demo

### Using PostgreSQL Demo Database

#### 1.1 Setup Sample Database

Create a sample PostgreSQL database with test data:

```sql
-- can use the sample_db_setup.sql file
\i ./docs/sample_db_setup.sql
```

#### 1.2 Test App

1. **Open Web Interface**: Navigate to http://localhost:8000

2. **Configure Database Connection**:

   - Database Type: `PostgreSQL`
   - Host: `localhost` (or your PostgreSQL host)
   - Port: `5432`
   - Database: `sourcesense_demo`
   - Username: `your_postgres_username`
   - Password: `your_postgres_password`

3. **Test Connection**: Click "Test Connection" to verify connectivity

4. **Configure Analysis Options**:

   - ✅ Enable Data Quality Analysis
   - ✅ Enable Sensitive Data Detection
   - Max Tables for Quality Analysis: `3`

5. **Extract Metadata**: Click "Extract Metadata" and observe:
   - Schema discovery results
   - Sensitive data detection findings
   - Data quality metrics

#### 1.3 Expected Results

**Schema Discovery**:

- 3 tables: `users`, `orders`, `products`
- 1 schema: `public`
- Multiple columns with various data types

**Sensitive Data Detection**:

- `email` column → PII category
- `password_hash` column → Authentication category
- `first_name`, `last_name` columns → PII category
- `phone_number` column → PII category
- `date_of_birth` column → PII category

**Data Quality Metrics**:

- Row counts for each table
- Null counts and percentages
- Uniqueness ratios
- Data type consistency