from datetime import datetime
from enum import Enum
from typing import Literal, NewType, cast

from pydantic import BaseModel
from typing_extensions import assert_never

from igx_api.l1 import openapi_client
from igx_api.l2.types.cluster import ClusterRunId
from igx_api.l2.types.collection import CollectionId
from igx_api.l2.types.tag import TagId, TagValue
from igx_api.l2.util.from_raw_model import FromRawModel

TrackRunId = NewType("TrackRunId", int)
"""The unique identifier of a Track Run."""

TrackTemplateId = NewType("TrackTemplateId", str)
"""The unique identifier of a Track Template."""

TrackTemplateVersion = NewType("TrackTemplateVersion", int)
"""The Version of a Track Template."""


class TrackOperationType(str, Enum):
    """Types of operations available in Track."""

    UNION = "union"
    INTERSECTION = "intersection"
    DIFFERENCE = "difference"
    FOLD_CHANGE = "fold_change"


class SimplifiedTrackOperation(BaseModel):
    """Simplified read model for Track Operation."""

    name: str
    """Operation name."""
    type: TrackOperationType
    """Operation type."""


class SimplifiedTrackTemplate(BaseModel):
    """Simplified read model for Track Template."""

    id: TrackTemplateId
    """Track Template Id."""
    name: str
    """Operation name."""
    created_at: datetime | None
    """Date when the template was created."""


class CollectionByIdSelector(BaseModel):
    """Selects a collection by matching it with the provided unique ID."""

    type: Literal["collection_id"] = "collection_id"
    """Internal type used to recognize the selector object."""
    value: CollectionId
    """The unique identifier of a collection."""


class CollectionByNameSelector(BaseModel):
    """Selects a collection by matching it with the provided unique ID."""

    type: Literal["collection_name"] = "collection_name"
    """Internal type used to recognize the selector object."""
    value: str
    """The name of a collection."""


class CollectionByTagValueSelector(BaseModel):
    """Selects a collection by matching it with the provided unique ID."""

    type: Literal["collection_tag_value"] = "collection_tag_value"
    """Internal type used to recognize the selector object."""
    tag_id: TagId
    """The collection tag id"""
    tag_value: TagValue
    """The tag value to look for"""


class SetOperationSelector(BaseModel):
    """Selects a collection by matching it with the provided unique ID."""

    type: Literal["set_operation"] = "set_operation"
    """Internal type used to recognize the selector object."""
    value: str
    """The set operation name"""


CollectionSelector = CollectionByIdSelector | CollectionByNameSelector | CollectionByTagValueSelector
TrackTemplateNodeInput = CollectionByIdSelector | CollectionByNameSelector | CollectionByTagValueSelector | SetOperationSelector


class TrackRun(FromRawModel[openapi_client.TrackRun]):
    """Existing Track Run configuration."""

    id: TrackRunId
    """Track Run Id."""
    name: str
    """Track Run name."""
    template_id: TrackTemplateId
    """Track Template Id."""
    template_version: TrackTemplateVersion
    """Track Template Version."""
    cluster_run_id: ClusterRunId
    """Cluster Run Id."""
    operations: list[SimplifiedTrackOperation]
    """List of operations present in this Track run."""

    @classmethod
    def _build(cls, raw: openapi_client.TrackRun) -> "TrackRun":
        assert raw.id is not None
        return cls(
            id=TrackRunId(raw.id),
            name=str(raw.name),
            template_id=TrackTemplateId(raw.template.id),
            template_version=TrackTemplateVersion(raw.template.version),
            cluster_run_id=ClusterRunId(raw.cluster_run_id),
            operations=[SimplifiedTrackOperation(name=d.name, type=TrackOperationType(d.type)) for d in raw.operations],
        )


class TrackTemplateFoldChangeInputs(BaseModel):
    """Track Fold change input operations that can be specified within the Track template.

    The results of the operations specified for this object will be used as inputs
    for the fold change measeurement computation.

    Example:
        Fold change ratio between results "A" and "B" after operation "C" is done equals 2.
    """

    from_input: TrackTemplateNodeInput | None = None
    """Previously computed operation results or input clone collections.
        Serves as the `B` value in the `A`/`B` fold change ratio formula."""
    to_input: TrackTemplateNodeInput | None = None
    """Previously computed operation results or input clone collections.
        Serves as the `A` value in the `A`/`B` fold change ratio formula."""


