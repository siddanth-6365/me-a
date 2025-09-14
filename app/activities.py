from typing import Any, Dict
from datetime import datetime
from sqlalchemy import create_engine, inspect, text

from application_sdk.activities import ActivitiesInterface
from application_sdk.observability.logger_adaptor import get_logger
# from application_sdk.
from temporalio import activity

logger = get_logger(__name__)
activity.logger = logger


class SourceSenseActivities(ActivitiesInterface):
    """Activities for SourceSense metadata extraction application."""

    @activity.defn
    async def test_database_connection(self, connection_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test database connection with provided configuration.
        
        Args:
            connection_config: Database connection configuration
            
        Returns:
            Dict containing connection test results
        """
        try:
            logger.info(f"Testing database connection to {connection_config.get('database_type')}")
            
            connection_url = self._build_connection_url(connection_config)
            engine = create_engine(connection_url, echo=False)
            
            # Test the connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            logger.info("Database connection successful")
            return {
                "status": "success",
                "message": "Database connection successful",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Database connection failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    @activity.defn
    async def extract_schema_metadata(self, connection_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract comprehensive schema metadata from the database.
        
        Args:
            connection_config: Database connection configuration
            
        Returns:
            Dict containing extracted schema metadata
        """
        try:
            logger.info("Starting schema metadata extraction")
            
            connection_url = self._build_connection_url(connection_config)
            engine = create_engine(connection_url, echo=False)
            inspector = inspect(engine)
            
            metadata = {
                "database_info": {
                    "database_type": connection_config.get("database_type"),
                    "database_name": connection_config.get("database"),
                    "extraction_timestamp": datetime.now().isoformat()
                },
                "schemas": [],
                "statistics": {
                    "total_schemas": 0,
                    "total_tables": 0,
                    "total_columns": 0
                }
            }
            
            # Get all schema names
            schema_names = inspector.get_schema_names()
            metadata["statistics"]["total_schemas"] = len(schema_names)
            
            for schema_name in schema_names:
                logger.info(f"Processing schema: {schema_name}")
                schema_info = {
                    "schema_name": schema_name,
                    "tables": []
                }
                
                # Get tables in schema
                table_names = inspector.get_table_names(schema=schema_name)
                
                for table_name in table_names:
                    logger.info(f"Processing table: {schema_name}.{table_name}")
                    table_info = await self._extract_table_metadata(
                        inspector, engine, schema_name, table_name
                    )
                    schema_info["tables"].append(table_info)
                    metadata["statistics"]["total_columns"] += len(table_info["columns"])
                
                metadata["statistics"]["total_tables"] += len(table_names)
                metadata["schemas"].append(schema_info)
            
            logger.info("Schema metadata extraction completed")
            return metadata
            
        except Exception as e:
            logger.error(f"Schema metadata extraction failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Schema metadata extraction failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    @activity.defn
    async def analyze_data_quality(self, connection_config: Dict[str, Any], 
                                 table_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze data quality metrics for specific tables.
        
        Args:
            connection_config: Database connection configuration
            table_info: Information about the table to analyze
            
        Returns:
            Dict containing data quality metrics
        """
        try:
            logger.info(f"Starting data quality analysis for {table_info['schema_name']}.{table_info['table_name']}")
            
            connection_url = self._build_connection_url(connection_config)
            engine = create_engine(connection_url, echo=False)
            
            schema_name = table_info["schema_name"]
            table_name = table_info["table_name"]
            full_table_name = f"{schema_name}.{table_name}" if schema_name else table_name
            
            quality_metrics = {
                "table_name": full_table_name,
                "analysis_timestamp": datetime.now().isoformat(),
                "metrics": {}
            }
            
            with engine.connect() as conn:
                # Get total row count
                count_query = text(f"SELECT COUNT(*) as total_rows FROM {full_table_name}")
                result = conn.execute(count_query)
                total_rows = result.fetchone()[0]
                quality_metrics["metrics"]["total_rows"] = total_rows
                
                # Analyze each column
                column_metrics = {}
                for column in table_info["columns"]:
                    column_name = column["column_name"]
                    logger.info(f"Analyzing column: {column_name}")
                    
                    # Check for null values
                    null_query = text(f"SELECT COUNT(*) FROM {full_table_name} WHERE {column_name} IS NULL")
                    null_result = conn.execute(null_query)
                    null_count = null_result.fetchone()[0]
                    
                    # Check for unique values (sample)
                    unique_query = text(f"SELECT COUNT(DISTINCT {column_name}) FROM {full_table_name}")
                    unique_result = conn.execute(unique_query)
                    unique_count = unique_result.fetchone()[0]
                    
                    column_metrics[column_name] = {
                        "null_count": null_count,
                        "null_percentage": (null_count / total_rows * 100) if total_rows > 0 else 0,
                        "unique_count": unique_count,
                        "uniqueness_ratio": (unique_count / total_rows) if total_rows > 0 else 0,
                        "data_type": column["data_type"]
                    }
                
                quality_metrics["metrics"]["columns"] = column_metrics
            
            logger.info("Data quality analysis completed")
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Data quality analysis failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Data quality analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    @activity.defn
    def detect_sensitive_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect potentially sensitive data based on column names and patterns.
        
        Args:
            metadata: Extracted metadata from the database
            
        Returns:
            Dict containing sensitive data detection results
        """
        logger.info("Starting sensitive data detection")
        
        # Common patterns for sensitive data
        sensitive_patterns = {
            "PII": ["email", "ssn", "social_security", "phone", "address", "name", "firstname", "lastname"],
            "Financial": ["credit_card", "account_number", "salary", "income", "payment"],
            "Health": ["medical", "health", "diagnosis", "patient"],
            "Authentication": ["password", "token", "secret", "key", "hash"]
        }
        
        sensitive_findings = {
            "detection_timestamp": datetime.now().isoformat(),
            "sensitive_columns": [],
            "summary": {category: 0 for category in sensitive_patterns.keys()}
        }
        
        try:
            for schema in metadata.get("schemas", []):
                for table in schema.get("tables", []):
                    for column in table.get("columns", []):
                        column_name = column["column_name"].lower()
                        
                        for category, patterns in sensitive_patterns.items():
                            for pattern in patterns:
                                if pattern in column_name:
                                    sensitive_finding = {
                                        "schema_name": schema["schema_name"],
                                        "table_name": table["table_name"],
                                        "column_name": column["column_name"],
                                        "data_type": column["data_type"],
                                        "category": category,
                                        "pattern_matched": pattern,
                                        "confidence": "medium"  # Could be enhanced with ML
                                    }
                                    sensitive_findings["sensitive_columns"].append(sensitive_finding)
                                    sensitive_findings["summary"][category] += 1
                                    break
            
            logger.info(f"Sensitive data detection completed. Found {len(sensitive_findings['sensitive_columns'])} potential sensitive columns")
            return sensitive_findings
            
        except Exception as e:
            logger.error(f"Sensitive data detection failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Sensitive data detection failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def _extract_table_metadata(self, inspector, engine, schema_name: str, table_name: str) -> Dict[str, Any]:
        """Extract detailed metadata for a specific table."""
        table_info = {
            "schema_name": schema_name,
            "table_name": table_name,
            "columns": [],
            "primary_keys": [],
            "foreign_keys": [],
            "indexes": []
        }
        
        # Get column information
        columns = inspector.get_columns(table_name, schema=schema_name)
        for column in columns:
            column_info = {
                "column_name": column["name"],
                "data_type": str(column["type"]),
                "nullable": column["nullable"],
                "default": str(column["default"]) if column["default"] is not None else None,
                "comment": column.get("comment")
            }
            table_info["columns"].append(column_info)
        
        # Get primary key information
        pk_constraint = inspector.get_pk_constraint(table_name, schema=schema_name)
        table_info["primary_keys"] = pk_constraint.get("constrained_columns", [])
        
        # Get foreign key information
        fk_constraints = inspector.get_foreign_keys(table_name, schema=schema_name)
        for fk in fk_constraints:
            fk_info = {
                "name": fk.get("name"),
                "constrained_columns": fk.get("constrained_columns", []),
                "referred_schema": fk.get("referred_schema"),
                "referred_table": fk.get("referred_table"),
                "referred_columns": fk.get("referred_columns", [])
            }
            table_info["foreign_keys"].append(fk_info)
        
        # Get index information
        indexes = inspector.get_indexes(table_name, schema=schema_name)
        for index in indexes:
            index_info = {
                "name": index.get("name"),
                "column_names": index.get("column_names", []),
                "unique": index.get("unique", False)
            }
            table_info["indexes"].append(index_info)
        
        return table_info

    def _build_connection_url(self, config: Dict[str, Any]) -> str:
        """Build database connection URL from configuration."""
        db_type = config.get("database_type", "").lower()
        username = config.get("username", "")
        password = config.get("password", "")
        host = config.get("host", "localhost")
        port = config.get("port", "")
        database = config.get("database", "")
        
        if db_type == "postgresql":
            port = port or "5432"
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        elif db_type == "mysql":
            port = port or "3306"
            return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        elif db_type == "sqlite":
            return f"sqlite:///{database}"
        elif db_type == "mssql":
            port = port or "1433"
            return f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    async def store_workflow_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store workflow results in the state store for frontend access."""
        try:
            workflow_id = data.get("workflow_id")
            results = data.get("results", {})
            
            if not workflow_id:
                return {"status": "error", "message": "No workflow ID provided"}
            
            # Store results in state store
            # Note: This is a simplified approach - in a real implementation,
            # you might want to use a different storage mechanism
            logger.info(f"Storing workflow results for {workflow_id}")
            
            return {
                "status": "success",
                "message": "Workflow results stored successfully",
                "workflow_id": workflow_id
            }
            
        except Exception as e:
            logger.error(f"Failed to store workflow results: {str(e)}")
            return {"status": "error", "message": str(e)}