"""Client module for the Cognyx BOM SDK."""

from collections.abc import Callable
from typing import Any

from typing_extensions import Unpack

from cognyx_bom_sdk.models import (
    Attribute,
    AttributeUpdatePayload,
    Bom,
    BomInstance,
    BomInstanceUpdate,
    BomUpdates,
    InstanceUpdatePayload,
    UpdatePayload,
)


def _parse_bom_data(bom_data: dict[str, Any]) -> Bom:
    """Parse the raw BOM data into a structured Bom object using Pydantic.

    Args:
        bom_data: Raw BOM data as a dictionary

    Returns:
        A structured Bom object

    Raises:
        ValidationError: If the data doesn't match the expected schema
    """
    # Pydantic will automatically validate the data against our model
    # and raise ValidationError if the data is invalid
    return Bom.model_validate(bom_data)


class BomClient:
    """Client for interacting with the Cognyx BOM API.

    This client is designed to be used in a Pyodide sandbox environment
    where it receives the full BOM data and provides methods to manipulate it.
    """

    def __init__(
        self,
        bom_data: dict[str, Any],
        update_callback: Callable[[UpdatePayload], None] | None = None,
    ) -> None:
        """Initialize the BOM client with the BOM data.

        Args:
            bom_data: The complete BOM data as a dictionary
            update_callback: Optional callback function that will be called with updates to apply to
            the BOM
        """
        self.bom = _parse_bom_data(bom_data)
        self.update_callback = update_callback
        # Type ignore for Any usage in callback

    def get_bom_instance(self, name: str) -> BomInstance | None:
        """Get a BOM instance by name.

        Args:
            name: The name of the BOM instance to retrieve

        Returns:
            The BOM instance or None if not found
        """
        return self.bom.get_instance(name)

    def get_bom_instance_by_id(self, instance_id: str) -> BomInstance | None:
        """Get a BOM instance by ID.

        Args:
            instance_id: The ID of the BOM instance to retrieve

        Returns:
            The BOM instance or None if not found
        """
        return self.bom.get_instance_by_id(instance_id)

    def find_bom_instance(self, predicate: Callable[[BomInstance], bool]) -> BomInstance | None:
        """Find a BOM instance using a predicate function.

        Args:
            predicate: A function that takes a BomInstance and returns True if it matches

        Returns:
            The first matching BOM instance or None if not found
        """
        return next((instance for instance in self.bom.instances if predicate(instance)), None)

    def list_bom_instances(self) -> list[BomInstance]:
        """List all BOM instances.

        Returns:
            List of all BOM instances
        """
        return self.bom.instances

    def get_instance_attribute(
        self, instance_id: str, attribute_name: str
    ) -> str | int | float | bool | dict | list | None:
        """Get an attribute value from a BOM instance.

        Args:
            instance_id: ID of the BOM instance
            attribute_name: Name of the attribute to retrieve

        Returns:
            The attribute value or None if not found

        Raises:
            ValueError: If the instance is not found
        """
        instance = self.get_bom_instance_by_id(instance_id)
        if not instance:
            raise ValueError(f"BOM instance with ID {instance_id} not found")
        return instance.get_attribute(attribute_name)

    def set_instance_attribute(
        self,
        instance_id: str,
        attribute_name: str,
        value: str | int | float | bool | dict | list | None,
    ) -> None:
        """Set an attribute value on a BOM instance.

        Args:
            instance_id: ID of the BOM instance
            attribute_name: Name of the attribute to set
            value: Value to set for the attribute

        Raises:
            ValueError: If the instance is not found
        """
        instance = self.get_bom_instance_by_id(instance_id)
        if not instance:
            raise ValueError(f"BOM instance with ID {instance_id} not found")

        instance.set_attribute(attribute_name, value)

        # Call the update callback if provided

        available_attributes = instance.object_type.bom_attributes
        available_attributes.extend(
            [
                Attribute(id=attr.attribute_id, name=attr.name)
                for attr in instance.custom_attributes
                if attr.attribute_id is not None
            ]
        )

        if instance.object_type.parent is not None:
            available_attributes.extend(instance.object_type.parent.bom_attributes)

        if self.update_callback:
            attribute_id = next(
                (
                    attr.id
                    for attr in available_attributes
                    if attr.name.lower() == attribute_name.lower()
                ),
                None,
            )

            if not attribute_id:
                raise ValueError(f"Attribute '{attribute_name}' not found in object type")

            self.update_callback(
                UpdatePayload(
                    type=BomUpdates.ATTRIBUTE_UPDATE,
                    payload=AttributeUpdatePayload(
                        instance_id=instance.id, attribute_id=attribute_id, attribute_value=value
                    ),
                )
            )

    def update_bom_instance(self, instance_id: str, **kwargs: Unpack[BomInstanceUpdate]) -> None:
        """Update multiple attributes of a BOM instance.

        Args:
            instance_id: ID of the BOM instance
            **kwargs: Attribute name-value pairs to update

        Raises:
            ValueError: If the instance is not found
        """
        instance = self.get_bom_instance_by_id(instance_id)
        if not instance:
            raise ValueError(f"BOM instance with ID {instance_id} not found")

        """the back end will remove the parent_id if it is not provided
        so if the update is not requested, we need to assign it to the payload
        so that it remains unchanged."""

        # Update the instance attributes
        for attr_name, attr_value in kwargs.items():
            instance.set_property(attr_name, attr_value)  # type: ignore

        # Call the update callback if provided
        if self.update_callback:
            self.update_callback(
                UpdatePayload(
                    type=BomUpdates.INSTANCE_UPDATE,
                    payload=InstanceUpdatePayload(instance_id=instance.id, properties=kwargs),
                )
            )
