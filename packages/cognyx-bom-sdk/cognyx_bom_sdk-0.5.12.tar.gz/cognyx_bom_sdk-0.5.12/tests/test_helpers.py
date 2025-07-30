from cognyx_bom_sdk.cognyx.helpers import format_bom, format_instance, get_parent_map
from cognyx_bom_sdk.cognyx.models import BomEdge, BomInstanceResponse, BomResponse
from cognyx_bom_sdk.models import BomInstanceSystemAttributes, ObjectType


def test_get_parent_map():
    edges = [
        BomEdge.model_validate({"id": 1, "from": "parent1", "to": "child1"}),
        BomEdge.model_validate({"id": 2, "from": "parent2", "to": "child2"}),
    ]
    result = get_parent_map(edges)
    assert result == {"child1": "parent1", "child2": "parent2"}


def test_format_instance():
    instance = BomInstanceResponse(
        id="iid",
        name="Instance",
        reference="ref",
        description="desc",
        quantity=2,
        status="active",
        entity_type=ObjectType(
            id="typeA-id",
            name="typeA",
            description="desc",
            slug="typeA",
            base_unit="unit",
            display_name="TypeA",
            label="TypeA",
            created_at="",
            updated_at="",
            bom_attributes=[],
        ),
        entity_type_id="typeA-id",
        system_attributes=BomInstanceSystemAttributes(statuses=[]),
        custom_attributes=[],
        bom_id="bom-id",
        view_id="view-id",
        variability_configurations=[],
    )
    result = format_instance(instance, "bom-id", "view-id", "parent-id")
    assert result.id == "iid"
    assert result.parent_id == "parent-id"
    assert result.bom_id == "bom-id"
    assert isinstance(result.object_type, ObjectType)
    assert result.custom_attributes == []


def test_format_bom():
    from cognyx_bom_sdk.models import BomInstance, ObjectType

    bom = BomResponse(
        id="bom-id",
        name="BOM",
        description="desc",
        reference="ref",
        image=None,
        status="draft",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        variability_configurations=[],
        bom_readiness=[],
        auth={
            "can": {
                "view": True,
                "update": False,
                "delete": False,
                "comment": False,
                "create": False,
                "create_revision": False,
                "share": False,
            }
        },
    )
    instance = BomInstance(
        id="iid",
        name="Instance",
        parent_id="parent-id",
        reference="ref",
        description="desc",
        quantity=1,
        status="active",
        bom_id="bom-id",
        view_id="view-id",
        object_type=ObjectType(
            id="typeA-id",
            name="typeA",
            description="desc",
            slug="typeA",
            base_unit="unit",
            display_name="TypeA",
            label="TypeA",
            created_at="",
            updated_at="",
            bom_attributes=[],
        ),
        object_type_id="typeA-id",
        variability_configurations=[],
        system_attributes={"statuses": []},
        custom_attributes=[],
    )
    instances = [instance]
    result = format_bom(bom, instances)
    assert result.id == "bom-id"
    assert result.instances == instances