class TrackTemplateFoldChangeAnnotation(FromRawModel[openapi_client.TrackTemplateFoldChangeAnnotation]):
    """Track fold change annotation computed for input operations results, defined within a Track template."""

    name: str
    """Name of the fold change annotation annotation. Has to be unique."""
    inputs: TrackTemplateFoldChangeInputs | None = None
    """Fold change input operations, a results of previously planned (performed during Track run) operations within the template."""

    @classmethod
    def _build(cls, raw: openapi_client.TrackTemplateFoldChangeAnnotation) -> "TrackTemplateFoldChangeAnnotation":
        return cls(
            name=str(raw.name),
            inputs=TrackTemplateFoldChangeInputs(
                from_input=build_node_input(raw.inputs.var_from) if raw.inputs.var_from is not None else None,
                to_input=build_node_input(raw.inputs.to) if raw.inputs.to is not None else None,
            )
            if raw.inputs is not None
            else None,
        )


class TrackTemplateUnionOperation(FromRawModel[openapi_client.TrackTemplateJoinOperation]):
    """Definition of a Track union operation performed on the results of provided operations."""

    name: str
    """Name of the union operation. Has to be unique."""
    inputs: list[TrackTemplateNodeInput] | None = None
    """A list of input operations for results of which the union will be applied."""
    annotations: list[TrackTemplateFoldChangeAnnotation] | None = None
    """Optional annotations to be added onto this operation result."""

    @classmethod
    def _build(cls, raw: openapi_client.TrackTemplateJoinOperation) -> "TrackTemplateUnionOperation":
        return cls(
            name=str(raw.name),
            inputs=[build_node_input(inp) for inp in raw.inputs],
            annotations=[TrackTemplateFoldChangeAnnotation.from_raw(x) for x in raw.annotations] if raw.annotations is not None else None,
        )


class TrackTemplateIntersectionOperation(FromRawModel[openapi_client.TrackTemplateJoinOperation]):
    """Definition of a Track intersection operation performed on the results of provided operations."""

    name: str
    """Name of the intersection operation. Has to be unique."""
    inputs: list[TrackTemplateNodeInput] | None = None
    """A list of input operations for results of which the intersection will be applied."""
    annotations: list[TrackTemplateFoldChangeAnnotation] | None = None
    """Optional annotations to be added onto this operation result."""

    @classmethod
    def _build(cls, raw: openapi_client.TrackTemplateJoinOperation) -> "TrackTemplateIntersectionOperation":
        return cls(
            name=str(raw.name),
            inputs=[build_node_input(inp) for inp in raw.inputs],
            annotations=[TrackTemplateFoldChangeAnnotation.from_raw(x) for x in raw.annotations] if raw.annotations is not None else None,
        )


class TrackTemplateDifferenceInputs(BaseModel):
    """Track difference operation inputs that can be specified within
    the Track template.

    Example:
        Assuming two operations `Operation A` and `Operation B` were already specified in the Track template:

        ```python
        # A difference operation specified in the Track template
        TrackTemplateDifferenceOperation(
            name="Operation C",
            input_operations=TrackTemplateDifferenceInputs(
                remove_operation="Operation A",
                from_operation="Operation B",
            ),
        ),
        ```
    """

    remove_input: TrackTemplateNodeInput | None = None
    """Clusters from this operation will be subtracted from the other one."""
    from_input: TrackTemplateNodeInput | None = None
    """Clusters from the other operation result will be subtracted from this one."""


class TrackTemplateDifferenceOperation(FromRawModel[openapi_client.TrackTemplateDifferenceOperation]):
    """Definition of a Track difference operation performed on the results of provided operations."""

    name: str
    """Name of the difference operation. Has to be unique."""
    inputs: TrackTemplateDifferenceInputs | None = None
    """Track difference operation inputs that can be specified within the Track template."""
    annotations: list[TrackTemplateFoldChangeAnnotation] | None = None
    """Optional annotations to be added onto this operation result."""

    @classmethod
    def _build(cls, raw: openapi_client.TrackTemplateDifferenceOperation) -> "TrackTemplateDifferenceOperation":
        return cls(
            name=str(raw.name),
            inputs=TrackTemplateDifferenceInputs(
                remove_input=build_node_input(raw.inputs.remove) if raw.inputs.remove is not None else None,
                from_input=build_node_input(raw.inputs.var_from) if raw.inputs.var_from is not None else None,
            ),
            annotations=[TrackTemplateFoldChangeAnnotation.from_raw(x) for x in raw.annotations] if raw.annotations is not None else None,
        )


