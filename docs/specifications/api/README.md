# API Specifications

This directory contains the OpenAPI 3.0 specification for our application's backend API. It serves as the single source of truth for all API endpoints, data models, and request/response schemas.

By keeping our API specifications here, we ensure consistency, enable automated code generation, and provide a clear contract between the frontend and backend.


## Directory Structure

```
.
├── openapi.yaml
├── paths/
│   ├── posts.yaml
│   ├── posts@{id}.yaml
│   └── posts@{id}@comments.yaml
└── components/
    ├── parameters/
    │   ├── pagination.yaml
    │   └── post-id.yaml
    ├── responses/
    │   ├── bad-request.yaml
    │   ├── unauthorized.yaml
    │   └── not-found.yaml
    ├── schemas/
    │   ├── error.yaml
    │   ├── blog-post.yaml
    │   ├── blog-post-summary.yaml
    │   ├── blog-post-response.yaml
    │   ├── blog-post-list-response.yaml
    │   ├── comment.yaml
    │   ├── comments-response.yaml
    │   ├── create-post-request.yaml
    │   └── create-comment-request.yaml
    └── examples/
        ├── blog-post.yaml
        ├── blog-post-summary.yaml
        ├── blog-post-response.yaml
        ├── blog-post-list-response.yaml
        ├── comment.yaml
        ├── comments-response.yaml
        ├── create-post-request.yaml
        ├── create-comment-request.yaml
        ├── error-400.yaml
        ├── error-401.yaml
        └── error-404.yaml
```

### `openapi.yaml`
This is the main entry point for the API specification. It references all paths and components using `$ref` to maintain a clean, modular structure.

### `/paths`
Contains individual path definitions organized by endpoint. Path parameters use `@` notation (e.g., `posts@{id}.yaml` represents `/posts/{id}`).

### `/components`
This directory contains all the reusable building blocks of the API specification.

- `/parameters`
  - Reusable parameters (e.g., pagination, IDs) that can be used across multiple endpoints.
- `/responses` 
  - Common HTTP response definitions (errors, success responses) for consistency across endpoints.
- `/schemas`
  - Data models and request/response schemas. Each schema is its own `.yaml` file for maintainability.
- `/examples`
  - Concrete examples for all schemas, providing realistic sample data for documentation and testing.

## Rules and Best Practices

### Single Source of Truth
The `openapi.yaml` file and its referenced components are the definitive contract for our API. Do not hardcode API paths or schemas in the application code without first defining them here.

### Modularity
All schemas should be defined in separate `.yaml` files within the `/schemas` directory. This keeps the main `openapi.yaml` file clean and focused on paths.

### Naming Conventions
 `PascalCase` for schema names (e.g., `UserDashboard`, `ProductItem`). Use `camelCase` for property names within schemas (e.g., `userName`, `renewalDate`).

### Documentation
All endpoints, parameters, and schemas must include a clear `description`. This is essential for both human understanding and for AI agents to generate correct code and documentation.

### Versioning
When making breaking changes to the API, update the `info.version` field in the `openapi.yaml` file.