# Cognyx Automation SDK

This repo contains a Cognyx' python BOM SDK. This library allows you to interact with the Cognyx BOM API when writing BOM automations in Cognyx.

## Setup

### Prerequisites

- Python 3.11.11
- `uv` package manager

### Installation

Install `uv` if you don't have it already:

```bash
pip install uv
```

Install the package:

```bash
uv install .
```

For development, install with development dependencies:

```bash
uv install -e ".[dev]"
```

## Tooling

This project uses `uv` for tooling. Dependencies are declared in pyproject.toml.

Run the following commands for development tasks:

```bash
# Run tests
uv run test
uv run coverage

# Run linting
uv run lint

# Run formatting
uv run format_code

# Run type checking
uv run typecheck
```

## Architecture

The repo uses ADR (Architecture Decision Record). These can be found in the doc folder. The ADRs explain the philosophy of the project, and how it is supposed to be used.

The main usage of this SDK is to expose functions helping Cognyx users to write BOM automations. These run in a pyodide sandbox.
The package exposes one main API to interact with a given Cognyx BOM, which data is passed when initializing the main Bom class. This class then provides a list of methods which are loaded as globals in the pyodide sandbox.

## API Documentation

### BomClient

The `BomClient` class is the main entry point for interacting with the Cognyx BOM API.

#### Initialization

When using the SDK in Cognyx automations, the initialization is already taken care of and is not needed.
You will directly get an instance of the BomClient to interact with the selected bom.
This section is provided for integration in other python projects.

```python
from cognyx_bom_sdk.client import BomClient

# Initialize with BOM data

def process_update(update: dict) -> None:
    # ... implement update handling

client = BomClient(bom_data, update_callback=process_update)
```

- `bom_data`: The complete BOM data as a dictionary
- `update_callback`: Callback function that will be called with updates to apply to the BOM

#### Methods

##### `get_bom_instance(name: str) -> BomInstance | None`

Get a BOM instance by name.

```python
instance = client.get_bom_instance("instance_name")
```

##### `get_bom_instance_by_id(instance_id: str) -> BomInstance | None`

Get a BOM instance by ID.

```python
instance = client.get_bom_instance_by_id("instance_id")
```

##### `find_bom_instance(predicate: Callable[[BomInstance], bool]) -> BomInstance | None`

Find a BOM instance using a predicate function.

```python
# Find an instance with a specific attribute value
instance = client.find_bom_instance(lambda i: i.name == "instance_name")
```

##### `list_bom_instances() -> list[BomInstance]`

List all BOM instances.

```python
instances = client.list_bom_instances()
```

##### `get_instance_attribute(instance_id: str, attribute_name: str) -> str | int | float | bool | dict | list | None`

Get an attribute value from a BOM instance.

```python
value = client.get_instance_attribute("instance_id", "attribute_name")
```

##### `set_instance_attribute(instance_id: str, attribute_name: str, value: str | int | float | bool | dict | list | None) -> None`

Set an attribute value on a BOM instance.

```python
client.set_instance_attribute("instance_id", "attribute_name", "new_value")
```

##### `update_bom_instance(instance_id: str, **kwargs) -> None`

Update multiple attributes of a BOM instance.

```python
client.update_bom_instance("instance_id", status="active", priority=1)
```

### Models

The SDK provides a set of Pydantic models that represent the data structures used in the Cognyx BOM system.

#### Enums

##### `BomUpdates`

Enum for different types of BOM updates.

```python
from cognyx_bom_sdk.models import BomUpdates

# Available values
BomUpdates.INSTANCE_UPDATE  # "instance_update"
BomUpdates.ATTRIBUTE_UPDATE  # "attribute_update"
```

##### `BomReadinessStatus`

Enum for different types of BOM readiness statuses.

```python
from cognyx_bom_sdk.models import BomReadinessStatus

# Available values
BomReadinessStatus.NOT_STARTED  # "not_started"
BomReadinessStatus.IN_PROGRESS  # "in_progress"
BomReadinessStatus.DONE  # "done"
```

##### `BomInstanceSystemStatus`

Enum for different types of BOM instance system statuses.

```python
from cognyx_bom_sdk.models import BomInstanceSystemStatus

# Available values
BomInstanceSystemStatus.IS_OPTIONAL  # "is_optional"
BomInstanceSystemStatus.HAS_VARIANTS  # "has_variants"
BomInstanceSystemStatus.HAS_WARNING_NO_VARIABILITY  # "has_warning_no_variability"
BomInstanceSystemStatus.IS_STANDARD  # "is_standard"
```