TrackTemplateOperation = TrackTemplateUnionOperation | TrackTemplateIntersectionOperation | TrackTemplateDifferenceOperation
"""A single Track operation definition present in the Track template.

    In general, those are used to to define what operations will be performed during the Track run.
    They need to have unique names (for matching purposes) and either need other operations within the template to be specified
    as their inputs or have inputs matched with them later on via `igx_api.l2.types.track.TrackWorkInput`.
"""


class TrackTemplate(FromRawModel[openapi_client.TrackTemplate]):
    """Track Template configuration."""

    id: TrackTemplateId
    """The unique identifier of a Track Template."""
    version: TrackTemplateVersion
    """The version of a Track Template"""
    name: str
    """Name of a Track Template."""
    created_at: datetime
    """Date of the Track Template's creation."""
    operations: list[TrackTemplateOperation]
    """List of operations present in this Track Run."""
    saved: bool
    """Indicates whether the template is reusable"""

    @classmethod
    def _build(cls, raw: openapi_client.TrackTemplate) -> "TrackTemplate":
        assert raw.created_at is not None

        return cls(
            id=TrackTemplateId(raw.id),
            version=TrackTemplateVersion(raw.version),
            name=str(raw.name),
            saved=raw.saved,
            created_at=raw.created_at,
            operations=[build_operation(d) for d in raw.operations],
        )


def transform_to_nullable_node_input(inp: TrackTemplateNodeInput | None) -> openapi_client.NullishTrackTemplateNodeInput:
    """An internal function used for transforming Track template node input config into API format.
    @private

    Args:
        inp (TrackTemplateNodeInput): Track template node input in "user format".

    Returns:
        openapi_client.NullishTrackTemplateNodeInput: Track template node input in "API format".
    """
    if inp is None:
        return cast(openapi_client.NullishTrackTemplateNodeInput, None)
    else:
        return openapi_client.NullishTrackTemplateNodeInput.from_dict(inp.model_dump())


def transform_to_node_input(inp: TrackTemplateNodeInput) -> openapi_client.TrackTemplateNodeInput:
    """An internal function used for transforming Track template node input config into API format.
    @private

    Args:
        inp (TrackTemplateNodeInput): Track template node input in "user format".

    Returns:
        openapi_client.TrackTemplateNodeInput: Track template node input in "API format".
    """
    return openapi_client.TrackTemplateNodeInput.from_dict(inp.model_dump())


def build_node_input(inp: openapi_client.TrackTemplateNodeInput | openapi_client.NullishTrackTemplateNodeInput) -> TrackTemplateNodeInput:
    """An internal function used for transforming Track template node inputs from API format to "user format".
    @private

    Args:
        inp (openapi_client.TrackTemplateTrackNodeInput): Track template node input in "API format".

    Returns:
        TrackTemplateNodeInput: Track template in "user format".
    """

    if isinstance(inp.actual_instance, openapi_client.UnionOperationInputsInputsInner):
        if isinstance(inp.actual_instance.actual_instance, openapi_client.MatchCollectionByItsID):
            assert inp.actual_instance.actual_instance.value is not None
            return CollectionByIdSelector(value=CollectionId(inp.actual_instance.actual_instance.value))
        elif isinstance(inp.actual_instance.actual_instance, openapi_client.MatchCollectionByItsName):
            return CollectionByNameSelector(value=inp.actual_instance.actual_instance.value)
        elif isinstance(inp.actual_instance.actual_instance, openapi_client.MatchCollectionByTagValue):
            value: openapi_client.MatchCollectionByTagValueValue = inp.actual_instance.actual_instance.value
            assert value.tag_id is not None
            return CollectionByTagValueSelector(tag_id=TagId(int(value.tag_id)), tag_value=str(value.tag_value))
        else:
            raise ValueError("Wrong Track operation type")
    elif isinstance(inp.actual_instance, openapi_client.SetOperationInput):
        return SetOperationSelector(value=inp.actual_instance.value)
    else:
        raise ValueError("Wrong Track operation type")


