# API Specifications

This directory contains the OpenAPI 3.0 specification for our application's backend API. It serves as the single source of truth for all API endpoints, data models, and request/response schemas.

By keeping our API specifications here, we ensure consistency, enable automated code generation, and provide a clear contract between the frontend and backend.


## Directory Structure

```
.
├── openapi/spec/openapi.yml
├── openapi/openapi-schema-guideline.md
├── openapi/spec/paths/
│   ├── posts.yml
│   ├── posts@{id}.yml
│   ├── posts@{id}@comments.yml
│   ├── posts@{id}@favorite.yml
│   ├── users@{uid}@posts.yml
│   └── users@{uid}@favorites.yml
└── openapi/spec/components/
    ├── parameters/
    │   ├── pagination.yml
    │   ├── post-id.yml
    │   └── user-id.yml
    ├── responses/
    │   ├── bad-request.yml
    │   ├── unauthorized.yml
    │   └── not-found.yml
    ├── schemas/
    │   ├── api-response-status.yml
    │   ├── blog-post.yml
    │   ├── blog-post-list-data.yml
    │   ├── blog-post-list-response.yml
    │   ├── blog-post-response.yml
    │   ├── blog-post-summary.yml
    │   ├── comment.yml
    │   ├── comments-response.yml
    │   ├── create-comment-request.yml
    │   ├── create-post-request.yml
    │   ├── error.yml
    │   ├── error-detail.yml
    │   └── pagination.yml
    └── examples/
        ├── blog-post.yml
        ├── blog-post-list-response.yml
        ├── blog-post-response.yml
        ├── blog-post-summary.yml
        ├── comment.yml
        ├── comments-response.yml
        ├── create-comment-request.yml
        ├── create-post-request.yml
        ├── error-400.yml
        ├── error-401.yml
        └── error-404.yml
```

### `openapi/spec/openapi.yml`
This is the main entry point for the API specification. It references all paths and components using `$ref` to maintain a clean, modular structure. The API integrates with Firebase Authentication and supports blog post management with commenting functionality. Anonymous users are supported via Firebase anonymous auth for favoriting posts; creating posts requires a non-anonymous (normal) login.

### `openapi-schema-guideline.md`
Contains detailed guidelines for maintaining consistent schema structure and naming conventions across the API specification. **Read this before modifying any schema files** - it covers essential patterns to prevent duplication errors and ensure clean code generation.


### `/paths`
Contains individual path definitions organized by endpoint. Path parameters use `@` notation (e.g., `posts@{id}.yml` represents `/posts/{id}`).

### `/components`
This directory contains all the reusable building blocks of the API specification.

- `/parameters`
  - Reusable parameters (e.g., pagination, IDs) that can be used across multiple endpoints.
- `/responses` 
  - Common HTTP response definitions (errors, success responses) for consistency across endpoints.
- `/schemas`
  - Data models and request/response schemas. Each schema is its own `.yml` file for maintainability. Includes core entities (BlogPost, Comment), request/response wrappers, error models, and utility schemas like Pagination and ApiResponseStatus.
- `/examples`
  - Concrete examples for all schemas, providing realistic sample data for documentation and testing.

## Rules and Best Practices

### Single Source of Truth
The `openapi/spec/openapi.yml` file and its referenced components are the definitive contract for our API. Do not hardcode API paths or schemas in the application code without first defining them here.

### Modularity
All schemas should be defined in separate `.yml` files within the `/schemas` directory. This keeps the main `openapi/spec/openapi.yml` file clean and focused on paths.

### Naming Conventions
 `PascalCase` for schema names (e.g., `UserDashboard`, `ProductItem`). Use `camelCase` for property names within schemas (e.g., `userName`, `renewalDate`).

### Documentation
All endpoints, parameters, and schemas must include a clear `description`. This is essential for both human understanding and for AI agents to generate correct code and documentation.

### Versioning
When making breaking changes to the API, update the `info.version` field in the `openapi/spec/openapi.yml` file.

### Schema Development
When creating or modifying schemas, follow these essential rules (see `openapi-schema-guideline.md` for details):

- **One schema per file** - Each `.yml` file should define exactly one reusable schema
- **No inline schemas** - Extract reusable components to separate files and use `$ref`
- **Consistent naming** - Use kebab-case for filenames, PascalCase for schema references
- **Always specify required fields** - Include a `required` array for all schemas
- **Run validation** - Use `npx @redocly/cli lint` before committing changes

## Viewing API Documentation

