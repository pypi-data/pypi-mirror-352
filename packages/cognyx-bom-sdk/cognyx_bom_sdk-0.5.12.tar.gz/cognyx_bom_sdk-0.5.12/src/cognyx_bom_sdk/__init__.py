"""Cognyx BOM SDK package.

This library allows interaction with the Cognyx BOM API when writing BOM automations in Cognyx.
It provides a set of functions to manipulate BOM data in a Pyodide sandbox environment.
"""

__version__ = "0.1.0"

from cognyx_bom_sdk.client import BomClient
from cognyx_bom_sdk.cognyx.automation_runtime import execute_code
from cognyx_bom_sdk.cognyx.cognyx import CognyxClient
from cognyx_bom_sdk.models import (
    Attribute,
    AttributeUpdatePayload,
    Bom,
    BomInstance,
    BomInstanceSystemAttributes,
    BomInstanceSystemStatus,
    BomInstanceUpdate,
    BomReadinessStatus,
    BomUpdates,
    Diversity,
    InstanceUpdatePayload,
    Object,
    ObjectType,
    UpdatePayload,
    VariabilityConfiguration,
)

# Export main classes and functions for easier imports
__all__ = [
    "Attribute",
    "AttributeUpdatePayload",
    "Bom",
    "BomClient",
    "BomInstance",
    "BomInstanceSystemAttributes",
    "BomInstanceSystemStatus",
    "BomInstanceUpdate",
    "BomReadinessStatus",
    "BomUpdates",
    "CognyxClient",
    "Diversity",
    "InstanceUpdatePayload",
    "Object",
    "ObjectType",
    "UpdatePayload",
    "VariabilityConfiguration",
    "execute_code",
]