def transform_operation(op: TrackTemplateOperation) -> openapi_client.TrackTemplateTrackOperation:
    """An internal function used for transforming Track template operations config into API format.
    @private

    Args:
        op (TrackTemplateOperation): Track template operation in "user format".

    Returns:
        openapi_client.TrackTemplateTrackOperation: Track template in "API format".
    """
    annotations = (
        [
            openapi_client.TrackTemplateFoldChangeAnnotation(
                name=x.name,
                type=TrackOperationType.FOLD_CHANGE,
                inputs=openapi_client.TrackTemplateFoldChangeAnnotationInputs(
                    **{
                        "from": transform_to_nullable_node_input(x.inputs.from_input) if x.inputs is not None else None,
                        "to": transform_to_nullable_node_input(x.inputs.to_input) if x.inputs is not None else None,
                    }
                ),
            )
            for x in op.annotations
        ]
        if op.annotations is not None
        else None
    )

    if isinstance(op, TrackTemplateUnionOperation):
        return openapi_client.TrackTemplateTrackOperation(
            openapi_client.TrackTemplateJoinOperation(
                name=op.name,
                type=TrackOperationType.UNION,
                inputs=[transform_to_node_input(inp) for inp in (op.inputs or [])],
                annotations=annotations,
            )
        )
    elif isinstance(op, TrackTemplateIntersectionOperation):
        return openapi_client.TrackTemplateTrackOperation(
            openapi_client.TrackTemplateJoinOperation(
                name=op.name,
                type=TrackOperationType.INTERSECTION,
                inputs=[transform_to_node_input(inp) for inp in (op.inputs or [])],
                annotations=annotations,
            )
        )
    elif isinstance(op, TrackTemplateDifferenceOperation):
        return openapi_client.TrackTemplateTrackOperation(
            openapi_client.TrackTemplateDifferenceOperation(
                name=op.name,
                type=TrackOperationType.DIFFERENCE,
                inputs=openapi_client.TrackTemplateDifferenceOperationInputs(
                    **{
                        "remove": transform_to_nullable_node_input(op.inputs.remove_input) if op.inputs is not None else None,
                        "from": transform_to_nullable_node_input(op.inputs.from_input) if op.inputs is not None else None,
                    }
                ),
                annotations=annotations,
            )
        )
    else:
        raise ValueError("Wrong Track operation type")


def build_operation(op: openapi_client.TrackTemplateTrackOperation) -> TrackTemplateOperation:
    """An internal function used for transforming Track template operations config from API format to "user format".
    @private

    Args:
        op (openapi_client.TrackTemplateTrackOperation): Track template operation in "API format".

    Returns:
        TrackTemplateOperation: Track template in "user format".
    """
    if isinstance(op.actual_instance, openapi_client.TrackTemplateJoinOperation):
        if op.actual_instance.type == TrackOperationType.UNION:
            return TrackTemplateUnionOperation.from_raw(op.actual_instance)
        else:
            return TrackTemplateIntersectionOperation.from_raw(op.actual_instance)
    elif isinstance(op.actual_instance, openapi_client.TrackTemplateDifferenceOperation):
        return TrackTemplateDifferenceOperation.from_raw(op.actual_instance)
    else:
        raise ValueError("Wrong Track operation type")


class UnionOperationInput(BaseModel):
    """Used to specify input collections for union operation during Track run configuration."""

    name: str
    """Name of the union operation. Has to match the one defined in the Track template."""
    inputs: list[CollectionSelector]
    """A list of input clone collections."""


class IntersectionOperationInput(BaseModel):
    """Used to specify input collections for intersection operation during Track run configuration."""

    name: str
    """Name of the intersection operation. Has to match the one defined in the Track template."""
    inputs: list[CollectionSelector]
    """A list of input clone collections."""


class DifferenceOperationInputs(BaseModel):
    """Used to specify input collections for difference operation during Track run configuration."""

    remove_input: CollectionSelector | None = None
    """Clusters from this collection will be removed from the other one."""
    from_input: CollectionSelector | None = None
    """Clusters from the other collection will be removed from this one."""


class DifferenceOperationInput(BaseModel):
    """Used to specify input collections for intersection operation during Track run configuration."""

    name: str
    """Name of the intersection operation. Has to match the one defined in the Track template."""
    inputs: DifferenceOperationInputs | None = None
    """Used to specify input collections for difference operation during Track run configuration."""


class FoldChangeInputs(BaseModel):
    """Track Fold change input operations that can be specified during the Track run configuration.

    The clone collection inputs specified for this object will be used as inputs
    for the fold change measeurement computation.

    Example:
        Fold change ratio between results "A" and "B" after operation "C" is done equals 2.
    """

    from_input: CollectionSelector | None = None
    """An input clone collection.
        Serves as the `B` value in the `A`/`B` fold change ratio formula."""
    to_input: CollectionSelector | None = None
    """An input clone collection.
        Serves as the `A` value in the `A`/`B` fold change ratio formula."""


