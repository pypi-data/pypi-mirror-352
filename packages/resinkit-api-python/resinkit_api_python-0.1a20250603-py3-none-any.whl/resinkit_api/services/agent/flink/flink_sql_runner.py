import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from resinkit_api.clients.job_manager.flink_job_manager_client import FlinkJobManager
from resinkit_api.clients.sql_gateway.flink_session import FlinkSession
from resinkit_api.clients.sql_gateway.flink_sql_gateway_client import FlinkSqlGatewayClient, FlinkSqlGatewayNotFoundException
from resinkit_api.clients.sql_gateway.flink_operation import FlinkOperation, ResultsFetchOpts
from resinkit_api.core.logging import get_logger
from resinkit_api.db.models import Task, TaskStatus
from resinkit_api.services.agent.flink.flink_resource_manager import FlinkResourceManager
from resinkit_api.services.agent.flink.flink_sql_task import FlinkSQLTask
from resinkit_api.services.agent.task_base import TaskBase
from resinkit_api.services.agent.task_runner_base import TaskRunnerBase, LogEntry
from resinkit_api.services.agent.data_models import TaskExecutionError, FlinkJobStatus, map_flink_status_to_task_status
from resinkit_api.services.agent.common.log_file_manager import LogFileManager
import pandas as pd
import json

logger = get_logger(__name__)

DEFAULT_POLLING_OPTIONS = ResultsFetchOpts(
    max_poll_secs=30,
    poll_interval_secs=0.5,
    n_row_limit=100,
)


def _df_to_json(df: pd.DataFrame) -> Dict[str, Any]:
    return json.loads(df.to_json(orient="records", date_format="iso"))


