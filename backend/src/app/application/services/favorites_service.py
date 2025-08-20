"""Application service for user favorite posts."""

from typing import List, Optional

from app.application.exceptions import ApplicationError, NotFoundError
from app.domain.entities import BlogPost
from app.domain.services import PostRepository


class FavoriteApplicationService:
    """Coordinates favorites operations using a favorites repository and post repository."""

    def __init__(self, favorite_repository, post_repository: PostRepository):
        self.favorite_repository = favorite_repository
        self.post_repository = post_repository

    async def add_favorite(self, user_id: str, post_id: str) -> None:
        try:
            post = await self.post_repository.find_by_id(post_id)
            if not post:
                raise NotFoundError("Blog post not found")
            await self.favorite_repository.add_favorite(user_id, post_id)
        except NotFoundError:
            raise
        except Exception as e:
            raise ApplicationError(f"Failed to add favorite: {str(e)}")

    async def remove_favorite(self, user_id: str, post_id: str) -> None:
        try:
            await self.favorite_repository.remove_favorite(user_id, post_id)
        except Exception as e:
            raise ApplicationError(f"Failed to remove favorite: {str(e)}")

    async def get_user_favorites(self, user_id: str, page: int = 1, limit: int = 10) -> dict:
        try:
            page = max(1, page or 1)
            limit = max(1, min(50, limit or 10))
            ids: List[str] = await self.favorite_repository.list_favorites(user_id)
            # Stable order by most recently favorited is not tracked; keep by insertion order approximation
            # For now, reverse to show latest added near the end first
            ids_sorted = list(reversed(ids))
            start = (page - 1) * limit
            end = start + limit
            page_ids = ids_sorted[start:end]
            posts: List[BlogPost] = []
            for pid in page_ids:
                post = await self.post_repository.find_by_id(pid)
                if post:
                    posts.append(post)
            return {
                "data": posts,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(ids),
                },
            }
        except Exception as e:
            raise ApplicationError(f"Failed to get favorites: {str(e)}")

    async def is_favorited(self, user_id: str, post_id: str) -> bool:
        try:
            return await self.favorite_repository.is_favorited(user_id, post_id)
        except Exception:
            return False
