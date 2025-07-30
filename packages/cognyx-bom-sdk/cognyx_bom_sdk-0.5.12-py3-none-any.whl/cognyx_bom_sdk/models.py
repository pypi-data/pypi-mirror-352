"""Models for the Cognyx BOM SDK."""

from collections.abc import Callable
from enum import Enum
from typing import Any, Optional, TypeAlias

from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import TypedDict

JsonObject: TypeAlias = dict[str, Any]  # Type alias for JSON-like objects


class BomUpdates(Enum):
    """Enum for different types of BOM updates."""

    INSTANCE_UPDATE = "instance_update"
    ATTRIBUTE_UPDATE = "attribute_update"


class BomReadinessStatus(Enum):
    """Enum for different types of BOM readiness statuses."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class BomInstanceSystemStatus(Enum):
    """Enum for different types of BOM instance system statuses."""

    IS_OPTIONAL = "is_optional"
    HAS_VARIANTS = "has_variants"
    HAS_WARNING_NO_VARIABILITY = "has_warning_no_variability"
    IS_STANDARD = "is_standard"


class BomInstanceSystemAttributes(BaseModel):
    """Represents the system attributes of a BOM instance."""

    statuses: list[str | BomInstanceSystemStatus] = Field(default_factory=list)


class Attribute(BaseModel):
    """Represents an attribute."""

    id: str
    name: str
    description: str = ""
    slug: str = ""
    value: Any | None = None
    options: list[str] | list[JsonObject] | JsonObject | None = None
    attribute_id: str | None = None
    type: str | None = None


class ObjectType(BaseModel):
    """Represents an object type."""

    id: str
    name: str
    description: str | None = None
    slug: str
    base_unit: str
    bom_attributes: list[Attribute] = Field(default_factory=list)
    catalog_attributes: list[Attribute] = Field(default_factory=list)
    parent_id: str | None = None
    parent: Optional["ObjectType"] = None
    display_name: str

    def get_attribute_id(self, attribute_name: str) -> str | None:
        """Get an attribute value from the object type.

        Args:
            attribute_name: Name of the attribute to retrieve

        Returns:
            The attribute value or None if not found
        """
        attribute = next(
            (attr for attr in self.bom_attributes if attr.name.lower() == attribute_name.lower()),
            None,
        )
        return attribute.id if attribute else None


class Diversity(BaseModel):
    """Represents a diversity."""

    id: str
    name: str
    description: str | None = None
    reference: str | None = None


class Object(BaseModel):
    """Represents an object."""

    id: str
    name: str
    description: str | None = None
    reference: str | None = None
    status: str
    object_type: ObjectType
    object_type_id: str
    attributes: list[Attribute] = Field(default_factory=list)


class VariabilityConfiguration(BaseModel):
    """Represents a configuration for a BOM instance."""

    id: str
    variability_id: str
    variability: Diversity
    object_id: str
    object: Object


class AttributeUpdate(TypedDict):
    """Represents an attribute update."""

    attribute_id: str
    value: str | int | float | bool | dict | list | None


class BomInstanceUpdate(TypedDict, total=False):
    """TypedDict for BomInstance update properties.

    This defines all the properties that can be updated on a BomInstance.
    The total=False means all fields are optional.
    """

    name: str | None
    description: str | None
    reference: str | None
    custom_attributes: list[AttributeUpdate] | None
    parent_id: str | None
    object_type_id: str | None
    quantity: int | float | None


class BomInstance(BaseModel):
    """Represents a BOM instance in the Cognyx system."""

    id: str = Field(..., min_length=1, description="Unique identifier for the BOM instance")
    name: str = Field(..., min_length=1, description="Name of the BOM instance")
    description: str | None = None
    bom_id: str
    view_id: str
    parent_id: str
    reference: str | None = None
    status: str
    custom_attributes: list[Attribute] = Field(default_factory=list)
    object_type: ObjectType
    object_type_id: str
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

    def get_attribute(self, attribute_name: str) -> str | int | float | bool | dict | list | None:
        """Get an attribute value from the BOM instance.

        Args:
            attribute_name: Name of the attribute to retrieve

        Returns:
            The attribute value or None if not found
        """
        attribute = next(
            (
                attr
                for attr in self.custom_attributes
                if attr.name.lower() == attribute_name.lower()
            ),
            None,
        )
        return attribute.value if attribute else None

    def set_attribute(
        self, attribute_name: str, value: str | int | float | bool | dict | list | None
    ) -> None:
        """Set an attribute value on the BOM instance.

        Args:
            attribute_name: Name of the attribute to set
            value: Value to set for the attribute
        """
        attribute = next(
            (attr for attr in self.custom_attributes if attr.name == attribute_name), None
        )
        if attribute:
            attribute.value = value
        else:
            attribute_id = self.object_type.get_attribute_id(attribute_name)
            if attribute_id:
                self.custom_attributes.append(
                    Attribute(id=attribute_id, name=attribute_name, value=value)
                )
            else:
                raise ValueError(f"Attribute '{attribute_name}' not found in object type")

    def set_property(self, property_name: str, value: str | int | float | None) -> None:
        """Set a property value on the BOM instance.

        Args:
            property_name: Name of the property to set
            value: Value to set for the property
        """
        setattr(self, property_name, value)

    def find_variability_configuration(
        self, predicate: Callable[[VariabilityConfiguration], bool]
    ) -> VariabilityConfiguration | None:
        """Find a variability configuration by a predicate.

        Args:
            predicate: A function that takes a VariabilityConfiguration and returns a boolean

        Returns:
            The first VariabilityConfiguration that matches the predicate, or None if not found
        """
        return next(
            (config for config in self.variability_configurations if predicate(config)), None
        )

    def is_optional(self) -> bool:
        """Check if the BOM instance is optional.

        Returns:
            bool: True if the BOM instance is optional, False otherwise
        """
        return BomInstanceSystemStatus.IS_OPTIONAL in self.system_attributes.statuses

    def has_variants(self) -> bool:
        """Check if the BOM instance has variants.

        Returns:
            bool: True if the BOM instance has variants, False otherwise
        """
        return BomInstanceSystemStatus.HAS_VARIANTS in self.system_attributes.statuses

    def is_standard(self) -> bool:
        """Check if the BOM instance is standard.

        Returns:
            bool: True if the BOM instance is standard, False otherwise
        """
        return BomInstanceSystemStatus.IS_STANDARD in self.system_attributes.statuses

    def has_warning_no_variability(self) -> bool:
        """Check if the BOM instance has a warning due to no variability.

        Returns:
            bool: True if the BOM instance has a warning due to no variability, False otherwise
        """
        return BomInstanceSystemStatus.HAS_WARNING_NO_VARIABILITY in self.system_attributes.statuses


class AttributeUpdatePayload(TypedDict):
    """TypedDict for attribute update payload."""

    instance_id: str
    attribute_id: str
    attribute_value: Any


class InstanceUpdatePayload(TypedDict):
    """TypedDict for instance update payload."""

    instance_id: str
    properties: BomInstanceUpdate


class UpdatePayload(TypedDict):
    """TypedDict for update payload with discriminated union pattern."""

    type: BomUpdates
    payload: AttributeUpdatePayload | InstanceUpdatePayload


class Bom(BaseModel):
    """Represents a complete BOM with all its instances."""

    id: str = Field(..., min_length=1, description="Unique identifier for the BOM")
    name: str = Field(..., min_length=1, description="Name of the BOM")
    reference: str | None = None
    description: str | None = None
    status: str
    instances: list[BomInstance] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_model(self) -> "Bom":
        """Validate the entire model after all fields are populated."""
        if not self.id:
            raise ValueError("BOM ID cannot be empty")
        if not self.name:
            raise ValueError("BOM name cannot be empty")
        return self

    def get_instance(self, name: str) -> BomInstance | None:
        """Get a BOM instance by name.

        Args:
            name: The name of the BOM instance to retrieve

        Returns:
            The BOM instance or None if not found
        """
        return next(
            (instance for instance in self.instances if instance.name.lower() == name.lower()), None
        )

    def get_instance_by_id(self, instance_id: str) -> BomInstance | None:
        """Get a BOM instance by ID.

        Args:
            instance_id: The ID of the BOM instance to retrieve

        Returns:
            The BOM instance or None if not found
        """
        return next((instance for instance in self.instances if instance.id == instance_id), None)


class Originator(TypedDict):
    """Represents an originator in the Cognyx system - i.e who made the request."""

    name: str
    value: str | None
