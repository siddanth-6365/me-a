# 🏗️ Framework Notes

**Interesting Challenges and Patterns from SourceSense Development**

## 🚧 **Key Challenges & Solutions**

### **1. Workflow-Activity Communication**
**Challenge**: Understanding data flow between workflows and activities

**Solution**: Direct parameter passing with structured returns
```python
# Direct parameter passing
connection_test = await workflow.execute_activity(
    activities_instance.test_database_connection,
    connection_config,  # Direct parameter
    start_to_close_timeout=timedelta(seconds=30),
)

# Structured return values
return {
    "status": "success",
    "message": "Database connection successful",
    "timestamp": datetime.now().isoformat()
}
```

**Key Insight**: Data is passed directly as parameters; return values must be serializable.

### **2. Error Handling Across Layers**
**Challenge**: Implementing consistent error handling in workflows and activities

**Solution**: Structured error responses with status checking
```python
# Activity-level: Catch and return structured errors
try:
    # Activity logic
    return {"status": "success", "data": result}
except Exception as e:
    return {"status": "error", "message": str(e)}

# Workflow-level: Check results and decide continuation
if connection_test.get("status") != "success":
    results["status"] = "failed"
    return results
```

**Key Insight**: Activities should catch exceptions and return error status; workflows should check results and decide on continuation.

### **3. Sensitive Data Detection**
**Challenge**: Reliable identification of PII, financial, and health data in column names

**Solution**: Pattern-based detection with keyword matching
```python
sensitive_patterns = {
    "PII": ["email", "phone", "ssn", "address"],
    "Financial": ["credit", "card", "account", "balance"],
    "Health": ["medical", "health", "patient", "diagnosis"]
}
```

**Key Insight**: Pattern-based approach provides solid foundation that can be easily extended.

### **4. Large Dataset Processing**
**Challenge**: Timeout issues when processing large databases

**Solution**: Batch processing with configurable limits
```python
max_tables = analysis_options.get("max_tables_for_quality_analysis", 5)
for table in tables[:max_tables]:
    # Process table
```

**Key Insight**: Configurable limits prevent timeouts while providing valuable insights.

### **5. Frontend Integration with Temporal UI**
**Challenge**: Dynamic generation of Temporal UI links for specific workflow runs

**Solution**: Capture workflow/run IDs and construct URLs in frontend
```javascript
function showTestConnectionModal(workflowId, runId) {
    const temporalUrl = `http://localhost:8080/namespaces/default/workflows/${workflowId}/runs/${runId}`;
    // Update modal content
}
```

**Key Insight**: Dynamic URL construction gives users direct access to workflow execution logs.

### **6. Multi-Database Support**
**Challenge**: Supporting different database types with correct connection URLs

**Solution**: Centralized connection URL building based on database type
```python
def _build_connection_url(self, config: Dict[str, Any]) -> str:
    db_type = config.get("database_type", "postgresql")
    if db_type == "postgresql":
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    elif db_type == "mysql":
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    # ... other database types
```

**Key Insight**: Centralized logic keeps database handling maintainable and consistent.

## 🔄 **Key Patterns Discovered**

### **1. Activity Sequence with Dependency Checking**
```python
connection_test = await workflow.execute_activity(...)
if connection_test.get("status") != "success":
    return results  # Stop on failure

schema_metadata = await workflow.execute_activity(...)
if schema_metadata.get("status") == "error":
    return results  # Stop on error
```

**Benefit**: Clear execution flow with early failure detection.

### **2. Result Aggregation Pattern**
```python
results = {
    "workflow_id": workflow_config.get("workflow_id"),
    "status": "running",
    "steps_completed": [],
    "connection_test": None,
    "schema_metadata": None,
    # ... other results
}

# Populate as activities complete
results["connection_test"] = connection_test
results["steps_completed"].append("connection_test")
```

**Benefit**: Clear result structure with progress tracking.

### **3. Conditional Execution Based on Configuration**
```python
if analysis_options.get("analyze_data_quality", False):
    logger.info("Step 4: Analyzing data quality")
    # Execute data quality analysis
    results["data_quality"] = quality_analyses
```

**Benefit**: Flexible execution paths with user-controlled features.

### **4. Batch Processing for Large Datasets**
```python
max_tables = analysis_options.get("max_tables_for_quality_analysis", 5)
tables_to_analyze = []

for schema in schema_metadata.get("schemas", [])[:2]:
    for table in schema.get("tables", [])[:max_tables]:
        tables_to_analyze.append(table_info)
        if len(tables_to_analyze) >= max_tables:
            break
```

**Benefit**: Prevents timeouts and memory issues with large datasets.

## 🎯 **Framework-Specific Insights**

### **Temporal Integration**
- Activities are executed by workers (can be different processes)
- Workflows are deterministic and can be replayed
- State is managed by Temporal, not your application

### **Observability Integration**
- Logger, metrics, and traces must be initialized before use
- The decorator automatically instruments methods
- Correlation IDs are handled automatically

---

**Built with SourceSense using Atlan Apps Framework** 🚀
