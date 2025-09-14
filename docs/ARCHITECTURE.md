# 🏗️ SourceSense Architecture Notes

## High-Level Design Decisions

### 1. Atlan Apps Framework Choice

**Decision**: Built on Atlan's application-sdk framework
**Rationale**: 
- Built-in observability (logging, metrics, tracing)
- Built-in Temporal workflow orchestration
- Dapr for distributed state management
- Production-ready infrastructure

### 2. SQLAlchemy Database Abstraction

**Decision**: Used SQLAlchemy for database connectivity
**Rationale**:
- **Multi-Database Support**: Single codebase supports PostgreSQL, MySQL, SQLite, SQL Server
- **Type Safety**: Strong typing and validation for database operations
- **Connection Pooling**: Built-in connection management and pooling
- **Schema Introspection**: Rich metadata extraction capabilities
- **Mature Ecosystem**: Well-tested, production-ready ORM

**Trade-offs**:
- Performance overhead vs direct database drivers
- Learning curve for complex queries
- Additional abstraction layer

### 3. Activity-Based Architecture

**Decision**: Split functionality into discrete activities
**Rationale**:
- **Modularity**: Each activity has a single responsibility
- **Testability**: Individual activities can be tested in isolation
- **Reusability**: Activities can be reused across different workflows
- **Monitoring**: Granular observability for each operation
- **Error Handling**: Isolated failure points with specific error handling

**Activity Breakdown**:
- `test_database_connection`: Validates database connectivity
- `extract_schema_metadata`: Discovers database structure
- `detect_sensitive_data`: Identifies sensitive information patterns
- `analyze_data_quality`: Computes data quality metrics
- `get_workflow_args`: Retrieves workflow configuration

### 4. Configuration-Driven Design

**Decision**: Externalized configuration for database connections and analysis options
**Rationale**:
- **Flexibility**: Easy to support different database types and configurations
- **Security**: Sensitive credentials not hardcoded in application
- **Testability**: Different configurations for different environments
- **User Experience**: Dynamic configuration through web interface

### 5. Observability-First Approach

**Decision**: Comprehensive logging, metrics, and tracing throughout the application
**Rationale**:
- **Debugging**: Rich context for troubleshooting issues
- **Monitoring**: Real-time visibility into application health
- **Performance**: Metrics for identifying bottlenecks
- **Compliance**: Audit trails for sensitive data operations

**Implementation**:
- Structured logging with correlation IDs
- Custom metrics for workflow execution
- Distributed tracing across activities
- Error tracking and alerting

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI        │    │   Temporal      │
│   (HTML/JS)     │◄──►│   Server         │◄──►│   Workflows     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Activities     │
                       │   (SQLAlchemy)   │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Databases      │
                       │   (PostgreSQL,   │
                       │    MySQL, etc.)  │
                       └──────────────────┘
```

## Data Flow

1. **User Input**: Web interface captures database connection details and analysis options
2. **Workflow Initiation**: Temporal workflow is triggered with configuration
3. **Activity Execution**: Workflow orchestrates activities in sequence:
   - Connection testing
   - Schema metadata extraction
   - Sensitive data detection
   - Data quality analysis (optional)
4. **State Persistence**: Dapr stores intermediate results and final output
5. **Result Presentation**: Web interface displays extracted metadata and analysis results

## Error Handling Strategy

### Workflow Level
- **Retry Logic**: Automatic retries for transient failures
- **Circuit Breaker**: Prevents cascading failures
- **Graceful Degradation**: Continue processing even if some activities fail

### Activity Level
- **Input Validation**: Validate configuration before processing
- **Connection Timeouts**: Prevent hanging on unresponsive databases
- **Resource Cleanup**: Ensure database connections are properly closed

### Application Level
- **Health Checks**: Monitor application and dependency health
- **Graceful Shutdown**: Handle termination signals properly
- **Error Reporting**: Comprehensive error logging and alerting

## Security Considerations

### Data Protection
- **Connection Security**: Encrypted database connections
- **Credential Management**: Secure storage of database credentials
- **Data Minimization**: Only extract necessary metadata
- **Sensitive Data Detection**: Identify and flag sensitive information

### Access Control
- **Authentication**: Web interface authentication (if required)
- **Authorization**: Role-based access to different database sources
- **Audit Logging**: Track all metadata extraction activities

## Scalability Design

### Horizontal Scaling
- **Stateless Activities**: Activities can run on any worker
- **Distributed State**: Dapr state store supports multiple instances
- **Load Balancing**: Temporal can distribute work across workers

### Performance Optimization
- **Connection Pooling**: Reuse database connections
- **Async Processing**: Non-blocking I/O operations
- **Caching**: Cache frequently accessed metadata
- **Batch Processing**: Process multiple tables efficiently

## Future Considerations

### Extensibility
- **Plugin Architecture**: Easy addition of new database types
- **Custom Analyzers**: Support for custom data quality rules
- **Integration Points**: Hooks for external system integration

### Monitoring and Alerting
- **Real-time Dashboards**: Live monitoring of extraction jobs
- **Alerting Rules**: Proactive notification of issues
- **Performance Metrics**: Detailed performance analysis

### Compliance and Governance
- **Data Lineage**: Track data flow and transformations
- **Compliance Reporting**: Generate reports for regulatory requirements
- **Data Classification**: Automatic data classification based on content
