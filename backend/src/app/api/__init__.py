# Import the implementation so it registers with BasePostsApi
from .posts_implementation import PostsImplementation

# This ensures the implementation is available when the module is imported
__all__ = ['PostsImplementation']