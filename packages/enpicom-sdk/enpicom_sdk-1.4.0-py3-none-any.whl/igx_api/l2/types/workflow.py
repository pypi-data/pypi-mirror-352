from enum import StrEnum
from typing import NewType

from igx_api.l1 import openapi_client
from igx_api.l2.types.job import JobState
from igx_api.l2.util.from_raw_model import FromRawModel

WorkflowExecutionId = NewType("WorkflowExecutionId", int)
"""The unique identifier of a workflow execution."""

WorkflowExecutionTaskId = NewType("WorkflowExecutionTaskId", int)
"""The unique identifier of a workflow execution task."""


class WorkflowExecutionTask(FromRawModel[openapi_client.WorkflowExecutionTaskStatesInner]):
    job_id: WorkflowExecutionTaskId
    """The unique identifier of the workflow execution task."""
    task_template_name: str
    """The unique identifier of the workflow execution."""
    state: JobState
    """The state of the workflow execution."""

    @classmethod
    def _build(cls, raw: openapi_client.WorkflowExecutionTaskStatesInner) -> "WorkflowExecutionTask":
        assert raw.task_template_name is not None
        assert raw.id is not None

        return cls(
            job_id=WorkflowExecutionTaskId(raw.id),
            task_template_name=raw.task_template_name,
            state=JobState(raw.state.lower()),
        )


class WorkflowTaskTemplateName(StrEnum):
    ENPI_APP_BASKET_ADD_CLONES = "enpi-app-basket-add-clones"
    ENPI_APP_BASKET_EXPORT = "enpi-app-basket-export-table"
    ENPI_APP_BASKET_EXPORT_FASTA = "enpi-app-basket-export-fasta"
    ENPI_APP_BASKET_MSA = "enpi-app-basket-msa"
    ENPI_APP_BASKET_REMOVE_CLONES = "enpi-app-basket-remove-clones"
    ENPI_APP_BRANCH = "enpi-app-phylogeny"
    ENPI_APP_BRANCH_EXPORT = "enpi-app-phylogeny-export"
    ENPI_APP_CHROMATOGRAM_CREATE = "enpi-app-chromatogram"
    ENPI_APP_CHROMATOGRAM_SAVE = "enpi-app-chromatogram-save"
    ENPI_APP_CLUSTER = "enpi-app-cluster"
    ENPI_APP_CLUSTER_EXPORT = "enpi-app-cluster-export"
    ENPI_APP_CLUSTER_RELATEDNESS = "enpi-app-cluster-similarity"
    ENPI_APP_COLLECTION_EXPORT = "enpi-app-collection-export"
    ENPI_APP_COLLECTION_IMPORT = "enpi-app-collection-import"
    ENPI_APP_EXPLORE = "enpi-app-repertoire-overview"
    ENPI_APP_INSPECT = "enpi-app-quality-control"
    ENPI_APP_LIABILITIES = "enpi-app-liabilities"
    ENPI_APP_METADATA_IMPORT = "enpi-app-metadata-import"
    ENPI_APP_METADATA_IMPORT_TEMPLATED = "enpi-app-metadata-import-templated"
    ENPI_APP_ML_DEPLOY_ENDPOINT = "enpi-app-ml-deploy-endpoint"
    ENPI_APP_PROFILE = "enpi-app-sequence-annotation"
    ENPI_APP_PROFILE_EXPORT_READ_FATES = "enpi-app-collection-export-read-fates"
    ENPI_APP_REFERENCE_CREATE = "enpi-app-reference-create"
    ENPI_APP_SEQUENCE_VIEWER_EXPORT_PDB = "enpi-app-sequence-viewer-export-pdb"
    ENPI_APP_TAG_CREATE = "enpi-app-tag-create"
    ENPI_APP_TRACK = "enpi-app-enrichment"
    ENPI_APP_TRACK_EXPORT = "enpi-app-enrichment-export"


"""Map of all workflow job templates"""
