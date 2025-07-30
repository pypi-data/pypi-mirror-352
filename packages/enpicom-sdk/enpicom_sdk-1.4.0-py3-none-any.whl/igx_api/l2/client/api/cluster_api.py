from pathlib import Path

import pandas as pd
from loguru import logger

from igx_api.l1 import openapi_client
from igx_api.l2.client.api.file_api import FileApi
from igx_api.l2.events.workflow_execution_task_waitable import WorkflowExecutionTaskWaitable
from igx_api.l2.types.api_error import ApiErrorContext
from igx_api.l2.types.cluster import AdditionalOptions, ClusterRun, ClusterRunId, ExportClustersMode, SequenceFeatureIdentities
from igx_api.l2.types.collection import CollectionId
from igx_api.l2.types.execution import Execution
from igx_api.l2.types.job import JobState
from igx_api.l2.types.log import LogLevel
from igx_api.l2.types.tag import TagId
from igx_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName


class ClusterApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_cluster_runs(self, collection_ids: list[CollectionId] | None = None) -> list[ClusterRun]:
        """Get all successful Cluster Runs or a selection of them linked to the passed Collection IDs.

        Args:
            collection_ids (list[igx_api.l2.types.collection.CollectionId] | None): IDs of clone collections.
                If passed, they will be used to filter Cluster Runs down to the ones originitating from
                the collections matched with passed IDs.

        Returns:
            list[igx_api.l2.types.cluster.ClusterRun]: List of Cluster Runs.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Get all Cluster Runs that were run using CollectionId=123
            ```python
            with IgxApiClient() as igx_client:
                cluster_runs = igx_client.cluster_api.get_cluster_runs(collection_ids=[CollectionId(123)])
            ```
        """
        cluster_api_instance = openapi_client.ClusterApi(self._inner_api_client)

        payload = openapi_client.GetClusterRunsRequestPayload(
            collection_ids=[int(id) for id in collection_ids] if collection_ids is not None else None,
        )

        with ApiErrorContext():
            data = cluster_api_instance.get_cluster_runs(payload)

        return [ClusterRun.from_raw(cr) for cr in data.clusters]

    def get_cluster_run(self, cluster_run_id: ClusterRunId) -> ClusterRun:
        """Get a successful Cluster Run by ID.

        Args:
            cluster_run_id (igx_api.l2.types.cluster.ClusterRunId): ID of a Cluster Run to get.

        Returns:
            igx_api.l2.types.cluster.ClusterRun: Cluster Run matching the provided ID.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Get a Cluster Run with ClusterRunId="b236c01c-e0e2-464e-8bd7-b1718476a78b"
            ```python
            with IgxApiClient() as igx_client:
                cluster_run = igx_client.cluster_api.get_cluster_run(ClusterRunId("b236c01c-e0e2-464e-8bd7-b1718476a78b"))
            ```
        """
        cluster_api_instance = openapi_client.ClusterApi(self._inner_api_client)

        with ApiErrorContext():
            data = cluster_api_instance.get_cluster_run(cluster_run_id)

        return ClusterRun.from_raw(data.cluster_run)

    def get_cluster_run_by_workflow_execution_task_id(self, workflow_execution_task_id: WorkflowExecutionTaskId) -> ClusterRun:
        """Get a successful Cluster Run by its workflow execution task ID.

        Args:
            workflow_execution_task_id (igx_api.l2.types.workflow.WorkflowExecutionTaskId): ID of a workflow execution task linked to a successful Cluster Run.

        Returns:
            igx_api.l2.types.cluster.ClusterRun: Successful Cluster Run linked to the provided workflow execution ID.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Get a Cluster Run by Workflow execution task ID:

            ```python
            with IgxApiClient() as igx_client:
                cluster_run = igx_client.cluster_api.get_cluster_run_by_workflow_execution_task_id(WorkflowExecutionTaskId(1234))
            ```
        """
        cluster_api_instance = openapi_client.ClusterApi(self._inner_api_client)

        with ApiErrorContext():
            data = cluster_api_instance.get_cluster_run_by_workflow_execution_task_id(workflow_execution_task_id)

        return ClusterRun.from_raw(data.cluster_run)

    def start(
        self,
        name: str,
        collection_ids: list[CollectionId],
        sequence_features: list[TagId],
        match_tags: list[TagId],
        identities: SequenceFeatureIdentities,
        additional_options: AdditionalOptions | None = None,
    ) -> Execution[ClusterRun]:
        """Start a new Cluster Run.

        Args:
            name (str): Cluster Run name.
            collection_ids (list[igx_api.l2.types.collection.CollectionId]): Collections to use in the clustering. All collections must have the
              same receptor.
            sequence_features (list[igx_api.l2.types.tag.TagId]): Sequence Features to be clustered on.
            identities (igx_api.l2.types.cluster.SequenceFeatureIdentities): Chain identities used for clustering.
            optional_restrictions (igx_api.l2.types.cluster.OptionalRestrictions | None): Optional restrictions applied to sequences before clustering.
            additional_options (igx_api.l2.types.cluster.AdditionalOptions | None): Additional Options for clustering configuration.

        Returns:
            igx_api.l2.types.execution.Execution[igx_api.l2.types.cluster.ClusterRun]: An awaitable that returns the completed Cluster Run
              when awaited.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Start a new Cluster Run for 3 collections, using 80% identity on IG CDR3 Amino Acids, with same CDR3 Length restriction
            ```python
            with IgxApiClient() as igx_client:
                cluster_run = igx_client.cluster_api.start_cluster_run(
                    name=f"Clustering for collections 1,2 and 3",
                    collection_ids=[CollectionId(x) for x in [1,2,3]],
                    sequence_features=[SequenceTags.Cdr3AminoAcids],
                    identities=SequenceFeatureIdentities(Heavy=80, Kappa=80, Lambda=80),
                    optional_restrictions=OptionalRestrictions(should_match_cdr3_length=True),
                    additional_options=None,
                ).wait()
            ```
        """
        cluster_api_instance = openapi_client.ClusterApi(self._inner_api_client)
        payload = openapi_client.ClusterWork(
            name=name,
            collection_ids=[int(c_id) for c_id in collection_ids],
            sequence_features=[int(tag_id) for tag_id in sequence_features],
            match_tags=[int(tag_id) for tag_id in match_tags],
            identities=identities.to_inner(),
            additional_options=additional_options.to_inner() if additional_options is not None else None,
        )

        with ApiErrorContext():
            start_cluster_run_response = cluster_api_instance.start_cluster_run(payload)
            assert start_cluster_run_response.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(start_cluster_run_response.workflow_execution_id)

            def on_complete(job_id: WorkflowExecutionTaskId, job_state: JobState) -> ClusterRun:
                assert job_state == JobState.SUCCEEDED, f"Job {job_id} did not reach {JobState.SUCCEEDED} state, got {job_state} state instead"

                cluster_run = self.get_cluster_run_by_workflow_execution_task_id(job_id)
                logger.success(f"Cluster run with job ID: {job_id} in workflow execution with ID: {workflow_execution_id} has successfully finished.")
                return cluster_run

            waitable = WorkflowExecutionTaskWaitable[ClusterRun](
                workflow_execution_id=workflow_execution_id, task_template_name=WorkflowTaskTemplateName.ENPI_APP_CLUSTER, on_complete=on_complete
            )
            return Execution(wait=waitable.wait_and_return_result)

    def export_clusters_as_csv(
        self,
        cluster_run_id: ClusterRunId,
        mode: ExportClustersMode,
        limit: int | None = None,
        output_directory: str | Path | None = None,
    ) -> Execution[Path]:
        """Start a Cluster export and download the results CSV file.

        Args:
            cluster_run_id (igx_api.l2.types.cluster.ClusterRunId):
                ID of the Cluster Run to export.
            mode (igx_api.l2.types.cluster.ExportClustersMode):
                Mode in which export is run.
            limit (int | None):
                If specified, the export will contain only the first N clusters, N being the value passed as this param.
            output_directory (str | Path | None):
                Directory into which the downloaded archive will be extracted. If left empty, a temporary directory will be created.

        Returns:
            igx_api.l2.types.execution.Execution[Path]: An awaitable that returns the path to the downloaded CSV file
              when awaited.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Download successful Cluster Export result as CSV.
            ```python
            with IgxApiClient() as igx_client:
                file_path = client.cluster_api.export_clusters_as_csv(
                    cluster_run_id=ClusterRunId("b236c01c-e0e2-464e-8bd7-b1718476a78b"),
                    mode=ExportClusterMode.CLONES,
                    limit=None,
                    output_directory="/home/exported_data/",
                )
                print(file_path)
            ```
        """
        cluster_api_instance = openapi_client.ClusterApi(self._inner_api_client)

        payload = openapi_client.GetClusteredClonesRequestPayload(
            cluster_run_id=cluster_run_id,
            mode=mode,
            limit=limit,
        )

        with ApiErrorContext():
            data = cluster_api_instance.export_clusters(payload)

            assert data.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(data.workflow_execution_id)

            def on_complete(job_id: WorkflowExecutionTaskId, job_state: JobState) -> Path:
                file_api = FileApi(self._inner_api_client, self._log_level)
                file_path = file_api.download_export_by_workflow_execution_task_id(job_id=job_id, output_directory=output_directory)

                logger.success(f"Exported clusters to {file_path}")

                return file_path

            waitable = WorkflowExecutionTaskWaitable[Path](
                workflow_execution_id=workflow_execution_id,
                on_complete=on_complete,
                task_template_name=WorkflowTaskTemplateName.ENPI_APP_CLUSTER_EXPORT,
            )

            return Execution(wait=waitable.wait_and_return_result)

    def export_clusters_as_df(
        self,
        cluster_run_id: ClusterRunId,
        mode: ExportClustersMode,
        limit: int | None = None,
    ) -> Execution[pd.DataFrame]:
        """Start a Cluster Export, download the results, and return them as Pandas DataFrame.

        Args:
            cluster_run_id (igx_api.l2.types.cluster.ClusterRunId):
                ID of the Cluster Run to export.
            mode (igx_api.l2.types.cluster.ExportClustersMode):
                Mode in which export is run.
            limit (int | None):
                If specified, the export will contain only the first N clusters, N being the value passed as this param.

        Returns:
            igx_api.l2.types.execution.Execution[pd.DataFrame]: An awaitable that returns the export results as Pandas
              DataFrame when awaited.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Download successful Cluster Export result as CSV.
            ```python
            with IgxApiClient() as igx_client:
                df = igx_client.cluster_api.export_clusters_as_df(
                    cluster_run_id=ClusterRunId("b236c01c-e0e2-464e-8bd7-b1718476a78b"),
                    mode=ExportClusterMode.CLONES,
                ).wait()
                print(df)
            ```
        """

        def wait() -> pd.DataFrame:
            file_path = self.export_clusters_as_csv(cluster_run_id, mode, limit).wait()
            return pd.read_csv(file_path, delimiter="\t")

        return Execution(wait=wait)