You can view the interactive API documentation in your browser using **redoc-cli**. Since our OpenAPI specification uses modular files with `$ref` references, you need to bundle them first.

### Quick Start (Recommended)

```bash
# Navigate to the project root directory
cd /path/to/your/project

# Bundle all references into a single file and serve (one command)
npx @redocly/cli bundle openapi/spec/openapi.yml --output temp-openapi.yml && npx redoc-cli serve temp-openapi.yml
```


This will:
- Validate and bundle all `$ref` files into a single OpenAPI specification
- Download tools temporarily (first time only)
- Start a local server at http://localhost:8080
- Automatically open the documentation in your browser

### Step-by-Step Approach

If you prefer to run commands separately:

```bash
# Step 1: Validate the OpenAPI specification
npx @redocly/cli lint openapi/spec/openapi.yml

# Step 2: Bundle the modular files into a single specification
npx @redocly/cli bundle openapi/spec/openapi.yml --output temp-openapi.yml

# Step 3: Serve the bundled specification
npx redoc-cli serve temp-openapi.yml

# Step 4: Clean up (optional)
rm temp-openapi.yml
```

### Backend Implementation

The FastAPI backend implementation follows this OpenAPI specification:

- **Generated Models**: Located in `backend/src/app/generated/` - auto-generated from this OpenAPI spec
- **Route Implementation**: `backend/src/app/api/routes/posts.py` implements the blog post endpoints
- **Testing**: Comprehensive test suite in `tests/backend/` covering unit, integration, and e2e tests

To run the backend:

```bash
# From project root with activated .venv
cd backend
uv run --active uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test endpoints
curl http://localhost:8000/health
curl "http://localhost:8000/posts?page=1&limit=10"
```

### Local Installation (Project Scripts)

Add these scripts to your `package.json` for convenience:

```json
{
  "scripts": {
    "oas:lint": "pnpm exec redocly lint openapi/spec/openapi.yml",
    "oas:bundle": "mkdir -p openapi/dist && pnpm exec redocly bundle openapi/spec/openapi.yml --remove-unused-components -o openapi/dist/openapi.yml",
    "oas:docs:project": "redocly preview --product=redoc --project-dir=./ --port=8081",
    "oas:docs:api": "pnpm oas:bundle && pnpm exec redocly build-docs openapi/dist/openapi.yml -o openapi/dist/index.html && open openapi/dist/index.html",
  }
}
```

For projects using `pnpm`, you can also add:

```json
{
  "scripts": {
    "oas:bundle": "@redocly/cli bundle openapi/spec/openapi.yml --output temp-openapi.yml",
    "orval:gen": "orval --config orval.config.ts"
  }
}
```

Then run:
```bash
# Validate, bundle, and serve the documentation
npm run docs:dev

# Or just serve (skip validation)
npm run docs:serve

# Clean up bundled file when done
npm run docs:clean
```

### What You'll See

The ReDoc interface provides:
- **Clean, professional documentation** with a responsive design
- **Interactive endpoint explorer** showing all API paths and methods  
- **Detailed schema definitions** with examples and validation rules
- **Request/response examples** for each endpoint
- **Searchable documentation** to quickly find specific endpoints or schemas

### Development Workflow

1. **Edit** the OpenAPI specification files in this directory
2. **Validate and bundle** the docs with the quick start command:
   ```bash
   npx @redocly/cli bundle openapi/spec/openapi.yml --output temp-openapi.yml && npx redoc-cli serve temp-openapi.yml
   ```
3. **Refresh** your browser to see changes (you'll need to re-run the bundle command after changes)
4. **Share** the documentation URL with team members for review
5. **Clean up** the temporary file when done: `rm temp-openapi.yml`

### Why Use Redocly CLI?

We use **@redocly/cli** instead of other bundling tools because:
- ✅ **Actively maintained** (2024) with modern OpenAPI 3.1 support
- ✅ **Built by the ReDoc team** - optimized for ReDoc documentation
- ✅ **Built-in validation** - catches specification errors during bundling
- ✅ **Better performance** - faster bundling than legacy tools
- ✅ **Superior error messages** - clearer debugging information

### Why Bundling is Required

Our OpenAPI specification is organized in modular files using `$ref` to reference:
- **Paths** in the `/paths` directory  
- **Schemas** in the `/components/schemas` directory
- **Parameters** in the `/components/parameters` directory
- **Examples** in the `/components/examples` directory

The bundling process resolves all these references into a single file that documentation tools can properly display.