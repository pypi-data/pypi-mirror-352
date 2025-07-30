from collections.abc import Awaitable, Callable
from contextlib import AsyncExitStack
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, cast

import aioboto3
from boto3.dynamodb.conditions import Key
from types_aiobotocore_dynamodb import DynamoDBServiceResource
from types_aiobotocore_dynamodb.service_resource import Table as DynamoTable

from sifts.common_types.snippets import ItemAnalysisResult, Snippet
from sifts.io.db.base import AnalysisDB


class DynamoVulnDB(AnalysisDB):
    def __init__(self, table_name: str = "llm_scan") -> None:
        self.table_name = table_name

    async def get_vulnerability(self, pk: str, sk: str) -> ItemAnalysisResult | None:
        result = await get_item_from_dynamo(self.table_name, pk=pk, sk=sk)
        if result is None:
            return None
        return cast(ItemAnalysisResult, result)

    async def insert_vulnerability(self, vuln: ItemAnalysisResult) -> bool:
        return await insert_item_into_dynamo(self.table_name, dict(vuln))

    async def insert_snippet(self, snippet: Snippet) -> bool:
        return await insert_item_into_dynamo(self.table_name, snippet._asdict())

    async def aget_snippet(self, root_id: str, path: str, hash_: str) -> Snippet | None:
        pk = f"ROOT#{root_id}#PATH#{path}"
        sk = f"SNIPPET#{hash_}"
        item = await get_item_from_dynamo(self.table_name, pk, sk)
        if item is not None:
            return Snippet(**item)
        return None

    async def get_vulnerabilities_by_snippet(
        self,
        root_nickname: str,
        path: str,
        snippet_hash: str,
    ) -> list[ItemAnalysisResult]:
        pk = f"ROOT#{root_nickname}#PATH#{path}"
        snippet_prefix = f"SNIPPET#{snippet_hash}"
        table = await get_table_resource(self.table_name)
        response = await table.query(
            KeyConditionExpression=Key("pk").eq(pk) & Key("sk").begins_with(snippet_prefix),
        )
        items = response.get("Items", [])
        return [ItemAnalysisResult(**item) for item in items]  # type: ignore [typeddict-item]

    async def get_vulnerabilities_vulnerable(self) -> list[ItemAnalysisResult]:
        msg = "Method get_vulnerabilities_vulnerable not implemented"
        raise NotImplementedError(msg)


SESSION = aioboto3.Session()
StartupCallable = Callable[[], Awaitable[None]]
ShutdownCallable = Callable[[], Awaitable[None]]
GetResourceCallable = Callable[[], Awaitable[DynamoDBServiceResource]]
DynamoContext = tuple[StartupCallable, ShutdownCallable, GetResourceCallable]


TABLE_RESOURCES: dict[str, DynamoTable] = {}


def create_dynamo_context() -> DynamoContext:
    context_stack = None
    resource = None

    async def _startup() -> None:
        nonlocal context_stack, resource

        context_stack = AsyncExitStack()
        resource = await context_stack.enter_async_context(
            SESSION.resource(
                service_name="dynamodb",
                use_ssl=True,
                verify=True,
            ),
        )
        if context_stack:
            await context_stack.aclose()

    async def _shutdown() -> None:
        if context_stack:
            await context_stack.aclose()

    async def _get_resource() -> DynamoDBServiceResource:
        if resource is None:
            await dynamo_startup()

        return cast(DynamoDBServiceResource, resource)

    return _startup, _shutdown, _get_resource


async def get_item_from_dynamo(table_name: str, pk: str, sk: str) -> dict[str, Any] | None:
    table = await get_table_resource(table_name)
    response = await table.get_item(Key={"pk": pk, "sk": sk})
    item: dict[str, Any] | None = response.get("Item")
    if item is not None:
        return item
    return None


dynamo_startup, dynamo_shutdown, get_resource = create_dynamo_context()


async def get_table_resource(table: str) -> DynamoTable:
    if table in TABLE_RESOURCES:
        return TABLE_RESOURCES[table]

    resource = await get_resource()
    return await resource.Table(table)


async def insert_item_into_dynamo(table_name: str, item: dict[str, Any]) -> bool:
    table = await get_table_resource(table_name)
    serialized_item = {k: serialize(v) for k, v in item.items()}
    await table.put_item(Item=serialized_item)
    return True


def serialize(object_: object) -> Any:  # noqa: ANN401
    if isinstance(object_, set):
        return [serialize(o) for o in object_]
    if isinstance(object_, datetime):
        return object_.astimezone(tz=UTC).isoformat()
    if isinstance(object_, float):
        return Decimal(str(object_))
    if isinstance(object_, Enum):
        return object_.value

    return object_
