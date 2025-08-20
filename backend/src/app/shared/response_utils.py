"""Utilities for API response handling and data transformation."""

from datetime import datetime
from typing import Optional


def normalize_published_at(published_at: Optional[str]) -> str:
    """
    Normalize publishedAt field for API responses.
    
    Args:
        published_at: The publishedAt value from post data (can be None)
        
    Returns:
        ISO format datetime string. Uses epoch timestamp for None values.
    """
    if published_at is None:
        return datetime.fromtimestamp(0).isoformat()
    return published_at