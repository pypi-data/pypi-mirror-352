from pathlib import Path

import pandas as pd
from loguru import logger

from igx_api.l1 import openapi_client
from igx_api.l2.client.api.file_api import FileApi
from igx_api.l2.events.workflow_execution_task_waitable import WorkflowExecutionTaskWaitable
from igx_api.l2.types.api_error import ApiError, ApiErrorContext
from igx_api.l2.types.cluster import ClusterId, ClusterRunId
from igx_api.l2.types.execution import Execution
from igx_api.l2.types.job import JobState
from igx_api.l2.types.log import LogLevel
from igx_api.l2.types.tree import Tree
from igx_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName


class TreeApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_trees_by_job_id(self, job_id: WorkflowExecutionTaskId) -> list[Tree]:
        """Get the calculated trees for a tree calculation.

        Args:
            job_id (igx_api.l2.types.job.JobId): The tree job id

        Returns:
            list[igx_api.l2.types.tree.Tree]: The calculated trees.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
                job_id = JobId(456)
                trees = self.get_trees_by_job_id(job_id=job_id)
            ```
        """

        tree_api_instance = openapi_client.TreeApi(self._inner_api_client)

        try:
            return [Tree.from_raw(i) for i in tree_api_instance.get_trees_by_job_id(job_id=job_id).trees]
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def start(self, cluster_run_id: ClusterRunId, cluster_id: ClusterId) -> Execution[list[Tree]]:
        """Start the calculation of phylogenetic trees for a specified cluster.

        Args:
            cluster_run_id (igx_api.l2.types.cluster.ClusterRunId): The unique identifier of the cluster run.
            cluster_id (igx_api.l2.types.cluster.ClusterId): The unique identifier of the cluster.

        Returns:
            igx_api.l2.types.execution.Execution[list[igx_api.l2.types.tree.Tree]]: An awaitable that returns the calculated trees.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
                cluster_run_id = ClusterRunId("b35a7864-0887-44e5-896a-feffdcc9d022")
                cluster_id = ClusterId(123)
                trees = client.tree_api.start(cluster_run_id=cluster_run_id, cluster_id=cluster_id).wait()
            ```
        """

        tree_api_instance = openapi_client.TreeApi(self._inner_api_client)

        try:
            tree_work = openapi_client.TreeWork(cluster_run_id=cluster_run_id, cluster_id=cluster_id)
            data = tree_api_instance.start_tree(tree_work)

            assert data.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(int(data.workflow_execution_id))

            def on_complete(job_id: WorkflowExecutionTaskId, job_state: JobState) -> list[Tree]:
                trees: list[Tree] = self.get_trees_by_job_id(job_id=job_id)

                logger.success(f"Tree compute with job ID: {job_id} in workflow execution with ID: {workflow_execution_id} has successfully finished.")

                return trees

            waitable = WorkflowExecutionTaskWaitable[list[Tree]](
                workflow_execution_id=workflow_execution_id, task_template_name=WorkflowTaskTemplateName.ENPI_APP_BRANCH, on_complete=on_complete
            )
            return Execution(wait=waitable.wait_and_return_result)
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def export_tree_as_tsv(self, tree: Tree, output_directory: str | Path | None = None) -> Execution[Path]:
        """Export the sequences of the specified tree into a TSV file and download it to the specified directory.

        Args:
            tree (igx_api.l2.types.tree.Tree): The tree to export.
            output_directory (str | Path | None): The directory where to download the TSV file. Defaults to a
              unique temporary directory.

        Returns:
            igx_api.l2.types.execution.Execution[Path]: An awaitable that returns the path to the downloaded TSV file containing the sequences.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            # Assuming trees were computed and fetched already
            trees = ...

            # Export the sequences of the Amino Acid tree
            amino_acid_tree: Tree = next(tree for tree in trees if tree.type == TreeType.AMINO_ACID)

            # Export the tree as a TSV file
            logger.info("Exporting the tree as a TSV file")
            tree_tsv_path: Path = igx_client.tree_api.export_tree_as_tsv(
                tree=amino_acid_tree,
            ).wait()
            ```
        """

        tree_api_instance = openapi_client.TreeApi(self._inner_api_client)

        with ApiErrorContext():
            export_request = openapi_client.StartTreeExportRequest(tree_id=tree.tree_id)
            export_job = tree_api_instance.start_tree_export(export_request)
            assert export_job.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(export_job.workflow_execution_id)

            def on_complete(job_id: WorkflowExecutionTaskId, job_state: JobState) -> Path:
                file_api = FileApi(self._inner_api_client, self._log_level)
                file_path = file_api.download_export_by_workflow_execution_task_id(job_id=job_id, output_directory=output_directory)

                return file_path

            waitable = WorkflowExecutionTaskWaitable[Path](
                workflow_execution_id=workflow_execution_id, on_complete=on_complete, task_template_name=WorkflowTaskTemplateName.ENPI_APP_BRANCH_EXPORT
            )
            return Execution(wait=waitable.wait_and_return_result)

    def export_tree_as_df(self, tree: Tree) -> Execution[pd.DataFrame]:
        """Export the sequences of the specified tree into a pandas DataFrame.

        Args:
            tree (igx_api.l2.types.tree.Tree): The tree to export.

        Returns:
            igx_api.l2.types.execution.Execution[pd.DataFrame]: An awaitable that returns a pandas DataFrame containing the sequences.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            # Assuming trees were computed and fetched already
            trees = ...

            # Export the sequences of the Amino Acid tree
            amino_acid_tree: Tree = next(tree for tree in trees if tree.type == TreeType.AMINO_ACID)

            # Export the tree as a Pandas DataFrame
            tree_df: pd.DataFrame = igx_client.tree_api.export_tree_as_df(
                tree=amino_acid_tree,
            ).wait()
        ```
        """

        export_tsv = self.export_tree_as_tsv(tree)

        def wait() -> pd.DataFrame:
            tsv_path = export_tsv.wait()
            return pd.read_csv(tsv_path, sep="\t")

        return Execution(wait=wait)
