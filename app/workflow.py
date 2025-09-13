import asyncio
from datetime import timedelta
from typing import Any, Callable, Coroutine, Dict, List, Sequence

from app.activities import SourceSenseActivities
from application_sdk.activities import ActivitiesInterface
from application_sdk.observability.decorators.observability_decorator import (
    observability,
)
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import get_metrics
from application_sdk.observability.traces_adaptor import get_traces
from application_sdk.workflows import WorkflowInterface
from temporalio import workflow

logger = get_logger(__name__)
workflow.logger = logger
metrics = get_metrics()
traces = get_traces()


@workflow.defn
class SourceSenseWorkflow(WorkflowInterface):
    """Main workflow for SourceSense metadata extraction application."""

    @observability(logger=logger, metrics=metrics, traces=traces)
    @workflow.run
    async def run(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the SourceSense metadata extraction workflow.

        Args:
            workflow_config (Dict[str, Any]): The workflow configuration

        Returns:
            Dict[str, Any]: The workflow execution results
        """
        logger.info("Starting SourceSense metadata extraction workflow")
        
        activities_instance = SourceSenseActivities()

        # Get the workflow configuration from the state store
        workflow_args: Dict[str, Any] = await workflow.execute_activity_method(
            activities_instance.get_workflow_args,
            workflow_config,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # Extract connection configuration
        connection_config = workflow_args.get("connection_config", {})
        analysis_options = workflow_args.get("analysis_options", {})
        is_test_only = analysis_options.get("test_only", False)
        
        logger.info(f"Processing database: {connection_config.get('database_type', 'Unknown')}")
        if is_test_only:
            logger.info("Running connection test only")

        results = {
            "workflow_id": workflow_config.get("workflow_id"),
            "status": "running",
            "steps_completed": [],
            "connection_test": None,
            "schema_metadata": None,
            "data_quality": None,
            "sensitive_data": None,
            "execution_summary": {}
        }

        try:
            # Step 1: Test database connection
            logger.info("Step 1: Testing database connection")
            connection_test = await workflow.execute_activity(
                activities_instance.test_database_connection,
                connection_config,
                start_to_close_timeout=timedelta(seconds=30),
            )
            results["connection_test"] = connection_test
            results["steps_completed"].append("connection_test")

            if connection_test.get("status") != "success":
                logger.error("Database connection failed, stopping workflow")
                results["status"] = "failed"
                results["error"] = "Database connection failed"
                return results

            # If this is a test-only run, return after connection test
            if is_test_only:
                logger.info("Connection test completed successfully, test-only mode")
                results["status"] = "completed"
                results["execution_summary"] = {"test_only": True, "connection_successful": True}
                return results

            # Step 2: Extract schema metadata
            logger.info("Step 2: Extracting schema metadata")
            schema_metadata = await workflow.execute_activity(
                activities_instance.extract_schema_metadata,
                connection_config,
                start_to_close_timeout=timedelta(minutes=10),
            )
            results["schema_metadata"] = schema_metadata
            results["steps_completed"].append("schema_extraction")

            if schema_metadata.get("status") == "error":
                logger.error("Schema metadata extraction failed")
                results["status"] = "failed"
                results["error"] = "Schema metadata extraction failed"
                return results

            # Step 3: Detect sensitive data
            logger.info("Step 3: Detecting sensitive data")
            sensitive_data = await workflow.execute_activity(
                activities_instance.detect_sensitive_data,
                schema_metadata,
                start_to_close_timeout=timedelta(minutes=5),
            )
            results["sensitive_data"] = sensitive_data
            results["steps_completed"].append("sensitive_data_detection")

            # Step 4: Analyze data quality (optional, for selected tables)
            if analysis_options.get("analyze_data_quality", False):
                logger.info("Step 4: Analyzing data quality")
                
                # Get a sample of tables to analyze (limit to prevent long execution)
                tables_to_analyze = []
                max_tables = analysis_options.get("max_tables_for_quality_analysis", 5)
                
                for schema in schema_metadata.get("schemas", [])[:2]:  # Limit to first 2 schemas
                    for table in schema.get("tables", [])[:max_tables]:
                        tables_to_analyze.append({
                            "schema_name": schema["schema_name"],
                            "table_name": table["table_name"],
                            "columns": table["columns"]
                        })
                        if len(tables_to_analyze) >= max_tables:
                            break
                    if len(tables_to_analyze) >= max_tables:
                        break

                # Analyze quality for selected tables
                quality_analyses = []
                for table_info in tables_to_analyze:
                    try:
                        quality_result = await workflow.execute_activity(
                            activities_instance.analyze_data_quality,
                            connection_config,
                            table_info,
                            start_to_close_timeout=timedelta(minutes=3),
                        )
                        quality_analyses.append(quality_result)
                    except Exception as e:
                        logger.warning(f"Quality analysis failed for table {table_info['table_name']}: {str(e)}")
                
                results["data_quality"] = quality_analyses
                results["steps_completed"].append("data_quality_analysis")

            # Generate execution summary
            results["execution_summary"] = self._generate_execution_summary(results)
            results["status"] = "completed"


            logger.info("SourceSense metadata extraction workflow completed successfully")
            return results

        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
            return results

    def _generate_execution_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the workflow execution results."""
        summary = {
            "total_steps": len(results["steps_completed"]),
            "completion_status": results["status"]
        }

        # Schema metadata summary
        if results.get("schema_metadata"):
            metadata = results["schema_metadata"]
            if metadata.get("statistics"):
                summary.update({
                    "total_schemas": metadata["statistics"].get("total_schemas", 0),
                    "total_tables": metadata["statistics"].get("total_tables", 0),
                    "total_columns": metadata["statistics"].get("total_columns", 0)
                })

        # Sensitive data summary
        if results.get("sensitive_data"):
            sensitive = results["sensitive_data"]
            summary["sensitive_columns_found"] = len(sensitive.get("sensitive_columns", []))
            summary["sensitive_categories"] = sensitive.get("summary", {})

        # Data quality summary
        if results.get("data_quality"):
            quality_data = results["data_quality"]
            summary["tables_analyzed_for_quality"] = len(quality_data) if isinstance(quality_data, list) else 0

        return summary

    @staticmethod
    def get_activities(activities: ActivitiesInterface) -> Sequence[Callable[..., Any]]:
        """Get the sequence of activities to be executed by the workflow.

        Args:
            activities (ActivitiesInterface): The activities instance
                containing the SourceSense operations.

        Returns:
            Sequence[Callable[..., Any]]: A sequence of activity methods to be executed.
        """
        if not isinstance(activities, SourceSenseActivities):
            raise TypeError("Activities must be an instance of SourceSenseActivities")

        return [
            activities.test_database_connection,
            activities.extract_schema_metadata,
            activities.analyze_data_quality,
            activities.detect_sensitive_data,
            activities.get_workflow_args,
        ]