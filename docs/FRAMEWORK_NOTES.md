# 🏗️ Framework Notes

**Interesting Challenges and Patterns from SourceSense Development**

## 🚧 **Key Challenges**

### **1. Observability Decorator Redundancy**
**Challenge**: Understanding why `@observability` decorator is needed in both `main.py` and `workflow.py`

**Pattern**: 
- `main.py`: Application-level observability (startup, shutdown, overall health)
- `workflow.py`: Workflow-level observability (execution steps, activity calls, progress tracking)

**Key Insight**: Both decorators are necessary for comprehensive, hierarchical observability coverage.

### **2. Activity Method Decoration Confusion**
**Challenge**: Understanding when to use `@activity.defn` vs regular methods

**Pattern**:
```python
class SourceSenseActivities(ActivitiesInterface):
    @activity.defn  # Required for Temporal execution
    async def test_database_connection(self, config):
        # Activity implementation
    
    def _build_connection_url(self, config):  # Helper method - no decoration
        # Internal logic
```

**Key Insight**: Only methods executed by Temporal need `@activity.defn`; helper methods should not be decorated.

### **3. Workflow-Activity Communication**
**Challenge**: Understanding data flow between workflows and activities

**Pattern**:
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

### **4. Error Handling Across Layers**
**Challenge**: Implementing consistent error handling in workflows and activities

**Pattern**:
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

## 🔄 **Interesting Patterns**

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

### **Dapr Integration**
- Components are configured but not actively used
- State management is handled by Temporal
- Future enhancement opportunity for caching and persistence

### **Observability Integration**
- Logger, metrics, and traces must be initialized before use
- The decorator automatically instruments methods
- Correlation IDs are handled automatically

## 🚀 **Best Practices Discovered**

1. **Activity Design**: Keep focused, use helper methods, return structured responses
2. **Workflow Design**: Sequential execution with dependency checking, proper error handling
3. **Configuration**: Use structured objects, validate early, pass through workflow parameters
4. **Error Handling**: Return structured error responses, log at appropriate levels
5. **Testing**: Mock external dependencies, test activities in isolation

## 🔮 **Future Enhancements**

- Implement Dapr state store for caching
- Publish workflow completion events
- Use Dapr secret store for credentials
- Add custom metrics and health checks

---

**Built with SourceSense using Atlan Apps Framework** 🚀
