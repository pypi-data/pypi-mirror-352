import os
import tempfile
from pathlib import Path
from typing import Generator, Mapping
from uuid import uuid4
from zipfile import ZipFile

import pandas as pd
from loguru import logger

from igx_api.l1 import openapi_client
from igx_api.l2.client.api.file_api import FileApi
from igx_api.l2.client.api.filter_api import FilterApi
from igx_api.l2.events.workflow_execution_task_waitable import WorkflowExecutionTaskWaitable
from igx_api.l2.events.workflow_execution_task_waitable_with_pre_steps import WorkflowExecutionTaskWaitableWithPreSteps
from igx_api.l2.tags import CloneTags, CollectionTags, SequenceTags
from igx_api.l2.types import import_metadata, import_metadata_templated
from igx_api.l2.types.api_error import ApiError, ApiErrorContext
from igx_api.l2.types.collection import AdditionalImportMetadata, CollectionId, CollectionMetadata
from igx_api.l2.types.execution import Execution
from igx_api.l2.types.file import File
from igx_api.l2.types.filter import Filter, MatchIds, MatchIdTarget, TemplatedFilter
from igx_api.l2.types.job import JobState
from igx_api.l2.types.log import LogLevel
from igx_api.l2.types.reference_database import ReferenceDatabaseRevision
from igx_api.l2.types.tag import TagId, TagKey
from igx_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName
from igx_api.l2.util.file import verify_headers_uniformity

DEFAULT_EXPORT_TAG_IDS = [
    # Collection tags
    CollectionTags.Name,
    CollectionTags.Organism,
    CollectionTags.Complexity,
    CollectionTags.Receptor,
    CollectionTags.NumberOfClones,
    CollectionTags.Reference,
    # Clone tags
    CloneTags.TenXBarcode,
    CloneTags.CloneCount,
    # Sequence tags
    SequenceTags.Chain,
    SequenceTags.SequenceCount,
    SequenceTags.Cdr3AminoAcids,
    SequenceTags.VGene,
    SequenceTags.JGene,
]
"""The default tags that are included when exporting a collection to a DataFrame or a CSV file.

These are:

- Collection level tags:
    - `igx_api.l2.tags.CollectionTags.Name`
    - `igx_api.l2.tags.CollectionTags.Organism`
    - `igx_api.l2.tags.CollectionTags.Complexity`
    - `igx_api.l2.tags.CollectionTags.Receptor`
    - `igx_api.l2.tags.CollectionTags.NumberOfClones`
    - `igx_api.l2.tags.CollectionTags.Reference`
- Clone level tags:
    - `igx_api.l2.tags.CloneTags.TenXBarcode`
    - `igx_api.l2.tags.CloneTags.CloneCount`
- Sequence level tags:
    - `igx_api.l2.tags.SequenceTags.Chain`
    - `igx_api.l2.tags.SequenceTags.SequenceCount`
    - `igx_api.l2.tags.SequenceTags.Cdr3AminoAcids`
    - `igx_api.l2.tags.SequenceTags.VGene`
    - `igx_api.l2.tags.SequenceTags.JGene`
"""


class CollectionApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_collections_metadata(self) -> Generator[CollectionMetadata, None, None]:
        """Get a generator through all available collections in the platform.

        Returns:
            Generator[igx_api.l2.types.collection.CollectionMetadata, None, None]: A generator through all collections in the platform.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with IgxApiClient() as igx_client:
                for collection in igx_client.collection_api.get_collections_metadata():
                    print(collection)
            ```
        """

        logger.info("Getting a generator through all collections")

        collection_api_instance = openapi_client.CollectionApi(self._inner_api_client)

        # Fetch the first page, there is always a first page, it may be empty
        try:
            get_collections_response = collection_api_instance.get_collections()
        except openapi_client.ApiException as e:
            raise ApiError(e)

        # `collections` and `cursor` get overwritten in the loop below when fetching a new page
        collections = get_collections_response.collections
        cursor = get_collections_response.cursor

        while True:
            for collection in collections:
                yield CollectionMetadata.from_raw(collection)

            # Check if we need to fetch a next page
            if cursor is None:
                logger.trace("No more pages of collections")
                return  # No more pages

            # We have a cursor, so we need to get a next page
            logger.trace("Fetching next page of collections")
            try:
                get_collections_response = collection_api_instance.get_collections(cursor=cursor)
            except openapi_client.ApiException as e:
                raise ApiError(e)
            collections = get_collections_response.collections
            cursor = get_collections_response.cursor

    def get_collection_metadata_by_id(self, collection_id: CollectionId) -> CollectionMetadata:
        """Get a single collection by its ID.

        Args:
            collection_id (igx_api.l2.types.collection.CollectionId): The ID of the collection to get.

        Returns:
            igx_api.l2.types.collection.CollectionMetadata: The collection, with all its metadata. This object does not contain
              the collection's clones or sequences, only the metadata. For collection's clone and sequence data refer
              to igx_api.l2.client.api.collection_api.CollectionApi.get_as_zip and igx_api.l2.client.api.collection_api.CollectionApi.get_as_df.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with IgxApiClient() as igx_client:
                collection: Collection = igx_client.collection_api.get_collection_metadata_by_id(collection_id=CollectionId(1234))
            ```
        """

        logger.info(f"Getting collection with ID `{collection_id}`")

        collection_api_instance = openapi_client.CollectionApi(self._inner_api_client)

        try:
            get_collection_response = collection_api_instance.get_collection(collection_id)
        except openapi_client.ApiException as e:
            raise ApiError(e)

        collection = CollectionMetadata.from_raw(get_collection_response.collection)

        return collection

    def delete_collection_by_id(self, collection_id: CollectionId) -> None:
        """Delete a single collection by its ID.

        This will remove the collection from the IGX Platform.

        Args:
            collection_id (igx_api.l2.types.collection.CollectionId): The ID of the collection to delete.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with IgxApiClient() as igx_client:
                igx_client.collection_api.delete_collection_by_id(collection_id=CollectionId(1234))
            ```
        """

        logger.info(f"Deleting collection with ID `{collection_id}`")

        collection_api_instance = openapi_client.CollectionApi(self._inner_api_client)

        try:
            collection_api_instance.delete_collection(id=collection_id)
        except openapi_client.ApiException as e:
            raise ApiError(e)

        logger.info(f"Collection with ID `{collection_id}` successfully deleted")

    def create_collection_from_csv(
        self,
        file_path: str | Path,
        reference_database_revision: ReferenceDatabaseRevision | None = None,
        skiprows: int = 0,
        mapping: Mapping[str, TagKey] | Mapping[str, TagId] | None = None,
        metadata: AdditionalImportMetadata | None = None,
        organism: str | None = None,
    ) -> Execution[CollectionMetadata]:
        """Import a collection from a CSV file (can be gzipped).

        The file should be a CSV file with a couple of required headers. These headers must
        either be the tag IDs (for example: 2035, 2040) or tag keys (for example: Name, Organism).
        The following tags are required:

            - igx_api.l2.tags.CollectionTags.Name
            - igx_api.l2.tags.CollectionTags.Organism
            - igx_api.l2.tags.SequenceTags.SequenceCount
            - igx_api.l2.tags.SequenceTags.CDR3Nucleotides or igx_api.l2.tags.SequenceTags.CDR3AminoAcids
            - igx_api.l2.tags.SequenceTags.ReceptorNucleotides or igx_api.l2.tags.SequenceTags.FullSequenceNucleotides
            - igx_api.l2.tags.SequenceTags.VCall
            - igx_api.l2.tags.SequenceTags.JCall

        Args:
            file_path (str | Path): The path to the CSV file to import.
            reference_database_revision (igx_api.l2.types.reference_database.ReferenceDatabaseRevision | None): The reference database revision to use.
                If this is not provided, IGX will check the references available for the organism specified in the imported file. If there's only one
                reference available, it will be picked for the import and the job will continue. If there's none or there's multiple references
                available, an error will be returned - in such case reference has to be picked manually by passing it to this parameter.
                There is no downsides to always specifying the reference manually, which is a safer and less error-prone option.
            skiprows (int): Number of rows to skip at the beginning of the file, before reading the headers. Defaults to 0.
            mapping (Mapping[str, igx_api.l2.types.tag.TagKey] | Mapping[str, igx_api.l2.types.tag.TagId] | None): Mapping of the
              CSV headers to IGX Platform tag keys
            metadata (igx_api.l2.types.collection.AdditionalImportMetadata | None): Additional metadata to add to the collection.
                <u>**If the metadata keys overlap with the keys in the CSV (or with the values of the mapping), the metadata will take
                precedence when creating tags.**</u>
            organism: (str | None): If passed, it's compared with the organism value found in the first line of the imported file and
                throws an error if the values are different. Can serve as a quick utility check.

        Returns:
            igx_api.l2.types.collection.CollectionMetadata: Metadata of the collection that was imported.

        Raises:
            KeyError: If 'Organism' column is not found in the imported df/csv.
            ValueError: If optional `organism` param value differs from the 'Organism' value from the df/csv.
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with IgxApiClient() as igx_client:
                reference_name = ...
                species = ...
                reference = igx_client.reference_database_api.get_revision_by_name(
                    name=reference_name,
                    species=reference_species,
                )

                collection: CollectionMetadata = igx_client.collection_api.create_collection_from_csv(
                    file_path=import_file_path,
                    reference_database_revision=reference,
                    skiprows=1,
                    mapping={
                        "title": CollectionTags.Name,
                        "species": CollectionTags.Organism,
                    },
                    metadata={
                        CollectionTags.ProjectId: "Project 001",
                    }
                ).wait()
                ```
        """

        logger.info(f"Importing collection from CSV file `{file_path}`")

        # Pandas supports gzipped CSV
        df = pd.read_csv(file_path, sep=",", skiprows=skiprows)

        # Get the organism from the first line. All lines should hold the same value
        organism_from_file = str(df.iloc[0].get("Organism", None))
        if organism_from_file is None:
            # If not found by tag key, try to access it via the tag ID
            organism_from_file = str(df.iloc[0].get(CollectionTags.Organism, None))

        # If it's still none, raise an error - it's a mandatory column anyways
        if organism_from_file is None:
            raise KeyError("A required 'Organism' column was not found in the imported file/df")

        # If `organism` param was passed, compare the values
        if (organism is not None) and (organism != organism_from_file):
            raise ValueError(
                f"Value of 'organism' param: {organism} differs from the organism found in file: {organism_from_file}",
            )

        # Map the headers in the CSV file to IGX Tag Keys
        if mapping is not None:
            # We drop the columns for which no mapping is specified
            unmapped_headers = set(df.columns).difference(set(mapping.keys()))
            logger.warning(f"The following headers are unmapped and are removed:\n{unmapped_headers}")
            df.drop(columns=list(unmapped_headers), inplace=True)
            df.rename(columns=mapping, inplace=True)
        if metadata is not None:
            for key, value in metadata.items():
                df[key] = value

        temporary_csv_file_path = f"/tmp/import_collection_csv.{uuid4()}.csv"
        df.to_csv(temporary_csv_file_path, index=False)
        verify_headers_uniformity(list(df.columns))

        # Upload the file to the platform
        file_api = FileApi(self._inner_api_client, self._log_level)
        file = file_api.upload_file(temporary_csv_file_path).wait()

        collection_api_instance = openapi_client.CollectionApi(self._inner_api_client)

        # Start the collection import, this starts a job, so we'll wait for that to be completed
        import_collection_request = openapi_client.ImportCollectionRequest(
            file_id=file.id,
            organism=organism_from_file,
            reference_database_id=str(reference_database_revision.reference_database_id) if reference_database_revision is not None else None,
            reference_database_version=int(reference_database_revision.reference_database_version) if reference_database_revision is not None else None,
        )

        with ApiErrorContext():
            import_collection_response = collection_api_instance.import_collection(import_collection_request)
            assert import_collection_response.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(import_collection_response.workflow_execution_id)

            def on_complete(job_id: WorkflowExecutionTaskId, job_state: JobState) -> CollectionMetadata:
                assert job_state == JobState.SUCCEEDED, f"Job {job_id} did not reach {JobState.SUCCEEDED} state, got {job_state} state instead"

                get_collection_id_response = collection_api_instance.get_collection_id_by_workflow_execution_task_id(job_id)
                assert get_collection_id_response.collection_id is not None

                collection_id = CollectionId(get_collection_id_response.collection_id)

                logger.success(f"Collection with ID `{collection_id}` was successfully imported")
                # Remove the file from tmp folder
                os.remove(temporary_csv_file_path)
                # Remove the file from the platform
                file_api.delete_file_by_id(file.id)

                return self.get_collection_metadata_by_id(collection_id)

            waitable = WorkflowExecutionTaskWaitable[CollectionMetadata](
                workflow_execution_id=workflow_execution_id, task_template_name=WorkflowTaskTemplateName.ENPI_APP_COLLECTION_IMPORT, on_complete=on_complete
            )

            return Execution(wait=waitable.wait_and_return_result)

    def create_collection_from_df(
        self,
        data_frame: pd.DataFrame,
        reference_database_revision: ReferenceDatabaseRevision | None = None,
    ) -> Execution[CollectionMetadata]:
        """Import a collection from a DataFrame.

        This is a convenience method to import a collection from a Pandas DataFrame. For more information about the
        collection import, see igx_api.l2.client.api.collection_api.CollectionApi.create_collection_from_csv.

        Args:
            data_frame (pd.DataFrame): The DataFrame containing the collection to import.
            reference_database_revision (igx_api.l2.types.reference_database.ReferenceDatabaseRevision | None): The reference database revision to use.
                If this is not provided, IGX will check the references available for the organism specified in the imported file. If there's only one
                reference available, it will be picked for the import and the job will continue. If there's none or there's multiple references
                available, an error will be returned - in such case reference has to be picked manually by passing it to this parameter.
                There is no downsides to always specifying the reference manually, which is a safer and less error-prone option.
        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Returns:
            igx_api.l2.types.execution.Execution[igx_api.l2.types.collection.CollectionMetadata]: An awaitable that returns the
              collection that was imported when awaited.

        Example:

            ```python
            reference_name = ...
            species = ...
            reference = igx_client.reference_database_api.get_revision_by_name(
                name=reference_name,
                species=reference_species,
            )

            with IgxApiClient() as igx_client:
                df = pd.read_csv('/home/data.csv')
                collection: CollectionMetadata = igx_client.collection_api.create_collection_from_df(
                    data_frame=df,
                    reference_database_revision=reference,
                ).wait()
            ```
        """

        # We need to turn the DataFrame into a CSV file
        with tempfile.NamedTemporaryFile(suffix=".csv") as temp_file:
            data_frame.to_csv(temp_file.name, index=False)

            create_collection_execution = self.create_collection_from_csv(
                file_path=temp_file.name,
                reference_database_revision=reference_database_revision,
            )

        def wait() -> CollectionMetadata:
            return create_collection_execution.wait()

        return Execution(wait=wait)

    def add_metadata(self, filter: Filter, annotation: import_metadata.Annotation) -> Execution[None]:
        """Import metadata to annotate collections, clones or sequences in batches using a filter.

        This method allows you to simply annotate collections, clones or sequences using a filter. The annotation values
        that you provide will be applied to all matching items of the specified level.

        If you would like to add different values based on different matched tags, have a look at the methods that
        support a templated filter, such as `add_metadata_from_file` or `add_metadata_from_df`.

        Args:
            filter (igx_api.l2.types.filter.Filter): The filter to narrow down which collections, clones or sequences you wish to annotate.
              Use igx_api.l2.api.filter_api.FilterApi.create_filter to create new filters.
            annotation (igx_api.l2.types.import_metadata.Annotation): The annotation to apply to the matched collections, clones or sequences. You
              specify a specific annotation target and the values to apply. Utility functions igx_api.l2.types.import_metadata_templated.collection_annotation,
              igx_api.l2.types.import_metadata_templated.clone_annotation and igx_api.l2.types.import_metadata_templated.sequence_annotation
              are the preferred way of creating annotation configuration.

        Returns:
            igx_api.l2.types.execution.Execution[None]: An awaitable execution.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            Batch tag multiple collections with some tags:

            ```python
            with IgxApiClient() as igx_client:
                collection_ids = [CollectionId(1), CollectionId(2), CollectionId(3)]

                # Create a filter
                filter = igx_client.filter_api.create_filter(
                    name="My filter",
                    condition=dict(
                        type="match_ids",
                        target="collection",
                        ids=collection_ids,
                    ),
                )

                # Create an annotation
                annotation = collection_annotation(tags=[
                    Tag(id=CollectionTags.CampaignId, value="My campaign"),
                    Tag(id=CollectionTags.ProjectId, value="My project"),
                ])

                # Add the metadata
                igx_client.collection_api.add_metadata(filter=filter, annotation=annotation).wait()
            ```
        """

        collection_api_instance = openapi_client.CollectionApi(self._inner_api_client)

        import_metadata_request = openapi_client.ImportMetadataRequest(
            openapi_client.SearchAndTag(
                filter=openapi_client.FilterIdOptionalVersion(id=filter.id, version=filter.version),
                annotation=annotation.to_api_payload(),
            )
        )

        with ApiErrorContext():
            import_metadata_response = collection_api_instance.import_metadata(import_metadata_request)
            assert import_metadata_response.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(import_metadata_response.workflow_execution_id)

            waitable = WorkflowExecutionTaskWaitable[CollectionMetadata](
                workflow_execution_id=workflow_execution_id, task_template_name=WorkflowTaskTemplateName.ENPI_APP_METADATA_IMPORT
            )

            return Execution(wait=waitable.wait)

    def add_metadata_from_file(
        self,
        filter: TemplatedFilter,
        annotation: import_metadata_templated.Annotation,
        file_path: str | Path,
    ) -> Execution[None]:
        """Import metadata from a CSV or XLSX file to annotate collections, clones or sequences.

        Args:
            filter (igx_api.l2.types.filter.TemplatedFilter): The filter to narrow down which collections, clones or sequences you wish to annotate.
              Use igx_api.l2.api.filter_api.FilterApi.create_filter to create new filters.
            annotation (igx_api.l2.types.import_metadata_templated.Annotation): The annotation to apply to the matched collections, clones or sequences. You
              specify a specific annotation target and the values to apply. Utility functions igx_api.l2.types.import_metadata_templated.collection_annotation,
              igx_api.l2.types.import_metadata_templated.clone_annotation and igx_api.l2.types.import_metadata_templated.sequence_annotation
              are the preferred way of creating annotation configuration.
            file_path (str | Path): The path to the CSV or XLSX file to import.

        Returns:
            igx_api.l2.types.execution.Execution[None]: An awaitable execution.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            Assume you have a CSV file which describes 2 sequence tags to match on, and a tag to add to the matched sequences.

            Let's call the match columns *match_chain* and *match_productive*, and the column to add *value_to_add*.
            We'll add the value to a custom imaginary tag that was created before this example.

            The CSV file would look like this:

            | match_chain | match_productive | value_to_add |
            |-------------|------------------|--------------|
            | Heavy       | true             | Heavy and productive |
            | Heavy       | false            | Heavy and unproductive |
            | Kappa       | true             | Kappa and productive |
            | Kappa       | false            | Kappa and unproductive |
            | Lambda      | true             | Lambda and productive |
            | Lambda      | false            | Lambda and unproductive |

            We also want to narrow down the collections we want to annotate to a single collection with the imaginary ID *1337*.

            ```python
            my_collection_id: CollectionId = CollectionId(1337)

            tag_id_chain: TagId = TagId(SequenceTags.Chain)
            tag_id_productive: TagId = TagId(SequenceTags.Productive)
            tag_id_value_to_add: TagId = TagId(52001)  # This is a custom tag

            with IgxApiClient() as igx_client:
                filter = igx_client.filter_api.get_templated_filter_by_id(FilterId('92be003d-6f5c-447a-baac-c9d420783fc8'))
                igx_client.collection_api.add_metadata_from_file(
                    filter=filter,
                    annotation=sequence_annotation([
                        template_tag(tag_id=tag_id_value_to_add, key="value_to_add"),
                    ]),
                    file_path="path/to/metadata.csv",
                ).wait()
            ```
        """

        # We need to upload the file to the platform
        file_api = FileApi(self._inner_api_client, self._log_level)
        file_execution = file_api.upload_file(file_path)

        file: File

        def pre_steps() -> tuple[WorkflowExecutionId, WorkflowTaskTemplateName]:
            nonlocal file
            file = file_execution.wait()

            collection_api_instance = openapi_client.CollectionApi(self._inner_api_client)

            # Start the metadata import, this starts a job, so we'll wait for that to be completed
            import_metadata_request = openapi_client.ImportMetadataRequest(
                openapi_client.TemplatedSearchAndTag(
                    filter=openapi_client.FilterIdOptionalVersion(id=filter.id, version=filter.version),
                    annotation=annotation.to_api_payload(),
                    template_file_id=file.id,
                )
            )

            with ApiErrorContext():
                # The metadata import has not started yet because we first need to wait for the file upload
                import_metadata_response = collection_api_instance.import_metadata(import_metadata_request)
                assert import_metadata_response.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(import_metadata_response.workflow_execution_id)

            return (workflow_execution_id, WorkflowTaskTemplateName.ENPI_APP_METADATA_IMPORT_TEMPLATED)

        def on_complete(job_id: WorkflowExecutionTaskId, job_state: JobState) -> None:
            assert job_state == JobState.SUCCEEDED, f"Job {job_id} did not reach {JobState.SUCCEEDED} state, got {job_state} state instead"

            nonlocal file
            file_api.delete_file_by_id(file.id)

        waitable = WorkflowExecutionTaskWaitableWithPreSteps[None](pre_steps=pre_steps, on_complete=on_complete)

        return Execution(wait=waitable.wait)

    def add_metadata_from_df(
        self,
        filter: TemplatedFilter,
        annotation: import_metadata_templated.Annotation,
        data_frame: pd.DataFrame,
    ) -> Execution[None]:
        """Import metadata from a DataFrame to annotate collections, clones or sequences.

        This is a convenience method to import metadata from a Pandas DataFrame. For more information about the
        metadata import, see the documentation for `import_metadata_from_csv`.

        Args:
            filter (igx_api.l2.types.filter.TemplatedFilter): The filter to narrow down which collections, clones or sequences you wish to annotate.
            annotation (igx_api.l2.types.import_metadata_templated.Annotation): The annotation to apply to the matched collections, clones or sequences. You
              specify a specific annotation target and the values to apply.
            data_frame (pd.DataFrame): The DataFrame containing the templated metadata to import.

        Returns:
            igx_api.l2.types.execution.Execution[None]: An awaitable execution.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            Part of the `add_calculated_metadata.py` example script.

            ```python
            # Specify the filter query to match the sequences we want to add metadata to
            metadata_filter = client.filter_api.create_templated_filter(
                name="Metadata import filter",
                shared=False,
                condition=TemplatedAndOperator(
                    conditions=[
                        TemplatedMatchTag(tag_id=CollectionTags.Name),
                        TemplatedMatchId(target=MatchIdTarget.SEQUENCE),
                    ]
                ),
            )

            # Specify the sequence-level annotation to add to the collection
            metadata_annotation: Annotation = sequence_annotation([template_tag(new_tag_archetype.id)])

            # Create metadata dataframe
            metadata_frame = pd.DataFrame(
                [
                    [
                        collection_name,  # Match
                        df_row[1]["Unique Sequence ID"],  # Match
                        grouped_df.loc[df_row[1]["Unique Clone ID"]]["Sequence Count"],  # Add
                    ]
                    for df_row in exported_df.iterrows()
                ],
                columns=["Name", "Unique Sequence ID", new_tag_archetype.key],
            )

            # Apply metadata to the collection
            client.collection_api.add_metadata_from_df(
                filter=metadata_filter,
                annotation=metadata_annotation,
                data_frame=metadata_frame,
            ).wait()
            ```
        """

        # We need to turn the DataFrame into a CSV file
        temporary_csv_file_path = f"/tmp/import_metadata.{uuid4()}.csv"
        data_frame.to_csv(temporary_csv_file_path, index=False)

        return self.add_metadata_from_file(filter, annotation, temporary_csv_file_path)

    def get_as_zip(
        self,
        collection_ids: list[CollectionId],
        filter: Filter | None = None,
        tag_ids: list[TagId] = DEFAULT_EXPORT_TAG_IDS,
        output_directory: str | Path | None = None,
    ) -> Execution[Path]:
        """Export collection(s) into a zip file. Inside of the archive, each collection is exported to a separate TSV file.

        Args:
            collection_ids (list[igx_api.l2.types.collection.CollectionId]): The collection IDs to export.
            filter (igx_api.l2.types.filter.Filter | None): The filter to narrow down which collections, clones or sequences you wish to export.
                If it's `None`, a new filter that matches all the `collection_ids` provided above will be created and used.
            tag_ids (list[igx_api.l2.types.tag.TagId]): The tag IDs to include in the export.
            output_directory (str | Path | None): The directory path under which file will get exported. If
              not provided, a temporary directory will be used.

        Returns:
            igx_api.l2.types.execution.Execution[Path]: An awaitable that returns the full path to the exported file when
              awaited.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with IgxApiClient() as igx_client:

                collection_id = CollectionId(1234)

                # Example assumes you have a filter
                collection_filter: Filter = ...

                path: str = igx_client.collection_api.get_as_tsv(
                    collection_ids=[collection_id],
                    filter=collection_filter,
                    tag_ids=[
                        CollectionTags.Name,
                        CollectionTags.Organism,
                        CollectionTags.Complexity,
                        CollectionTags.Receptor,
                        SequenceTags.Chain,
                        SequenceTags.Productive,
                    ],
                    output_directory="example/export_result/"
                )
            ```
        """

        # Create the collectiom filter if it wasn't provided, it will match and
        # get all the clones from target collections
        if filter is None:
            filter_api = FilterApi(self._inner_api_client, self._log_level)
            filter = filter_api.create_filter(
                name=f"all-collection-clones-filter-{uuid4()}",  # Unique name to avoid collision
                condition=MatchIds(
                    target=MatchIdTarget.COLLECTION,
                    ids=collection_ids,  # Match all collection IDs passed to this function
                ),
            )

        # Start the collection export, this starts a job, so we'll wait for that to be completed
        export_collection_request = openapi_client.ExportRequest(
            payload=openapi_client.ExportPayload(
                collection_ids=[int(collection_id) for collection_id in collection_ids],
                filter=openapi_client.FilterIdOptionalVersion(id=filter.id, version=filter.version),
                tag_ids=[int(tag_id) for tag_id in tag_ids],
            )
        )
        collection_api_instance = openapi_client.CollectionApi(self._inner_api_client)

        with ApiErrorContext():
            export_collection_response = collection_api_instance.export(export_collection_request)
            assert export_collection_response.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(export_collection_response.workflow_execution_id)

            def on_complete(job_id: WorkflowExecutionTaskId, job_state: JobState) -> Path:
                file_api = FileApi(self._inner_api_client, self._log_level)
                file_path = file_api.download_export_by_workflow_execution_task_id(job_id=job_id, output_directory=output_directory)

                logger.success("Collection(s) export has succeeded.")
                return file_path

            waitable = WorkflowExecutionTaskWaitable[Path](
                workflow_execution_id=workflow_execution_id,
                on_complete=on_complete,
                task_template_name=WorkflowTaskTemplateName.ENPI_APP_COLLECTION_EXPORT,
            )

            return Execution(wait=waitable.wait_and_return_result)

    def get_as_df(
        self,
        collection_ids: list[CollectionId],
        filter: Filter | None = None,
        tag_ids: list[TagId] = DEFAULT_EXPORT_TAG_IDS,
    ) -> Execution[pd.DataFrame]:
        """Export collection(s) to a Pandas DataFrame.

        Args:
            collection_ids (list[igx_api.l2.types.collection.CollectionId]): The collection IDs to export.
            filter (igx_api.l2.types.filter.Filter | None): The filter to narrow down which collections, clones or sequences you wish to export.
                If it's `None`, a new filter that matches all the `collection_ids` provided above will be created and used.
            tag_ids (list[igx_api.l2.types.tag.TagId]): The tag IDs to include in the export.

        Returns:
            Execution[pd.DataFrame]: An awaitable that will return a DataFrame with the exported collection.

        Raises:
            igx_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```python
            with IgxApiClient() as igx_client:
                # Example assumes you have a filter
                filter: Filter = ...

                df: pd.DataFrame = igx_client.collection_api.get_as_df(
                    collection_ids=[CollectionId(1)],
                    filter=filter,
                    tag_ids=[CollectionTags.Name, CloneTags.TenXBarcode, SequenceTags.CDR3AminoAcids],
                )
            ```
        """
        tmp_dir = tempfile.TemporaryDirectory()
        get_as_zip_execution = self.get_as_zip(collection_ids=collection_ids, filter=filter, tag_ids=tag_ids, output_directory=tmp_dir.name)

        def wait() -> pd.DataFrame:
            zip_path = get_as_zip_execution.wait()

            # Extract all TSV files from the ZIP archive
            with ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmp_dir.name)

            # Read all TSV files into a single DataFrame
            all_dfs = []
            for root, _, files in os.walk(tmp_dir.name):
                for file in files:
                    if file.endswith(".tsv"):
                        file_path = os.path.join(root, file)
                        df = pd.read_csv(file_path, delimiter="\t")
                        all_dfs.append(df)

            return pd.concat(all_dfs)

        return Execution(wait=wait)
