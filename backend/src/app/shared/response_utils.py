"""Response utilities for consistent API responses."""

from datetime import datetime, timezone
from typing import Optional, Union

# Constants
DRAFT_POST_PLACEHOLDER_DATE = datetime.fromtimestamp(0, tz=timezone.utc)


def parse_published_at(published_at_value: Optional[Union[str, datetime]]) -> datetime:
    """
    Parse and normalize publishedAt datetime values.
    
    Args:
        published_at_value: The value from post data, may be ISO string, datetime, or None (drafts)
        
    Returns:
        datetime: Normalized datetime object, uses epoch time for draft posts (None values)
    """
    if published_at_value is None:
        # Use epoch time as placeholder for draft posts
        return DRAFT_POST_PLACEHOLDER_DATE
    
    if isinstance(published_at_value, str):
        # If it's an ISO string, parse it
        return datetime.fromisoformat(published_at_value.replace('Z', '+00:00'))
    
    # If it's already a datetime, use it directly
    return published_at_value


def create_api_blog_post(post_data: dict, is_favorited: bool = False):
    """
    Create an ApiBlogPost object from post data with consistent datetime handling.
    
    Args:
        post_data: Dictionary containing post data from service layer
        is_favorited: Whether the post is favorited by current user
        
    Returns:
        ApiBlogPost: Properly formatted API response object
    """
    # Import here to avoid circular imports
    from generated_fastapi_server.models.blog_post import BlogPost as ApiBlogPost
    
    # Create base args
    args = {
        "id": post_data["id"],
        "title": post_data["title"],
        "content": post_data["content"],
        "excerpt": post_data["excerpt"],
        "author": post_data["author"],
        "publishedAt": parse_published_at(post_data.get("publishedAt")),
        "status": post_data["status"]
    }
    
    # Add isFavorited only if the field exists in the model
    try:
        # Check if the model has isFavorited field by creating a test instance
        test_args = args.copy()
        test_args["isFavorited"] = False
        ApiBlogPost(**test_args)
        args["isFavorited"] = is_favorited
    except TypeError:
        # Field doesn't exist, skip it
        pass
    
    return ApiBlogPost(**args)
