"""Models for the Cognyx BOM SDK."""

from enum import Enum
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field, field_validator
from typing_extensions import TypedDict

from cognyx_bom_sdk.models import (
    Attribute,
    BomInstance,
    BomInstanceSystemAttributes,
    ObjectType,
    VariabilityConfiguration,
)


class BomStatus(Enum):
    """Status of a BOM."""

    DRAFT = "draft"
    APPROVED = "published"


class SystemAttributesStyling(TypedDict):
    """Styling for a system attribute."""

    color: str
    icon: str


class SystemAttributes(TypedDict):
    """System attributes for a diversity."""

    styling: SystemAttributesStyling


PermissionsList = TypeVar("PermissionsList", bound=str)


class Auth(TypedDict, Generic[PermissionsList]):
    """Authentication permissions for a diversity."""

    can: dict[PermissionsList, bool]


class Diversity(BaseModel):
    """Represents a diversity."""

    id: str
    name: str
    description: str | None = None
    reference: str | None = None
    created_at: str
    updated_at: str

    system_attributes: SystemAttributes

    auth: Auth[Literal["view"] | Literal["update"] | Literal["delete"]]


class BomReadinessView(TypedDict):
    """Readiness of a BOM view."""

    id: str
    name: str


class BomReadinessStatusCount(TypedDict):
    """Count of BOM readiness statuses."""

    not_started: int
    in_progress: int
    done: int


class BomReadiness(BaseModel):
    """Readiness of a BOM."""

    view: BomReadinessView
    total_instances: int
    statuses: BomReadinessStatusCount


class BomResponse(BaseModel):
    """Response from the Cognyx BOM API GET /bom/{bom_id}."""

    id: str
    name: str
    description: str | None = None
    reference: str | None = None
    image: str | None = None
    status: BomStatus

    created_at: str
    updated_at: str

    variability_configurations: None | list[Diversity] = []
    bom_readiness: None | list[BomReadiness] = []

    auth: Auth[
        Literal["comment"]
        | Literal["create"]
        | Literal["create_revision"]
        | Literal["delete"]
        | Literal["update"]
        | Literal["view"]
        | Literal["share"]
    ]


class BomInstanceResponse(BaseModel):
    """Response from the Cognyx BOM API GET /bom-instances/{instance_id}."""

    id: str = Field(..., min_length=1, description="Unique identifier for the BOM instance")
    name: str = Field(..., min_length=1, description="Name of the BOM instance")
    description: str | None = None
    bom_id: str
    view_id: str
    reference: str | None = None
    status: str
    custom_attributes: list[Attribute] = Field(default_factory=list)
    entity_type: ObjectType
    entity_type_id: str
    quantity: int | float | None
    variability_configurations: list[VariabilityConfiguration] = Field(default_factory=list)
    system_attributes: BomInstanceSystemAttributes = Field(
        default_factory=BomInstanceSystemAttributes
    )

    @field_validator("id", "name")
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("This field cannot be empty")
        return v


class BulkAttributesUpdateResponse(BaseModel):
    """Response from the Cognyx BOM API POST /bom-instances/attributes/bulk-update."""

    id: str
    name: str | None = None
    custom_attributes: list[dict] = []


class BomConfig(TypedDict):
    """BOM configuration."""

    default_type: Literal["tree"] | Literal["table"]
    default_view: str


class ProjectSettings(TypedDict):
    """Project settings."""

    bom: BomConfig


class FeaturesSettings(TypedDict):
    """Features settings."""

    boms: BomConfig


class GlobalSettingsResponse(BaseModel):
    """Response from the Cognyx BOM API GET /settings/global."""

    app_client_id: str
    cognyx_client_id: str
    features: FeaturesSettings


class RootBomNode(BaseModel):
    """Root bom node."""

    id: str
    label: str
    description: str | None = None
    reference: str | None = None
    group: Literal["Bom"]


class BomNodeSystemAttributes(TypedDict):
    """System attributes for a BOM node."""

    instance: BomInstance


class BomNode(BaseModel):
    """Node in a BOM tree."""

    id: str
    label: str
    description: str | None
    reference: str | None
    group: str
    system_attributes: BomNodeSystemAttributes


class BomEdge(BaseModel):
    """Edge in a BOM tree."""

    id: int
    source: str = Field(..., alias="from")
    target: str = Field(..., alias="to")


class BomTree(BaseModel):
    """Response from the Cognyx BOM API GET /bom/{bom_id}/tree."""

    nodes: list[RootBomNode | BomNode]
    edges: list[BomEdge]
