"""Cognyx BOM SDK client."""

import asyncio

import httpx

from cognyx_bom_sdk.cognyx.helpers import format_bom, format_instance, get_parent_map
from cognyx_bom_sdk.cognyx.models import (
    BomEdge,
    BomInstanceResponse,
    BomNode,
    BomResponse,
    BomTree,
    BulkAttributesUpdateResponse,
    GlobalSettingsResponse,
    RootBomNode,
)
from cognyx_bom_sdk.models import Bom, BomInstance, BomInstanceUpdate, Originator


def headers(token: str, originator: Originator | None = None) -> dict[str, str]:
    """Generate headers for the Cognyx API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if originator is not None:
        originator_name = originator.get("name")
        originator_value = originator.get("value")
        if originator_name is not None:
            value: str = originator_value if originator_value is not None else originator_name
            name = f"CX-{originator_name.upper()}"
            headers[name] = value

    return headers


class CognyxClient:
    """Cognyx BOM SDK client."""

    def __init__(self, base_url: str, jwt_token: str) -> None:
        """Initialize the Cognyx client.

        Args:
            base_url: Base URL of the Cognyx API
            jwt_token: JWT token for authentication
        """
        self.base_url = base_url
        self.jwt_token = jwt_token

    async def get_bom(self, bom_id: str) -> BomResponse:
        """Get a BOM by ID.

        Args:
            bom_id: ID of the BOM to retrieve

        Returns:
            The BOM data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/boms/{bom_id}",
                headers=headers(self.jwt_token),
            )
            response.raise_for_status()

            json = response.json()
            bom_data = json["data"]
            print(bom_data)
            return BomResponse.model_validate(bom_data)

    async def get_default_view(self) -> str:
        """Get the default view for a BOM.

        Returns:
            The default view data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/settings/global",
                headers=headers(self.jwt_token),
            )
            response.raise_for_status()

            settings = GlobalSettingsResponse.model_validate(response.json())

            return settings.features["boms"]["default_view"]

    async def get_bom_tree(self, bom_id: str, view_id: str | None = None) -> BomTree:
        """Get a BOM as a tree.

        Args:
            bom_id: ID of the BOM
            view_id: ID of the view

        Returns:
            The BOM data as a tree
        """
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            view_id = await self.get_default_view() if view_id is None else view_id

            response = await client.get(
                f"{self.base_url}/api/v1/boms/{bom_id}/tree",
                headers=headers(self.jwt_token),
                params={
                    "view_id": view_id,
                    "includeInstances": True,
                },
            )
            response.raise_for_status()

            edges = [BomEdge.model_validate(edge) for edge in response.json()["edges"]]

            parents_map = get_parent_map(edges)

            tree = response.json()

            nodes: list[RootBomNode | BomNode] = []

            for node in tree["nodes"]:
                if node["group"] == "Bom":
                    nodes.append(RootBomNode.model_validate(node))
                else:
                    if (parent_id := parents_map.get(node["id"])) is not None:
                        node["system_attributes"]["instance"] = format_instance(
                            instance=BomInstanceResponse.model_validate(
                                node["system_attributes"]["instance"]
                            ),
                            bom_id=bom_id,
                            view_id=view_id,
                            parent_id=parent_id,
                        )
                    nodes.append(BomNode.model_validate(node))

            return BomTree(
                nodes=nodes,
                edges=edges,
            )

    async def get_instance(
        self, instance_id: str, bom_id: str, view_id: str, parent_id: str | None = None
    ) -> BomInstance:
        """Get a BOM instance by ID asynchronously.

        Args:
            instance_id: ID of the BOM instance to retrieve
            bom_id: ID of the BOM
            view_id: ID of the view
            parent_id: ID of the parent instance

        Returns:
            The BOM instance data
        """
        if parent_id is None:
            raise ValueError("Parent ID is required")
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/bom-instances/{instance_id}",
                headers=headers(self.jwt_token),
                params={"include": "entityType,entityType.bomAttributes"},
            )
            response.raise_for_status()
            json = response.json()

            return format_instance(
                instance=BomInstanceResponse.model_validate(json["data"]),
                bom_id=bom_id,
                view_id=view_id,
                parent_id=parent_id,
            )

    async def get_bom_instances(
        self,
        bom_id: str,
        nodes: list[BomNode],
        edges: list[BomEdge],
        view_id: str | None = None,
    ) -> list[BomInstance]:
        """Get all BOM instances for a BOM.

        Args:
            bom_id: ID of the BOM
            nodes: List of nodes in the BOM tree
            edges: List of edges in the BOM tree
            view_id: ID of the view

        Returns:
            List of BOM instance data
        """
        parent_map = get_parent_map(edges)
        view_id = await self.get_default_view() if view_id is None else view_id

        return await asyncio.gather(
            *[
                self.get_instance(node.id, bom_id, view_id, parent_map.get(node.id))
                for node in nodes
                if node.group != "Bom"
            ]
        )

    async def load_bom_data(self, bom_id: str, view_id: str | None = None) -> Bom:
        """Load BOM data.

        Args:
            bom_id: ID of the BOM
            view_id: ID of the view

        Returns:
            The formatted BOM data
        """
        bom, bom_tree = await asyncio.gather(
            self.get_bom(bom_id),
            self.get_bom_tree(bom_id, view_id),
        )
        instances = [
            node.system_attributes["instance"]
            for node in bom_tree.nodes
            if isinstance(node, BomNode)
        ]

        self.instances = instances

        return format_bom(bom, instances)

    async def update_instance(
        self,
        instance_id: str,
        properties: BomInstanceUpdate,
        originator: Originator | None = None,
    ) -> BomInstanceResponse:
        """Update a BOM instance.

        Args:
            instance_id: ID of the BOM instance to update
            properties: Properties to update
            originator: Originator of the update

        Raises:
            httpx.HTTPStatusError: If the update fails
        """
        async with httpx.AsyncClient() as client:
            payload = {}

            for key, value in properties.items():
                if key == "object_type_id":
                    payload["entity_type_id"] = value
                else:
                    payload[key] = value

            try:
                response = await client.patch(
                    f"{self.base_url}/api/v1/bom-instances/{instance_id}",
                    headers=headers(token=self.jwt_token, originator=originator),
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()["data"]

                return BomInstanceResponse.model_validate(data)

            except httpx.HTTPStatusError as e:
                raise e

    async def update_instance_attribute(
        self,
        instance_id: str,
        attribute_id: str,
        value: str | int | float | bool | dict | list | None,
        originator: Originator | None = None,
    ) -> BulkAttributesUpdateResponse:
        """Update an attribute of a BOM instance.

        Args:
            instance_id: ID of the BOM instance to update
            attribute_id: ID of the attribute to update
            value: Value to set for the attribute
            originator: Originator of the update

        Raises:
            httpx.HTTPStatusError: If the update fails
        """
        async with httpx.AsyncClient() as client:
            payload = {
                "bomInstanceIds": [instance_id],
                "attributes": [
                    {
                        "attribute_id": attribute_id,
                        "value": value,
                    }
                ],
            }

            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/bom-instances/attributes/bulk-update",
                    headers=headers(token=self.jwt_token, originator=originator),
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()["data"]

                return BulkAttributesUpdateResponse.model_validate(data[0])

            except httpx.HTTPStatusError as e:
                raise e
