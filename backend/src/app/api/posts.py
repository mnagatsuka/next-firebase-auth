from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.models import (
    BlogPost,
    BlogPostListData,
    BlogPostListResponse,
    BlogPostResponse,
    BlogPostSummary,
    Comment,
    CommentsResponse,
    CreateCommentRequest,
    CreatePostRequest,
    PaginationInfo,
)
from app.api.dependencies import (
    create_comment_use_case,
    create_post_use_case,
    get_post_comments_use_case,
    get_post_use_case,
    get_posts_use_case,
    update_post_use_case,
)
from app.application.use_cases.get_posts import GetPosts
from app.application.use_cases.get_post import GetPost
from app.application.use_cases.create_post import CreatePost
from app.application.use_cases.update_post import UpdatePost
from app.application.use_cases.comments import CreateComment, GetPostComments


router = APIRouter()


@router.get("/posts", response_model=BlogPostListResponse, tags=["posts"])
async def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    use_case: GetPosts = Depends(get_posts_use_case),
) -> BlogPostListResponse:
    """Get paginated blog posts — matches OpenAPI contract."""

    result = await use_case.execute(page=page, limit=limit)

    posts = [
        BlogPostSummary(
            id=p.id,
            title=p.title,
            excerpt=p.excerpt,
            author=p.author,
            publishedAt=p.published_at,
        )
        for p in result.posts
    ]

    pagination = PaginationInfo(
        page=page,
        limit=limit,
        total=result.total,
        hasNext=page * limit < result.total,
    )

    return BlogPostListResponse(status="success", data=BlogPostListData(posts=posts, pagination=pagination))


@router.get("/posts/{post_id}", response_model=BlogPostResponse, tags=["posts"])
async def get_post(
    post_id: str,
    use_case: GetPost = Depends(get_post_use_case),
) -> BlogPostResponse:
    post = await use_case.execute(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    api_post = BlogPost(
        id=post.id,
        title=post.title,
        content=post.content,
        excerpt=post.excerpt,
        author=post.author,
        publishedAt=post.published_at,
        status=post.status,  # type: ignore[assignment]
    )
    return BlogPostResponse(status="success", data=api_post)


@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=BlogPostResponse, tags=["posts"])
async def create_post(
    body: CreatePostRequest,
    use_case: CreatePost = Depends(create_post_use_case),
) -> BlogPostResponse:
    post = await use_case.execute(
        title=body.title,
        content=body.content,
        excerpt=body.excerpt,
        status=body.status,
        author="System",  # placeholder; wire auth later
    )
    api_post = BlogPost(
        id=post.id,
        title=post.title,
        content=post.content,
        excerpt=post.excerpt,
        author=post.author,
        publishedAt=post.published_at,
        status=post.status,  # type: ignore[assignment]
    )
    return BlogPostResponse(status="success", data=api_post)


@router.put("/posts/{post_id}", response_model=BlogPostResponse, tags=["posts"])
async def update_post(
    post_id: str,
    body: CreatePostRequest,
    use_case: UpdatePost = Depends(update_post_use_case),
) -> BlogPostResponse:
    updated = await use_case.execute(
        post_id,
        title=body.title,
        content=body.content,
        excerpt=body.excerpt,
        status=body.status,
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    api_post = BlogPost(
        id=updated.id,
        title=updated.title,
        content=updated.content,
        excerpt=updated.excerpt,
        author=updated.author,
        publishedAt=updated.published_at,
        status=updated.status,  # type: ignore[assignment]
    )
    return BlogPostResponse(status="success", data=api_post)


@router.get("/posts/{post_id}/comments", response_model=CommentsResponse, tags=["comments"])
async def get_comments(
    post_id: str,
    use_case: GetPostComments = Depends(get_post_comments_use_case),
) -> CommentsResponse:
    result = await use_case.execute(post_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    comments = [
        Comment(
            id=c.id,
            content=c.content,
            author=c.author,
            createdAt=c.created_at,
            postId=c.post_id,
        )
        for c in result
    ]
    return CommentsResponse(status="success", data=comments)


@router.post(
    "/posts/{post_id}/comments",
    status_code=status.HTTP_201_CREATED,
    response_model=BlogPostResponse,
    tags=["comments"],
)
async def create_comment(
    post_id: str,
    body: CreateCommentRequest,
    use_case: CreateComment = Depends(create_comment_use_case),
) -> BlogPostResponse:
    post = await use_case.execute(post_id, content=body.content, author=body.author)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    api_post = BlogPost(
        id=post.id,
        title=post.title,
        content=post.content,
        excerpt=post.excerpt,
        author=post.author,
        publishedAt=post.published_at,
        status=post.status,  # type: ignore[assignment]
    )
    return BlogPostResponse(status="success", data=api_post)
