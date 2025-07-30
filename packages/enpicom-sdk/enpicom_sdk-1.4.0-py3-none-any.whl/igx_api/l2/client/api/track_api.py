import os
import zipfile
from pathlib import Path

import pandas as pd
from loguru import logger

from igx_api.l1 import openapi_client
from igx_api.l2.client.api.file_api import FileApi
from igx_api.l2.events.workflow_execution_task_waitable import WorkflowExecutionTaskWaitable
from igx_api.l2.types.api_error import ApiErrorContext
from igx_api.l2.types.cluster import ClusterRunId
from igx_api.l2.types.execution import Execution
from igx_api.l2.types.job import JobState
from igx_api.l2.types.log import LogLevel
from igx_api.l2.types.tag import TagId
from igx_api.l2.types.track import (
    SimplifiedTrackTemplate,
    TrackExportMode,
    TrackRun,
    TrackRunId,
    TrackTemplate,
    TrackTemplateId,
    TrackTemplateOperation,
    TrackWorkInput,
    transform_operation,
    transform_operation_input,
)
from igx_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName
from igx_api.l2.util.file import unique_temp_dir


class TrackApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_runs(
        self,
    ) -> list[TrackRun]:
        """Get all successful Track Runs.

        Returns:
            list[igx_api.l2.types.track.TrackRun]: List of Track Runs.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with IgxApiClient() as igx_client:
                track_runs = igx_client.track_api.get_runs()
            ```
        """
        track_api_instance = openapi_client.TrackApi(self._inner_api_client)

        with ApiErrorContext():
            data = track_api_instance.get_track_runs()

        return [TrackRun.from_raw(cr) for cr in data.runs]

    def get_run(self, track_run_id: TrackRunId) -> TrackRun:
        """Get a single Track Run by its ID.

        Args:
            track_run_id (igx_api.l2.types.track.TrackRunId): ID of the Track run to get.

        Returns:
            igx_api.l2.types.track.TrackRun: A successful Track Run.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with IgxApiClient() as igx_client:
                track_run = igx_client.track_api.get_run(TrackRunId(123))
            ```
        """
        track_api_instance = openapi_client.TrackApi(self._inner_api_client)

        with ApiErrorContext():
            data = track_api_instance.get_track_run(int(track_run_id))

        return TrackRun.from_raw(data.run)

    def get_run_by_job_id(self, job_id: WorkflowExecutionTaskId) -> TrackRun:
        """Get a single Track Run by its job ID.

        Args:
            job_id (igx_api.l2.types.job.JobId): ID of a job linked to a successful Track Run.

        Returns:
            igx_api.l2.types.track.TrackRun: Successful Track Run linked to the provided job ID.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Fetch a Track Run

            ```python
            with IgxApiClient() as igx_client:
                track_run = igx_client.track_api.get_run_by_job_id(JobId(1234))
            ```
        """
        track_api_instance = openapi_client.TrackApi(self._inner_api_client)

        with ApiErrorContext():
            data = track_api_instance.get_track_run_by_job_id(job_id)

        return TrackRun.from_raw(data.run)

    def get_templates(self) -> list[SimplifiedTrackTemplate]:
        """Get all available Track templates.

        Returns:
            list[igx_api.l2.types.track.SimplifiedTrackTemplate]: Available Track templates.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with IgxApiClient() as igx_client:
                templates = igx_client.track_api.get_templates()
            ```
        """
        track_api_instance = openapi_client.TrackApi(self._inner_api_client)

        with ApiErrorContext():
            data = track_api_instance.get_track_templates()

        return [
            SimplifiedTrackTemplate(
                id=TrackTemplateId(d.id),
                name=d.name,
                created_at=d.created_at,
            )
            for d in data.templates
        ]

    def get_template(self, track_template_id: TrackTemplateId) -> TrackTemplate:
        """Get a Track template by its ID.

        Args:
            track_template_id (igx_api.l2.types.track.TrackTemplateId): ID of a Track template to get.

        Returns:
            igx_api.l2.types.track.TrackTemplate: A Track template matching the provided ID.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with IgxApiClient() as igx_client:
                template = igx_client.track_api.get_template(TrackTemplateId(24))
            ```
        """
        track_api_instance = openapi_client.TrackApi(self._inner_api_client)

        with ApiErrorContext():
            data = track_api_instance.get_track_template(str(track_template_id))

        return TrackTemplate.from_raw(data.template)

    def delete_template(self, track_template_id: TrackTemplateId) -> None:
        """Delete a Track Template by its ID.

        Args:
            track_template_id (igx_api.l2.types.track.TrackTemplateId): ID of the deleted Track template.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with IgxApiClient() as igx_client:
                template = igx_client.track_api.delete_template(TrackTemplateId(24))
            ```
        """
        track_api_instance = openapi_client.TrackApi(self._inner_api_client)

        with ApiErrorContext():
            track_api_instance.delete_track_template(str(track_template_id))

    def create_template(
        self,
        name: str,
        operations: list[TrackTemplateOperation],
    ) -> TrackTemplate:
        """Create a new Track Template.

        Args:
            name (str): Track template name.
            operations (list[igx_api.l2.types.track.TrackTemplateOperation]): Configs for the template's operations.

        Returns:
            igx_api.l2.types.track.TrackTemplate: A newly created Track template.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with IgxApiClient() as igx_client:
                operations=[
                    TrackTemplateUnionOperation(
                        name="Counter",
                    ),
                    TrackTemplateIntersectionOperation(
                        name="Target",
                    ),
                    TrackTemplateDifferenceOperation(
                        name="Result",
                        input_operations=TrackTemplateDifferenceInputs(
                            remove_operation="Counter",
                            from_operation="Target",
                        ),
                        annotations=[
                            TrackTemplateFoldChangeAnnotation(name="Target FC"),
                        ],
                    ),
                ],
                template = igx_client.track_api.create_template(name="my new template", operations=operations)
            ```
        """
        track_api_instance = openapi_client.TrackApi(self._inner_api_client)

        payload = openapi_client.NewTrackTemplate(name=name, saved=True, operations=[transform_operation(op) for op in operations])

        with ApiErrorContext():
            data = track_api_instance.create_track_template(payload)

        return TrackTemplate.from_raw(data.template)

    def start(
        self,
        name: str,
        track_template: TrackTemplate,
        cluster_run_id: ClusterRunId,
        inputs: list[TrackWorkInput],
    ) -> Execution[TrackRun]:
        """Start a new Track run.

        Args:
            name (str):
                Track run name.
            track_template (igx_api.l2.types.track.TrackTemplate):
                Track template ID.
            cluster_run_id (igx_api.l2.types.cluster.ClusterRunId):
                Cluster run ID.
            inputs (list[igx_api.l2.types.track.TrackWorkInput]):
                Configs for the template's operations.

        Returns:
            igx_api.l2.types.execution.Execution[igx_api.l2.types.track.TrackRun]: An awaitable that returns the new Track Run.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Assuming that those are the collections meant for Track run:
                - Counter collection IDs: 1, 2
                - Target collection IDs: 3, 4

            ```python
            with IgxApiClient() as igx_client:
                track_run = client.track_api.start(
                    name="Test Run",
                    track_template=template,
                    cluster_run_id=cluster_run.id,
                    inputs=[
                        UnionOperationInput(
                            name="Counter",
                            input_collections=[CollectionSelector(value=CollectionId(1)),
                                CollectionSelector(value=CollectionId(2))],
                        ),
                        IntersectionOperationInput(
                            name="Target",
                            input_collections=[CollectionSelector(value=CollectionId(3)),
                                CollectionSelector(value=CollectionId(4))
                            ],
                        ),
                        FoldChangeInput(
                            name="Target FC",
                            operation_name="Result"
                            input_collections=FoldChangeInputCollections(
                                from_collection=CollectionSelector(value=CollectionId(3)),
                                to_collection=CollectionSelector(value=CollectionId(4)),
                            ),
                        ),
                    ],
                ).wait()
            ```
        """
        track_api_instance = openapi_client.TrackApi(self._inner_api_client)

        payload = openapi_client.TrackWork(
            name=name,
            template=openapi_client.TrackTemplateIdVersion(id=str(track_template.id), version=int(track_template.version)),
            cluster_run_id=cluster_run_id,
            inputs=[transform_operation_input(x) for x in inputs],
        )

        with ApiErrorContext():
            data = track_api_instance.start_track_run(payload)
            assert data.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(int(data.workflow_execution_id))

            def on_complete(job_id: WorkflowExecutionTaskId, job_state: JobState) -> TrackRun:
                track_run = self.get_run_by_job_id(job_id)

                logger.success(f"Track run with job ID: {data.workflow_execution_id} has successfully finished.")

                return track_run

            waitable = WorkflowExecutionTaskWaitable[TrackRun](
                workflow_execution_id=workflow_execution_id, task_template_name=WorkflowTaskTemplateName.ENPI_APP_TRACK, on_complete=on_complete
            )
            return Execution(wait=waitable.wait_and_return_result)

    def export_as_tsv(
        self,
        track_run_id: TrackRunId,
        operation: str,
        mode: TrackExportMode,
        tag_ids: list[TagId],
        limit: int | None = None,
        output_directory: str | Path | None = None,
    ) -> Execution[Path]:
        """Run an export of a Track operation result and download the TSV file.

        Args:
            track_run_id (igx_api.l2.types.track.TrackRunId): Track run ID.
            operation (str): Name of the operation to export.
            mode (igx_api.l2.types.track.TrackExportMode): Mode in which export will be run.
            tag_ids (list[igx_api.l2.types.tag.TagId]): List of tags to be included in the export.
            limit (int | None):
                If specified, the export will contain only the first N clusters, N being the value passed as this param.
            output_directory (str | Path | None): The directory where to download the TSV file. Defaults to a
              unique temporary directory.

        Returns:
            igx_api.l2.types.execution.Execution[Path]: An awaitable that returns the path to the downloaded TSV file containing the sequences.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with IgxApiClient() as igx_client:
                tsv_path = igx_client.track_api.export_as_tsv(
                    track_run_id=TrackRunId(42),
                    operation="Result",
                    mode=TrackExportMode.REPRESENTATIVES,
                    tag_ids=[SequenceTags.Cdr3AminoAcids, SequenceTags.Chain],
                    limit=50,
                    output_directory="/results",
                ).wait()
            ```
        """

        # Ensure that the directory exists
        if output_directory is None:
            output_directory = unique_temp_dir()

        track_api_instance = openapi_client.TrackApi(self._inner_api_client)

        payload = openapi_client.TrackExportPayload(
            operation_name=operation,
            track_run_id=track_run_id,
            mode=mode,
            tag_ids=[int(id) for id in tag_ids],
            limit=limit,
        )

        with ApiErrorContext():
            response = track_api_instance.export_track_results(payload)
            assert response.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(response.workflow_execution_id)

            def on_complete(job_id: WorkflowExecutionTaskId, job_state: JobState) -> Path:
                file_api = FileApi(self._inner_api_client, self._log_level)
                zip_path = file_api.download_export_by_workflow_execution_task_id(job_id=job_id, output_directory=output_directory)

                with zipfile.ZipFile(zip_path, "r") as archive:
                    names = archive.namelist()
                    archive.extractall(output_directory)
                paths = [Path(os.path.join(output_directory, name)) for name in names]

                if len(paths) > 1:
                    logger.warning(f'More than 1 file encountered in the zipped export: {",".join([str(path) for path in paths])}, only returning first file')
                logger.success(f"Track results export with job ID: {job_id} has successfully finished.")

                return paths[0]

            waitable = WorkflowExecutionTaskWaitable[Path](
                workflow_execution_id=workflow_execution_id, on_complete=on_complete, task_template_name=WorkflowTaskTemplateName.ENPI_APP_TRACK_EXPORT
            )
            return Execution(wait=waitable.wait_and_return_result)

    def export_as_df(
        self,
        track_run_id: TrackRunId,
        operation: str,
        mode: TrackExportMode,
        tag_ids: list[TagId],
        limit: int | None = None,
    ) -> Execution[pd.DataFrame]:
        """Runs an Export of a Track Operation results and loads it as a pandas DataFrame.

        Args:
            track_run_id (igx_api.l2.types.track.TrackRunId): Track run ID.
            operation (str): Name of the operation to export.
            mode (igx_api.l2.types.track.TrackExportMode): Mode in which export will be run.
            tag_ids (list[igx_api.l2.types.tag.TagId]): List of tags to be included in the export.
            limit (int | None):
                If specified, the export will contain only the first N clusters, N being the value passed as this param.

        Returns:
            igx_api.l2.types.execution.Execution[Path]: An awaitable that returns the path to the downloaded TSV file containing the sequences.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with IgxApiClient() as igx_client:
                tsv_path = igx_client.track_api.export_as_df(
                    track_run_id=TrackRunId(42),
                    operation="Result",
                    mode=TrackExportMode.REPRESENTATIVES,
                    tag_ids=[SequenceTags.Cdr3AminoAcids, SequenceTags.Chain],
                    limit=50
                ).wait()
            ```
        """

        export_tsv = self.export_as_tsv(track_run_id, operation, mode, tag_ids, limit)

        def wait() -> pd.DataFrame:
            file_path = export_tsv.wait()
            return pd.read_csv(file_path, delimiter="\t")

        return Execution(wait=wait)