class FoldChangeInput(BaseModel):
    """Track fold change annotation specification."""

    name: str
    """Name of the fold change annotation annotation. Has to match the one defined in the Track template."""
    operation_name: str
    """Name of the operation this annotation belongs to. Has to match the one defined in the Track template."""
    inputs: FoldChangeInputs | None = None
    """Input collections for the fold change."""


TrackWorkInput = UnionOperationInput | IntersectionOperationInput | DifferenceOperationInput | FoldChangeInput
"""An input for Track run configuration, used to provide data for the operations and annotations specified
    previously within the Track template configuration.

    In general, they need to match the unique names specified within Track templates in order to fill them
    with the clustered clone data - for info about the templates, see `igx_api.l2.types.track.TrackTemplateOperation`.
"""


def transform_collection_selector(
    sel: CollectionSelector,
) -> openapi_client.MatchCollectionByItsID | openapi_client.MatchCollectionByItsName | openapi_client.MatchCollectionByTagValue:
    """Internal transform function for collection selectors.
    @private
    """
    if isinstance(sel, CollectionByIdSelector):
        return openapi_client.MatchCollectionByItsID(type="collection_id", value=int(sel.value))
    if isinstance(sel, CollectionByNameSelector):
        return openapi_client.MatchCollectionByItsName(type="collection_name", value=sel.value)
    if isinstance(sel, CollectionByTagValueSelector):
        return openapi_client.MatchCollectionByTagValue(
            type="collection_tag_value", value=openapi_client.MatchCollectionByTagValueValue(tag_id=sel.tag_id, tag_value=str(sel.tag_value))
        )
    else:
        assert_never(sel)


def transform_operation_input(input_value: TrackWorkInput) -> openapi_client.TrackWorkInputsInner:
    """Internal transform function for operation inputs.
    @private
    """
    if isinstance(input_value, UnionOperationInput):
        return openapi_client.TrackWorkInputsInner(
            openapi_client.UnionOperationInputs(
                name=input_value.name,
                type=TrackOperationType.UNION,
                inputs=[openapi_client.UnionOperationInputsInputsInner(transform_collection_selector(x)) for x in input_value.inputs],
            )
        )
    elif isinstance(input_value, IntersectionOperationInput):
        return openapi_client.TrackWorkInputsInner(
            openapi_client.IntersectionOperationInputs(
                name=input_value.name,
                type=TrackOperationType.INTERSECTION,
                inputs=[openapi_client.UnionOperationInputsInputsInner(transform_collection_selector(x)) for x in input_value.inputs],
            )
        )
    elif isinstance(input_value, DifferenceOperationInput):
        return openapi_client.TrackWorkInputsInner(
            openapi_client.DifferenceOperationInputs(
                name=input_value.name,
                type=TrackOperationType.DIFFERENCE,
                inputs=openapi_client.DifferenceOperationInputsInputs(
                    **{
                        "remove": openapi_client.DifferenceOperationInputsInputsRemove(transform_collection_selector(input_value.inputs.remove_input))
                        if input_value.inputs is not None and input_value.inputs.remove_input is not None
                        else None,
                        "from": openapi_client.DifferenceOperationInputsInputsRemove(transform_collection_selector(input_value.inputs.from_input))
                        if input_value.inputs is not None and input_value.inputs.from_input is not None
                        else None,
                    }
                ),
            )
        )
    elif isinstance(input_value, FoldChangeInput):
        inputs = input_value.inputs
        assert inputs is not None

        return openapi_client.TrackWorkInputsInner(
            openapi_client.FoldChangeAnnotationInputs(
                name=input_value.name,
                operation_name=input_value.operation_name,
                type=TrackOperationType.FOLD_CHANGE,
                inputs=openapi_client.FoldChangeAnnotationInputsInputs(
                    **{
                        "from": openapi_client.DifferenceOperationInputsInputsRemove(transform_collection_selector(inputs.from_input))
                        if inputs.from_input is not None
                        else None,
                        "to": openapi_client.DifferenceOperationInputsInputsRemove(transform_collection_selector(inputs.to_input))
                        if inputs.to_input is not None
                        else None,
                    }
                ),
            )
        )
    else:
        assert_never(input_value)


class TrackExportMode(str, Enum):
    """Mode of Track export that determines the shape and content of the final file."""

    CLONES = "clones"
    """All clones from each cluster will be exported."""
    REPRESENTATIVES = "representatives"
    """Within each cluster, every unique CDR/FR sequence will be tallied and the most abundant sequence for each region will be chosen."""
    CONSENSUS = "consensus"
    """The clone abundance will be used to choose a representative from each cluster."""
