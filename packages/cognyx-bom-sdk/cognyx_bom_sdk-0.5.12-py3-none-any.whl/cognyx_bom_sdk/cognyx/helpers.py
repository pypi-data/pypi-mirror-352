"""Helper functions for the Cognyx BOM SDK."""

from cognyx_bom_sdk.cognyx.models import BomEdge, BomInstanceResponse, BomResponse
from cognyx_bom_sdk.models import Bom, BomInstance


def get_parent_map(edges: list[BomEdge]) -> dict[str, str]:
    """Get a map of child IDs to parent IDs.

    Args:
        edges: List of edges in the BOM tree

    Returns:
        A map of child IDs to parent IDs
    """
    parents_map: dict[str, str] = {}
    for edge in edges:
        parents_map[edge.target] = edge.source
    return parents_map


def format_instance(
    instance: BomInstanceResponse, bom_id: str, view_id: str, parent_id: str
) -> BomInstance:
    """Format a BOM instance.

    Args:
        instance: BOM instance data
        bom_id: ID of the BOM
        view_id: ID of the view
        parent_id: ID of the parent instance

    Returns:
        The formatted BOM instance data
    """
    return BomInstance(
        id=instance.id,
        name=instance.name,
        parent_id=parent_id,
        reference=instance.reference,
        description=instance.description,
        quantity=instance.quantity,
        status=instance.status,
        bom_id=bom_id,
        view_id=view_id,
        object_type=instance.entity_type,
        object_type_id=instance.entity_type_id,
        variability_configurations=[],
        system_attributes=instance.system_attributes,
        custom_attributes=instance.custom_attributes,
    )


def format_bom(bom: BomResponse, instances: list[BomInstance]) -> Bom:
    """Format a BOM.

    Args:
        bom: BOM data
        instances: List of BOM instance data

    Returns:
        The formatted BOM data
    """
    return Bom(
        id=bom.id,
        name=bom.name,
        reference=bom.reference,
        description=bom.description,
        status=str(bom.status),
        instances=instances,
    )
