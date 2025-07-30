# 2. SDK API

Date: 2025-03-31

## Status

Accepted

## Context

As we're adding an automation feature in Cognyx, we want users to write python code to automate some business logic on their BOMs. To achieve this, the Cognyx app provides a way to run python code running in a Pyodide sandbox. In order to facilitate the user's work, we want to populate the global scope of the sandbox with some functions which help the manipulation of the BOM. 

## Decision

We will create an SDK which will be imported by the Cognyx app and loaded in the Pyodide sandbox's context. When running the sandbox, we have the full BOM data in the shape of a json. This json will be passed to a class constructor function in the SDK. The class will then expose methods to easily access the BOM data:
- get_bom_instance(name: str) -> BomInstance
- get_bom_instance_by_id(id: str) -> BomInstance
- find_bom_instance(predicate: Callable[[BomInstance], bool]) -> Optional[BomInstance]
- list_bom_instances() -> List[BomInstance] 
- get_instance_attribute(instance_id: str, attribute_name: str) -> Any
- set_instance_attribute(instance_id: str, attribute_name: str, value: Any) -> None
- update_bom_instance(instance_id: str, **kwargs: InstanceUpdate) -> None

The class constructor should also accept a callable, which argument will be a list of updates to apply to the BOM. This callable will be passed to the pyodide sandbox, so that update requests can be processed by the sandbox runner.

## Consequences

What becomes easier or more difficult to do and any risks introduced by the change that will need to be mitigated.
