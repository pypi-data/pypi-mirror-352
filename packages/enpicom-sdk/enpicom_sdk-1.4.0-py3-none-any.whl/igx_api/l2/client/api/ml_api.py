import os
import time
import uuid
from typing import assert_never

import pandas as pd
from loguru import logger

from igx_api.l1 import openapi_client
from igx_api.l2.client.api.file_api import FileApi
from igx_api.l2.events.workflow_execution_task_waitable import WorkflowExecutionTaskWaitable
from igx_api.l2.types.api_error import ApiError, ApiErrorContext
from igx_api.l2.types.clone import CloneId
from igx_api.l2.types.collection import CollectionId
from igx_api.l2.types.execution import Execution
from igx_api.l2.types.file import OnCollisionAction
from igx_api.l2.types.job import JobState
from igx_api.l2.types.log import LogLevel
from igx_api.l2.types.ml import (
    MlAwsEndpointConfig,
    MlEndpoint,
    MlEndpointId,
    MlEndpointSignature,
    MlflowModelUri,
    MlInputMapItem,
    MlInvocation,
    MlInvocationId,
    MlInvocationStats,
    MlInvocationStatus,
    MlOutputIntent,
)
from igx_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName


class InvocationFailed(Exception):
    """Indicates that the ML invocation has failed."""

    def __init__(self, invocation_id: MlInvocationId):
        """@private"""
        super().__init__(f"ML invocation with ID `{invocation_id}` failed")


class DeploymentFailed(Exception):
    """Indicates that the ML deployment has failed."""

    def __init__(self, workflow_execution_task_id: WorkflowExecutionTaskId):
        """@private"""
        super().__init__(f"ML deployment job with ID `{workflow_execution_task_id}` failed")


class MlApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_ml_endpoints(self) -> list[MlEndpoint]:
        """Get all ML endpoints.

        Returns:
            list[igx_api.l2.types.ml.MlEndpoint]: A list of ML endpoints.
        """

        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        try:
            return [MlEndpoint.from_raw(i) for i in ml_api_instance.get_ml_endpoints().ml_endpoints]
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def get_ml_invocation_stats(self) -> list[MlInvocationStats]:
        """Get ML invocation statistics.

        Returns:
            list[igx_api.l2.types.ml.MlInvocationStats]: A list of ML invocation statistics.
        """
        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        try:
            stats = ml_api_instance.get_ml_invocation_stats().stats
            return [MlInvocationStats.from_raw(i) for i in stats]
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def register_ml_endpoint(
        self,
        display_name: str,
        input_mapping: list[MlInputMapItem],
        output_intents: list[MlOutputIntent],
        vendor_config: MlAwsEndpointConfig,
        signatures: list[MlEndpointSignature],
    ) -> MlEndpointId:
        """Register a ML endpoint.

        Args:
            display_name (str): The display name of the ML endpoint.
            input_mapping (list[MlInputMapItem]): The input mapping of the ML endpoint.
            output_intents (list[MlOutputIntent]): The output intents of the ML endpoint.
            vendor_config (MlAwsEndpointConfig): The AWS endpoint configuration of the ML endpoint.
            signatures (list[MlEndpointSignature]): The signatures of the ML endpoint.

        Returns:
            endpoint_id (str): The unique identifier of a ML endpoint.
        """

        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        try:
            result = ml_api_instance.register_ml_endpoint(
                register_ml_endpoint_request=openapi_client.RegisterMlEndpointRequest(
                    display_name=display_name,
                    input_mapping=[openapi_client.MlInputMapItem.model_validate(i) for i in input_mapping],
                    output_intents=[openapi_client.MlOutputIntent.from_dict(dict(i)) for i in output_intents],
                    vendor_config=openapi_client.MlAwsEndpointConfig.from_dict(
                        {**vendor_config, "region": vendor_config.get("region", "eu-west-1"), "endpoint_type": "external"}
                    ),
                    signatures=[openapi_client.MlEndpointSignature.model_validate(i) for i in signatures],
                )
            )
            return MlEndpointId(result.endpoint_id)
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def unregister_ml_endpoint(self, endpoint_id: MlEndpointId) -> None:
        """Unregister a ML endpoint.

        Args:
            endpoint_id (MlEndpointId): The unique identifier of a ML endpoint.
        """

        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        try:
            ml_api_instance.unregister_ml_endpoint(id=endpoint_id)
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def deploy_model(
        self,
        display_name: str,
        input_mapping: list[MlInputMapItem],
        output_intents: list[MlOutputIntent],
        model_uri: MlflowModelUri,
        signatures: list[MlEndpointSignature],
    ) -> Execution[MlEndpointId]:
        """Deploy a model from ML flow as a SageMaker model with an endpoint.

        Args:
            display_name (str): The display name of the ML endpoint.
            input_mapping (list[MlInputMapItem]): The input mapping of the ML endpoint.
            output_intents (list[MlOutputIntent]): The output intents of the ML endpoint.
            model_uri (MlFlowModelUri): The URI of a MLflow model.
        """
        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        payload = openapi_client.DeployModelRequest(
            display_name=display_name,
            input_mapping=[openapi_client.MlInputMapItem.model_validate(i) for i in input_mapping],
            output_intents=[openapi_client.MlOutputIntent.from_dict(dict(i)) for i in output_intents],
            model_uri=model_uri,
            signatures=[openapi_client.MlEndpointSignature.model_validate(i) for i in signatures],
        )

        with ApiErrorContext():
            deploy_model_response = ml_api_instance.deploy_model(deploy_model_request=payload)
            assert deploy_model_response.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(int(deploy_model_response.workflow_execution_id))

            def on_complete(job_id: WorkflowExecutionTaskId, job_state: JobState) -> MlEndpointId:
                # If the job has succeeded, return the endpoint_id
                match job_state:
                    case JobState.SUCCEEDED:
                        result = ml_api_instance.get_endpoint_by_workflow_execution_task_id(workflow_execution_task_id=job_id)
                        return MlEndpointId(result.endpoint_id)
                    case _:
                        raise DeploymentFailed(job_id)

            waitable = WorkflowExecutionTaskWaitable[MlEndpointId](
                workflow_execution_id=workflow_execution_id, task_template_name=WorkflowTaskTemplateName.ENPI_APP_ML_DEPLOY_ENDPOINT, on_complete=on_complete
            )

            return Execution(wait=waitable.wait_and_return_result)

    def undeploy_model(self, endpoint_id: MlEndpointId) -> None:
        """Remove a SageMaker model and endpoint.

        Args:
            endpoint_id (MlEndpointId): The unique identifier of a ML endpoint.
        """
        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        try:
            ml_api_instance.undeploy_model(id=endpoint_id)
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def invoke_endpoint(
        self, endpoint_id: MlEndpointId, clone_ids: list[CloneId] | None = None, collection_ids: list[CollectionId] | None = None
    ) -> Execution[MlInvocation]:
        """Invoke a ML endpoint.

        Args:
            endpoint_id (MlEndpointId): The unique identifier of a ML endpoint.
            clone_ids (list[CloneId]): The unique identifiers of the clones.

        Returns:
            output_key (MlInvocationOutputKey): The output key of a ML invocation.
            invocation_id (MlInvocationId): The unique identifier of a ML invocation.
        """
        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        try:
            if clone_ids is not None and collection_ids is not None:
                raise ValueError("Either clone_ids or collection_ids must be provided, but not both")

            result = ml_api_instance.invoke_endpoint(
                id=endpoint_id,
                invoke_ml_endpoint_request=openapi_client.InvokeMlEndpointRequest.from_dict(dict(clone_ids=clone_ids, collection_ids=collection_ids)),
            )
            invocation_id = MlInvocationId(result.invocation_id)

            def wait() -> MlInvocation:
                return self.wait_for_invocation_to_be_completed(invocation_id)

            return Execution(wait=wait)
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def invoke_endpoint_raw(self, endpoint_id: MlEndpointId, input_file: str | pd.DataFrame) -> Execution[MlInvocation]:
        """Invoke a ML endpoint without intent.

        Args:
            endpoint_id (MlEndpointId): The unique identifier of a ML endpoint.
            input_file (str | pd.DataFrame): Model input either a path to a CSV file or a pandas DataFrame.

        Returns:
            output_key (MlInvocationOutputKey): The output key of a ML invocation.
            invocation_id (MlInvocationId): The unique identifier of a ML invocation.
        """
        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        file_api_instance = FileApi(self._inner_api_client, self._log_level)
        try:
            if isinstance(input_file, pd.DataFrame):
                file_path = os.path.join(os.getcwd(), f"input_{uuid.uuid4()}.csv")
                input_file.to_csv(path_or_buf=file_path, index=False)
                file_obj = file_api_instance.upload_file(file_path=file_path, on_collision=OnCollisionAction.ERROR).wait()
                os.remove(file_path)  # Remove temp created file
            elif isinstance(input_file, str):
                file_name = input_file.split(os.sep)[-1]
                ext = file_name.split(".")[-1]
                if ext.lower() != "csv":
                    raise ValueError("Input file must be a CSV file")
                file_obj = file_api_instance.upload_file(file_path=input_file, on_collision=OnCollisionAction.ERROR).wait()
            else:
                raise ValueError("Input file must be a CSV file or pandas DataFrame")

            result = ml_api_instance.invoke_endpoint_raw(
                id=endpoint_id, invoke_ml_endpoint_raw_request=openapi_client.InvokeMlEndpointRawRequest(file_id=file_obj.id)
            )
            invocation_id = MlInvocationId(result.invocation_id)

            def wait() -> MlInvocation:
                return self.wait_for_invocation_to_be_completed(invocation_id)

            return Execution(wait=wait)
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def get_invocation(self, invocation_id: MlInvocationId) -> MlInvocation:
        """Get a ML invocation.

        Args:
            invocation_id (MlInvocationId): The unique identifier of a ML invocation.

        Returns:
            MlInvocation: The ML invocation.
        """
        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        try:
            invocation = ml_api_instance.get_invocation(id=invocation_id).invocation
            return MlInvocation(
                id=MlInvocationId(invocation.id),
                ml_endpoint_id=MlEndpointId(invocation.ml_endpoint_id),
                started_at=str(invocation.started_at),
                completed_at=str(invocation.completed_at) if invocation.completed_at is not None else None,
                status=MlInvocationStatus(invocation.status),
            )
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def wait_for_invocation_to_be_completed(self, invocation_id: MlInvocationId) -> MlInvocation:
        """
        Wait for a ML invocation and processing to be completed. If the invocation fails an exception will be raised.

        Args:
            invocation_id (MlInvocationId): The unique identifier of a ML invocation.

        Returns:
            igx_api.l2.types.job.Job: The job that was waited for. If this returns, it means the job has succeeded.

        Raises:
            igx_api.l2.client.api.ml_api.InvocationFailed: If the invocation and processing failed.
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with IgxApiClient() as igx_client:
                igx_client.ml_api.wait_for_invocation_to_be_completed(invocation_id=MlInvocationId("abc"))
            ```
        """

        logger.info(f"Waiting for ML invocation with ID `{invocation_id}` to be completed")

        poll_interval_seconds = 10

        # We do not limit this loop at the top level, we do not know how long it takes for a job to be picked up.
        while True:
            with ApiErrorContext():
                invocation = self.get_invocation(invocation_id)

            match invocation.status:
                case MlInvocationStatus.Pending:
                    logger.debug(
                        f"ML invocation with ID `{invocation_id}` still has status `{invocation.status.value}`. Waiting for {poll_interval_seconds} seconds"
                    )
                    time.sleep(poll_interval_seconds)
                case MlInvocationStatus.HandlingIntent:
                    logger.debug(f"Job with ID `{invocation_id}` still has status `{invocation.status.value}`. Waiting for {poll_interval_seconds} seconds")
                    time.sleep(poll_interval_seconds)
                case MlInvocationStatus.Succeeded:
                    logger.success(f"Job with ID `{invocation_id}` succeeded")
                    return invocation
                case MlInvocationStatus.Failed:
                    raise InvocationFailed(invocation_id)
                case _:
                    assert_never(invocation.status)