#### Core Models

##### `Attribute`

Represents an attribute in the Cognyx system.

```python
from cognyx_bom_sdk.models import Attribute

attribute = Attribute(
    id="attr_id",
    name="attr_name",
    description="attr_description",
    value="attr_value"
)
```

Key fields:
- `id`: Unique identifier for the attribute
- `name`: Name of the attribute
- `description`: Description of the attribute
- `value`: Value of the attribute (can be any type)
- `options`: Available options for the attribute (if applicable)

##### `ObjectType`

Represents an object type in the Cognyx system.

```python
from cognyx_bom_sdk.models import ObjectType

object_type = ObjectType(
    id="type_id",
    name="type_name",
    description="type_description",
    slug="type_slug",
    base_unit="unit",
    display_name="display_name",
    bom_attributes=[...],  # List of Attribute objects
    catalog_attributes=[...],  # List of Attribute objects
)
```

Key methods:
- `get_attribute_id(attribute_name: str) -> str | None`: Get an attribute ID by name

##### `BomInstance`

Represents a BOM instance in the Cognyx system.

```python
from cognyx_bom_sdk.models import BomInstance

instance = BomInstance(
    id="instance_id",
    name="instance_name",
    description="instance_description",
    bom_id="bom_id",
    view_id="view_id",
    parent_id="parent_id",
    reference="reference",
    status="status",
    object_type=object_type,  # ObjectType instance
    object_type_id="object_type_id",
    quantity=1,
    custom_attributes=[...],  # List of Attribute objects
    variability_configurations=[...],  # List of VariabilityConfiguration objects
)
```

Key methods:
- `get_attribute(attribute_name: str) -> Any`: Get an attribute value by name
- `set_attribute(attribute_name: str, value: Any) -> None`: Set an attribute value
- `set_property(property_name: str, value: str | int) -> None`: Set a property value
- `is_optional() -> bool`: Check if the instance is optional
- `has_variants() -> bool`: Check if the instance has variants
- `is_standard() -> bool`: Check if the instance is standard
- `has_warning_no_variability() -> bool`: Check if the instance has a warning due to no variability

##### `Bom`

Represents a complete BOM with all its instances.

```python
from cognyx_bom_sdk.models import Bom

bom = Bom(
    id="bom_id",
    name="bom_name",
    reference="reference",
    description="description",
    status="status",
    instances=[...],  # List of BomInstance objects
)
```

Key methods:
- `get_instance(name: str) -> BomInstance | None`: Get a BOM instance by name
- `get_instance_by_id(instance_id: str) -> BomInstance | None`: Get a BOM instance by ID

##### `VariabilityConfiguration`

Represents a configuration for a BOM instance.

```python
from cognyx_bom_sdk.models import VariabilityConfiguration

config = VariabilityConfiguration(
    id="config_id",
    variability_id="variability_id",
    variability=diversity,  # Diversity instance
    object_id="object_id",
    object=object,  # Object instance
)
```

#### Update Models

##### `BomInstanceUpdate`

TypedDict for BomInstance update properties.

```python
from cognyx_bom_sdk.models import BomInstanceUpdate

update: BomInstanceUpdate = {
    "name": "new_name",
    "description": "new_description",
    "quantity": 2,
}
```

##### `UpdatePayload`

TypedDict for update payload with discriminated union pattern.

```python
from cognyx_bom_sdk.models import UpdatePayload, BomUpdates, AttributeUpdatePayload

update_payload: UpdatePayload = {
    "type": BomUpdates.ATTRIBUTE_UPDATE,
    "payload": {
        "instance_id": "instance_id",
        "attribute_id": "attribute_id",
        "attribute_value": "new_value",
    },
}
```

## Project Guidelines

- Always write semantic, modern and performant Python code, with type hints and inline documentation
- Always define Models when relevant instead of relying on abstract List & dictionaries. These should be exposed by the library to help the consumers of the SDK
- All code should be correctly formatted and linted using ruff. Functions should be tested
- Try to use as little dependencies as possible to keep it lightweight and safe to integrate in the pyodide sandbox
- When writing tests on existing code, avoid changing the existing code to pass your test. Instead, modify the test so that it passes

## CI/CD

This project uses GitHub Actions for CI/CD. It automatically tests, lints, and publishes the package.
