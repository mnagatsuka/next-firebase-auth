"""Repositories for user favorite posts (in-memory and DynamoDB)."""

from typing import Dict, List, Set

import boto3
from boto3.resources.base import ServiceResource
from botocore.exceptions import ClientError


class InMemoryFavoriteRepository:
    """Simple in-memory favorite store mapping user_id -> set(post_id)."""

    def __init__(self) -> None:
        self._data: Dict[str, Set[str]] = {}

    async def add_favorite(self, user_id: str, post_id: str) -> None:
        self._data.setdefault(user_id, set()).add(post_id)

    async def remove_favorite(self, user_id: str, post_id: str) -> None:
        if user_id in self._data:
            self._data[user_id].discard(post_id)

    async def list_favorites(self, user_id: str) -> List[str]:
        return list(self._data.get(user_id, set()))

    async def is_favorited(self, user_id: str, post_id: str) -> bool:
        return post_id in self._data.get(user_id, set())


class DynamoDBFavoriteRepository:
    """DynamoDB implementation for favorites.

    Table schema (recommended):
    - Partition key: user_id (string)
    - Sort key: post_id (string)
    """

    def __init__(
        self,
        table_name: str,
        *,
        endpoint_url: str,
        region_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
    ) -> None:
        self._table_name = table_name
        self._dynamodb: ServiceResource = boto3.resource(
            "dynamodb",
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self._table = self._dynamodb.Table(table_name)

    async def add_favorite(self, user_id: str, post_id: str) -> None:
        try:
            self._table.put_item(Item={"user_id": user_id, "post_id": post_id})
        except ClientError as e:
            raise Exception(f"Failed to add favorite: {e}")

    async def remove_favorite(self, user_id: str, post_id: str) -> None:
        try:
            self._table.delete_item(Key={"user_id": user_id, "post_id": post_id})
        except ClientError as e:
            raise Exception(f"Failed to remove favorite: {e}")

    async def list_favorites(self, user_id: str) -> List[str]:
        from boto3.dynamodb.conditions import Key

        try:
            resp = self._table.query(KeyConditionExpression=Key("user_id").eq(user_id))
        except ClientError:
            return []
        items = resp.get("Items", [])
        return [i.get("post_id") for i in items if i.get("post_id")]

    async def is_favorited(self, user_id: str, post_id: str) -> bool:
        try:
            resp = self._table.get_item(Key={"user_id": user_id, "post_id": post_id})
        except ClientError:
            return False
        return "Item" in resp