class FlinkSQLRunner(TaskRunnerBase):
    """Runner for executing Flink SQL jobs via the SQL Gateway."""

    def __init__(self, job_manager: FlinkJobManager, sql_gateway_client: FlinkSqlGatewayClient, runtime_env: dict | None = None):
        """
        Initialize the Flink SQL Runner.

        Args:
            job_manager: FlinkJobManager instance for job management
            sql_gateway_client: FlinkSqlGatewayClient instance for SQL Gateway interaction
            runtime_env: Optional runtime environment configuration
        """
        super().__init__(runtime_env or {})
        self.job_manager = job_manager
        self.sql_gateway_client = sql_gateway_client
        self.resource_manager = FlinkResourceManager()
        self.tasks: Dict[str, FlinkSQLTask] = {}

    @classmethod
    def validate_config(cls, task_config: dict) -> None:
        """
        Validates the configuration for running a Flink SQL job.

        Args:
            task_config: The task configuration dictionary

        Raises:
            ValueError: If the configuration is invalid
        """
        try:
            FlinkSQLTask.validate(task_config)
        except Exception as e:
            raise ValueError(f"Invalid Flink SQL configuration: {str(e)}")

    def from_dao(self, dao: Task, variables: Dict[str, Any] | None = None) -> FlinkSQLTask:
        """
        Create a FlinkSQLRunner instance from a Task DAO.

        Args:
            dao: The Task DAO

        Returns:
            The FlinkSQLRunner instance
        """
        return FlinkSQLTask.from_dao(dao, variables)

    async def submit_task(self, task: FlinkSQLTask) -> FlinkSQLTask:
        """
        Submits a Flink SQL job to the SQL Gateway.

        Args:
            task: The task instance

        Returns:
            The created task instance, with updated:
            - status
            - result_summary
            - execution_details
            - if failed, error_info will be set

        Raises:
            TaskExecutionError: If job submission fails
        """
        task_id = task.task_id
        self.tasks[task_id] = task

        # Process resources
        resources = await self.resource_manager.process_resources(task.resources)

        lfm = LogFileManager(task.log_file, limit=1000, logger=logger)

        try:
            # Update task status
            task.status = TaskStatus.RUNNING
            if task.result_summary is None:
                task.result_summary = {}
            if task.result_summary.get("results") is None:
                task.result_summary["results"] = []
            if task.result_summary.get("job_ids") is None:
                task.result_summary["job_ids"] = []
            if task.result_summary.get("is_query") is None:
                task.result_summary["is_query"] = []
            lfm.info(f"Starting Flink SQL job: {task.name}")

            # Create session properties
            session_properties = self._create_session_properties(task, resources)
            session_name = f"session_{task_id}"

            # Create and open a session; no need to close it, going to reuse it
            with self.sql_gateway_client.get_session(
                properties=session_properties,
                session_name=session_name,
                create_if_not_exist=True,
            ) as session:
                lfm.info(f"Created Flink SQL session: {session_name}")
                # Execute each SQL statement
                operation_handles = []
                for i, sql in enumerate(task.sql_statements):
                    lfm.info(f"Executing SQL statement {i+1}/{len(task.sql_statements)}")
                    lfm.info(f"SQL: {sql}")

                    # Execute the statement
                    async with session.execute(sql).asyncio() as operation:
                        # Store the operation handle for later status checks
                        operation_handles.append(operation.operation_handle)
                        result_df, res_data = await operation.fetch(
                            polling_opts=ResultsFetchOpts(
                                max_poll_secs=task.connection_timeout_seconds,
                                poll_interval_secs=0.5,
                                n_row_limit=100,
                            )
                        ).asyncio()
                        lfm.info(f"Results: {result_df.to_string()}")
                        task.result_summary["results"].append(_df_to_json(result_df))
                        task.result_summary["job_ids"].append(res_data.job_id)
                        task.result_summary["is_query"].append(res_data.is_query_result)

                        # If job_id is available, fetch additional job information
                        if res_data.job_id:
                            try:
                                # Get job exceptions
                                job_exceptions = await self.job_manager.get_job_exceptions(res_data.job_id)
                                if job_exceptions:
                                    lfm.info(f"Job exceptions for {res_data.job_id}: {job_exceptions}")
                                    if "job_exceptions" not in task.result_summary:
                                        task.result_summary["job_exceptions"] = []
                                    task.result_summary["job_exceptions"].append(job_exceptions)
                                else:
                                    if "job_exceptions" not in task.result_summary:
                                        task.result_summary["job_exceptions"] = []
                                    task.result_summary["job_exceptions"].append(None)
                            except Exception as e:
                                lfm.error(f"Failed to fetch job information for {res_data.job_id}: {str(e)}")

                        # Get the operation status
                        status = await operation.status().asyncio()
                        lfm.info(f"Operation status: {status.status}")
                        # if this is the last and the status is "FINISHED"
                        if i == len(task.sql_statements) - 1 and status.status == "FINISHED":
                            task.status = TaskStatus.COMPLETED
                            lfm.info(f"Flink SQL job completed successfully, name: {task.name}, id: {task.task_id}")
                        else:
                            lfm.info(f"Flink SQL job submitted successfully, name: {task.name}, id: {task.task_id}, status: {status.status}")

            # Update execution_details with important execution information
            task.execution_details = {
                "log_file": task.log_file,
                "session_name": session_name,
                "session_id": session.session_handle,
                "operation_ids": operation_handles,
                "job_ids": [jid for jid in task.result_summary.get("job_ids", []) if jid],
            }
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_info = {"error": str(e), "error_type": e.__class__.__name__, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            lfm.error(f"Failed to submit Flink SQL job: {str(e)}")
        return task

    def get_status(self, task: TaskBase) -> TaskStatus:
        """
        Gets the status of a submitted Flink SQL job.

        Args:
            task: The task instance

        Returns:
            The task status
        """
        if not task:
            return TaskStatus.UNKNOWN
        return task.status

    def get_result(self, task: FlinkSQLTask) -> Optional[Any]:
        """
        Gets the result of a completed Flink SQL job.

        Args:
            task: The task instance

        Returns:
            The task result
        """
        if not task:
            return None
        return task.result

    def get_log_summary(self, task: FlinkSQLTask, level: str = "INFO") -> List[LogEntry]:
        """
        Gets a summary of logs for a Flink SQL job.

        Args:
            task: The task instance
            level: The log level to filter by

        Returns:
            A list of log entries
        """
        if not task or not task.log_file or not os.path.exists(task.log_file):
            return []

        try:
            lfm = LogFileManager(task.log_file, limit=1000, logger=logger)
            entries = lfm.get_entries(level=level)
            return entries
        except Exception as e:
            logger.error(f"Failed to read logs for task {task.task_id}: {str(e)}")
            return [LogEntry(timestamp=datetime.now().timestamp(), level="ERROR", message=f"Error reading logs: {str(e)}")]

    async def cancel(self, task: FlinkSQLTask, force: bool = False) -> FlinkSQLTask:
        """
        Cancels a running Flink SQL job.

        Args:
            task: The task instance
            force: Whether to force cancel the job

        Returns:
            The updated task instance

        Raises:
            TaskExecutionError: If cancellation fails
        """
        if not task:
            logger.warning(f"Task {task.task_id} not found")
            return task

        lfm = LogFileManager(task.log_file, limit=1000, logger=logger)
        try:
            await self.job_manager.cancel_all_jobs(task.get_job_ids())
            lfm.info(f"Successfully cancelled all jobs for task {task.task_id}")
            await self.sql_gateway_client.cancel_all_operations(task.get_session_id(), task.get_operation_ids())
            lfm.info(f"Successfully cancelled all operations for task {task.task_id}")
            return task
        except FlinkSqlGatewayNotFoundException:
            lfm.warning(f"Session or operation not found for task {task.task_id}")
        except Exception as e:
            lfm.error(f"Failed to cancel task {task.task_id}: {str(e)}")
        return await self.fetch_task_status(task)

    async def shutdown(self):
        """Shutdown the runner, cancel all tasks and clean up resources."""
        logger.info("Shutting down Flink SQL Runner")

        # Cancel all running tasks
        running_tasks = [task_id for task_id, task in self.tasks.items() if task.status in [TaskStatus.RUNNING, TaskStatus.PENDING]]

        for task_id in running_tasks:
            lfm = LogFileManager(self.tasks[task_id].log_file, limit=1000, logger=logger)
            try:
                logger.info(f"Cancelling task {task_id} during shutdown")
                updated_task = await self.cancel(self.tasks[task_id], force=True)
                # Update our local tasks dict with the updated task
                self.tasks[task_id] = updated_task
            except Exception as e:
                lfm.error(f"Error cancelling task {task_id} during shutdown: {str(e)}")
        # Clean up resources
        try:
            self.resource_manager.cleanup()
            logger.info("Resource manager cleanup completed")
        except Exception as e:
            logger.error(f"Error cleaning up resources: {str(e)}")

    def _create_session_properties(self, task: FlinkSQLTask, resources: Dict[str, List[str]]) -> Dict[str, str]:
        """
        Create session properties for the Flink SQL Gateway.

        Args:
            task: The task instance
            resources: Processed resources

        Returns:
            Dictionary of session properties
        """
        properties = {}

        # Add jar paths
        if resources.get("jar_paths"):
            jar_paths = ";".join(resources["jar_paths"])
            properties["pipeline.jars"] = jar_paths

        # Add classpath jars
        if resources.get("classpath_jars"):
            classpath_jars = ";".join(resources["classpath_jars"])
            properties["pipeline.classpaths"] = classpath_jars

        # Set parallelism
        properties["parallelism.default"] = str(task.parallelism)

        # Add execution mode (we're using streaming for SQL Gateway)
        properties["execution.runtime-mode"] = "streaming"

        # Set pipeline name
        properties["pipeline.name"] = task.pipeline_name

        return properties

    async def fetch_task_status(self, task: FlinkSQLTask) -> FlinkSQLTask:
        """
        Fetches the latest status of a Flink SQL task.

        Args:
            task: The task instance

        Returns:
            An updated task instance with the latest status, result_summary, error_info, and execution_details

        Raises:
            TaskExecutionError: If fetching status fails
        """
        if not task:
            logger.warning(f"Task {task.task_id} not found")
            return None

        if task.all_jobs_finished():
            return task

        lfm = LogFileManager(task.log_file, limit=1000, logger=logger)
        session_id = task.get_session_id()
        operation_ids = task.get_operation_ids()
        job_ids = task.get_job_ids()

        if not job_ids and not operation_ids:
            lfm.warning(f"No job IDs or operation IDs found for task {task.task_id}, consider task completed")
            task.status = TaskStatus.COMPLETED
            return task

        if job_ids and self.job_manager:
            # Use Flink job statuses as the source of truth
            try:
                task = await self._determine_task_status_from_flink_jobs(task, job_ids, lfm)
            except Exception as e:
                lfm.error(f"Error fetching Flink job statuses for task {task.task_id}: {str(e)}")
                # Fall back to session/operation status check
                task = await self._determine_task_status_from_session(task, session_id, operation_ids, lfm)
        else:
            # Fall back to session/operation status check
            task = await self._determine_task_status_from_session(task, session_id, operation_ids, lfm)

        return task

    async def _determine_task_status_from_flink_jobs(self, task: FlinkSQLTask, job_ids: List[str], lfm) -> FlinkSQLTask:
        """
        Determine task status based on Flink job statuses.

        Logic:
        - If any job is still running/created/restarting -> RUNNING
        - If all jobs are finished -> COMPLETED
        - If all jobs are failed -> FAILED
        - If any job is cancelled -> CANCELLED
        - Mixed states with some failures -> FAILED
        """
        # map of job_id to job execution result
        job_results = {}
        task_statuses: list[TaskStatus] = []
        job_statuses: list[FlinkJobStatus] = []

        # Fetch status for all jobs
        for job_id in job_ids:
            if not job_id:  # Skip None/empty job IDs
                continue

            try:
                job_details = await self.job_manager.get_job_execution_result(job_id)
                if job_details:
                    # Extract status from the execution-result response
                    # job_details is a JobExecutionResult Pydantic model, not a dict
                    job_status_str = (job_details.status or "").upper()

                    # Convert string to FlinkJobStatus enum
                    try:
                        flink_status = FlinkJobStatus(job_status_str)
                    except ValueError:
                        # Handle unknown status by defaulting to RUNNING
                        lfm.warning(f"Unknown Flink job status: {job_status_str}, defaulting to RUNNING")
                        flink_status = FlinkJobStatus.RUNNING

                    # Map to TaskStatus
                    task_status = map_flink_status_to_task_status(flink_status, job_details.raw_response)
                    error_info = None
                    if task_status == TaskStatus.FAILED:
                        error_info = await self.job_manager.get_job_exceptions(job_id)

                    job_results[job_id] = {
                        "status": flink_status.value,
                        "task_status": task_status.value,
                        "error_info": error_info,
                    }
                    task_statuses.append(task_status)
                    job_statuses.append(flink_status)
                    lfm.info(f"Job {job_id} status: {flink_status.value} -> {task_status.value}")
                else:
                    lfm.warning(f"Could not fetch details for job {job_id}")
                    # Job not found, assume it completed or was cleaned up
                    job_results[job_id] = {
                        "status": FlinkJobStatus.FINISHED.value,
                        "task_status": TaskStatus.COMPLETED.value,
                    }
                    task_statuses.append(TaskStatus.COMPLETED)
                    job_statuses.append(FlinkJobStatus.FINISHED)
            except Exception as e:
                lfm.error(f"Error fetching status for job {job_id}: {str(e)}")
                # If we can't get status, assume job failed
                job_results[job_id] = {
                    "status": FlinkJobStatus.FAILED.value,
                    "task_status": TaskStatus.FAILED.value,
                }
                task_statuses.append(TaskStatus.FAILED)
                job_statuses.append(FlinkJobStatus.FAILED)

        if not job_results:
            # No job statuses available, keep current status
            return task

        task.result_summary["job_results"] = job_results
        task.result_summary["all_jobs_finished"] = all(status.is_terminal() for status in job_statuses)

        # Apply logic based on task statuses
        # Check for running jobs first (highest priority)
        if any(status == TaskStatus.RUNNING for status in task_statuses):
            task.status = TaskStatus.RUNNING
            return task

        # Check for cancelled jobs
        if any(status == TaskStatus.CANCELLED for status in task_statuses):
            task.status = TaskStatus.CANCELLED
            return task

        # Check if all jobs are completed
        if all(status == TaskStatus.COMPLETED for status in task_statuses):
            task.status = TaskStatus.COMPLETED
            return task

        # Check if any job is failed
        if any(status == TaskStatus.FAILED for status in task_statuses):
            task.status = TaskStatus.FAILED
            return task

        # Default: keep current status if we can't determine a clear state
        lfm.warning(f"Could not determine clear status from job statuses: {[status.value for status in task_statuses]}")
        return task

    async def _determine_task_status_from_session(self, task: FlinkSQLTask, session_id: str, operation_ids: List[str], lfm) -> FlinkSQLTask:
        """
        Fallback method to determine task status from session/operation status.
        """
        if not session_id or not operation_ids:
            lfm.warning(f"No session or operation ID found for task {task.task_id}")
            return task

        try:
            # Check the last operation status
            operation_id = operation_ids[-1]
            session_status = await self.sql_gateway_client.get_operation_status(session_id, operation_id)
            if session_status:
                task.status = TaskStatus.from_str(session_status)
                lfm.info(f"Session operation status for task {task.task_id}: {task.status.value}")
            else:
                lfm.warning(f"Could not get session operation status for task {task.task_id}")
                # If we can't get the operation status, it might have been cleaned up
                # In this case, don't change the status unless we know it failed
                if task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    task.status = TaskStatus.COMPLETED  # Assume completed if operation is gone
        except FlinkSqlGatewayNotFoundException:
            lfm.warning(f"Session or operation not found for task {task.task_id}")
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            lfm.error(f"Error fetching status for task {task.task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
        return task
