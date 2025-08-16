from __future__ import annotations

from fastapi import Depends

from app.application.use_cases.get_posts import GetPosts
from app.application.use_cases.get_post import GetPost
from app.application.use_cases.create_post import CreatePost
from app.application.use_cases.update_post import UpdatePost
from app.application.use_cases.comments import CreateComment, GetPostComments
from app.domain.ports import PostRepository
from app.infra.repositories.memory_post_repository import MemoryPostRepository


def get_post_repository() -> PostRepository:
    # For now, provide an in-memory repo. Swap to real infra in production.
    return MemoryPostRepository()


def get_posts_use_case(repo: PostRepository = Depends(get_post_repository)) -> GetPosts:
    return GetPosts(repo)


def get_post_use_case(repo: PostRepository = Depends(get_post_repository)) -> GetPost:
    return GetPost(repo)


def create_post_use_case(repo: PostRepository = Depends(get_post_repository)) -> CreatePost:
    return CreatePost(repo)


def update_post_use_case(repo: PostRepository = Depends(get_post_repository)) -> UpdatePost:
    return UpdatePost(repo)


def get_post_comments_use_case(
    repo: PostRepository = Depends(get_post_repository),
) -> GetPostComments:
    return GetPostComments(repo)


def create_comment_use_case(
    repo: PostRepository = Depends(get_post_repository),
) -> CreateComment:
    return CreateComment(repo)
