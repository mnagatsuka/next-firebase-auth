"""Repositories for user favorite posts (in-memory and DynamoDB)."""

from typing import Dict, List, Set, Optional

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
        endpoint_url: Optional[str] = None,
        region_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ) -> None:
        self._table_name = table_name
        kwargs = {"region_name": region_name}
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        if aws_access_key_id:
            kwargs["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key:
            kwargs["aws_secret_access_key"] = aws_secret_access_key
        self._dynamodb: ServiceResource = boto3.resource("dynamodb", **kwargs)
        self._table = self._dynamodb.Table(table_name)
        print(f"DynamoDB FavoritesRepository initialized with table: {table_name}, region: {region_name}, endpoint: {endpoint_url}")
        # Verify table exists
        try:
            table_status = self._table.table_status
            print(f"Table {table_name} status: {table_status}")
        except Exception as e:
            print(f"Error checking table status: {e}")

    async def add_favorite(self, user_id: str, post_id: str) -> None:
        try:
            # Synchronous boto3 operation - should complete before returning
            response = self._table.put_item(Item={"user_id": user_id, "post_id": post_id})
            # Add logging to verify the operation
            print(f"DynamoDB put_item response: {response}")
        except ClientError as e:
            print(f"DynamoDB put_item error: {e}")
            raise Exception(f"Failed to add favorite: {e}")
        except Exception as e:
            print(f"Unexpected error in add_favorite: {e}")
            raise

    async def remove_favorite(self, user_id: str, post_id: str) -> None:
        try:
            response = self._table.delete_item(Key={"user_id": user_id, "post_id": post_id})
            print(f"DynamoDB delete_item response: {response}")
        except ClientError as e:
            print(f"DynamoDB delete_item error: {e}")
            raise Exception(f"Failed to remove favorite: {e}")
        except Exception as e:
            print(f"Unexpected error in remove_favorite: {e}")
            raise

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
