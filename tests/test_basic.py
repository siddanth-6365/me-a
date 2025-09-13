import pytest
from app.activities import SourceSenseActivities
from app.workflow import SourceSenseWorkflow


class TestSourceSenseApplication:
    """Basic tests for SourceSense application components."""

    @pytest.fixture()
    def workflow(self) -> SourceSenseWorkflow:
        """Create a SourceSenseWorkflow instance for testing."""
        return SourceSenseWorkflow()

    @pytest.fixture()
    def activities(self) -> SourceSenseActivities:
        """Create a SourceSenseActivities instance for testing."""
        return SourceSenseActivities()

    def test_workflow_instantiation(self, workflow):
        """Test that workflow can be instantiated."""
        assert workflow is not None
        assert isinstance(workflow, SourceSenseWorkflow)

    def test_activities_instantiation(self, activities):
        """Test that activities can be instantiated."""
        assert activities is not None
        assert isinstance(activities, SourceSenseActivities)

    def test_workflow_get_activities(self, workflow, activities):
        """Test that workflow can get activities sequence."""
        activity_sequence = workflow.get_activities(activities)
        assert len(activity_sequence) == 5
        assert activities.test_database_connection in activity_sequence
        assert activities.extract_schema_metadata in activity_sequence
        assert activities.analyze_data_quality in activity_sequence
        assert activities.detect_sensitive_data in activity_sequence
        assert activities.get_workflow_args in activity_sequence

    def test_workflow_get_activities_invalid_type(self, workflow):
        """Test that workflow raises error for invalid activities type."""
        with pytest.raises(TypeError, match="Activities must be an instance of SourceSenseActivities"):
            workflow.get_activities("invalid_activities")

    def test_activities_connection_url_building(self, activities):
        """Test that activities can build connection URLs."""
        config = {
            "database_type": "postgresql",
            "username": "user",
            "password": "pass",
            "host": "localhost",
            "port": "5432",
            "database": "testdb"
        }
        
        url = activities._build_connection_url(config)
        expected = "postgresql://user:pass@localhost:5432/testdb"
        assert url == expected

    def test_activities_sensitive_data_detection(self, activities):
        """Test that activities can detect sensitive data."""
        metadata = {
            "schemas": [
                {
                    "schema_name": "public",
                    "tables": [
                        {
                            "table_name": "users",
                            "columns": [
                                {"column_name": "email", "data_type": "VARCHAR"},
                                {"column_name": "password", "data_type": "VARCHAR"},
                                {"column_name": "id", "data_type": "INTEGER"}
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = activities.detect_sensitive_data(metadata)
        assert "sensitive_columns" in result
        assert "summary" in result
        assert len(result["sensitive_columns"]) > 0  # Should find email and password
