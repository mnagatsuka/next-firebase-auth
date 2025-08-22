#!/usr/bin/env python3
"""Seed DynamoDB Local with sample posts and comments for local development."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import boto3

from app.shared.config import get_settings


def main() -> None:
    settings = get_settings()

    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url=settings.AWS_ENDPOINT_URL,
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    posts = dynamodb.Table(settings.DYNAMODB_TABLE_POSTS)
    comments = dynamodb.Table(settings.DYNAMODB_TABLE_COMMENTS)

    now = datetime.now(timezone.utc).isoformat()

    # Create a published post
    post_id = str(uuid.uuid4())
    post_item = {
        "id": post_id,
        "title": "Hello DynamoDB Local",
        "content": "This is a sample post stored in DynamoDB Local.",
        "excerpt": "Sample post",
        "author": "seed-user",
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now,
    }
    posts.put_item(Item=post_item)
    print(f"Seeded post: {post_id}")

    # Create a draft post
    draft_id = str(uuid.uuid4())
    draft_item = {
        "id": draft_id,
        "title": "Draft Post",
        "content": "This is a draft and should not show up in published list.",
        "excerpt": "Draft excerpt",
        "author": "seed-user",
        "status": "draft",
        "published_at": None,
        "created_at": now,
        "updated_at": now,
    }
    posts.put_item(Item=draft_item)
    print(f"Seeded draft post: {draft_id}")

    # Create comments for the published post
    for i in range(3):
        comment_id = str(uuid.uuid4())
        comments.put_item(
            Item={
                "id": comment_id,
                "content": f"Nice article #{i+1}",
                "author": "seed-user",
                "post_id": post_id,
                "created_at": now,
            }
        )
        print(f"Seeded comment: {comment_id}")

    print("Seeding complete.")


if __name__ == "__main__":
    main()
