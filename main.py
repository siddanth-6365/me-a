import asyncio

from app.activities import SourceSenseActivities
from app.workflow import SourceSenseWorkflow
from application_sdk.application import BaseApplication
from application_sdk.observability.decorators.observability_decorator import (
    observability,
)
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import get_metrics
from application_sdk.observability.traces_adaptor import get_traces

logger = get_logger(__name__)
metrics = get_metrics()
traces = get_traces()

APPLICATION_NAME = "sourcesense"


@observability(logger=logger, metrics=metrics, traces=traces)
async def main():
    logger.info("Starting SourceSense application")
   
    app = BaseApplication(name=APPLICATION_NAME)

    # setup workflow
    await app.setup_workflow(
        workflow_and_activities_classes=[(SourceSenseWorkflow, SourceSenseActivities)],
    )

    # start worker
    await app.start_worker()

    # Setup the application server
    await app.setup_server(workflow_class=SourceSenseWorkflow)

    # start server
    await app.start_server()


if __name__ == "__main__":
    asyncio.run(main())
