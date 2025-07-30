from enum import Enum
from typing import NewType

from igx_api.l1 import openapi_client
from igx_api.l2.types.cluster import ClusterId, ClusterRunId
from igx_api.l2.util.from_raw_model import FromRawModel

TreeId = NewType("TreeId", int)
"""The unique identifier of a tree."""


class TreeType(str, Enum):
    """Type of a tree."""

    NUCLEOTIDE = "nucleotide"
    AMINO_ACID = "amino_acid"


class Tree(FromRawModel[openapi_client.Tree]):
    """A single amino acid or nucleotide tree."""

    cluster_run_id: ClusterRunId
    """The unique identifier of a Cluster run."""
    cluster_id: ClusterId
    """The identifier of a cluster, unique only within a given Cluster run."""
    tree_id: TreeId
    """The unique identifier of a tree."""
    newick: str
    """Tree's representation in Newick format."""
    type: TreeType
    """Type of a tree."""

    @classmethod
    def _build(cls, raw: openapi_client.Tree) -> "Tree":
        return cls(
            cluster_run_id=ClusterRunId(raw.cluster_run_id),
            cluster_id=ClusterId(int(raw.cluster_id)),
            tree_id=TreeId(int(raw.tree_id)),
            newick=raw.newick,
            type=TreeType.NUCLEOTIDE if raw.type == "nucleotide" else TreeType.AMINO_ACID,
        )
