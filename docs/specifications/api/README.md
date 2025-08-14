# API Specifications

This directory contains the OpenAPI 3.0 specification for our application's backend API. It serves as the single source of truth for all API endpoints, data models, and request/response schemas.

By keeping our API specifications here, we ensure consistency, enable automated code generation, and provide a clear contract between the frontend and backend.


## Directory Structure

```
.
├── openapi.yml
├── paths/
│   ├── posts.yml
│   ├── posts@{id}.yml
│   └── posts@{id}@comments.yml
└── components/
    ├── parameters/
    │   ├── pagination.yml
    │   └── post-id.yml
    ├── responses/
    │   ├── bad-request.yml
    │   ├── unauthorized.yml
    │   └── not-found.yml
    ├── schemas/
    │   ├── error.yml
    │   ├── blog-post.yml
    │   ├── blog-post-summary.yml
    │   ├── blog-post-response.yml
    │   ├── blog-post-list-response.yml
    │   ├── comment.yml
    │   ├── comments-response.yml
    │   ├── create-post-request.yml
    │   └── create-comment-request.yml
    └── examples/
        ├── blog-post.yml
        ├── blog-post-summary.yml
        ├── blog-post-response.yml
        ├── blog-post-list-response.yml
        ├── comment.yml
        ├── comments-response.yml
        ├── create-post-request.yml
        ├── create-comment-request.yml
        ├── error-400.yml
        ├── error-401.yml
        └── error-404.yml
```

### `openapi.yml`
This is the main entry point for the API specification. It references all paths and components using `$ref` to maintain a clean, modular structure.

### `/paths`
Contains individual path definitions organized by endpoint. Path parameters use `@` notation (e.g., `posts@{id}.yml` represents `/posts/{id}`).

### `/components`
This directory contains all the reusable building blocks of the API specification.

- `/parameters`
  - Reusable parameters (e.g., pagination, IDs) that can be used across multiple endpoints.
- `/responses` 
  - Common HTTP response definitions (errors, success responses) for consistency across endpoints.
- `/schemas`
  - Data models and request/response schemas. Each schema is its own `.yml` file for maintainability.
- `/examples`
  - Concrete examples for all schemas, providing realistic sample data for documentation and testing.

## Rules and Best Practices

### Single Source of Truth
The `openapi.yml` file and its referenced components are the definitive contract for our API. Do not hardcode API paths or schemas in the application code without first defining them here.

### Modularity
All schemas should be defined in separate `.yml` files within the `/schemas` directory. This keeps the main `openapi.yml` file clean and focused on paths.

### Naming Conventions
 `PascalCase` for schema names (e.g., `UserDashboard`, `ProductItem`). Use `camelCase` for property names within schemas (e.g., `userName`, `renewalDate`).

### Documentation
All endpoints, parameters, and schemas must include a clear `description`. This is essential for both human understanding and for AI agents to generate correct code and documentation.

### Versioning
When making breaking changes to the API, update the `info.version` field in the `openapi.yml` file.

## Viewing API Documentation

You can view the interactive API documentation in your browser using **redoc-cli**. Since our OpenAPI specification uses modular files with `$ref` references, you need to bundle them first.

### Quick Start (Recommended)

```bash
# Navigate to the project root directory
cd /path/to/your/project

# Bundle all references into a single file and serve (one command)
npx @redocly/cli bundle docs/specifications/api/openapi.yml --output temp-openapi.yml && npx redoc-cli serve temp-openapi.yml
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
npx @redocly/cli lint docs/specifications/api/openapi.yml

# Step 2: Bundle the modular files into a single specification
npx @redocly/cli bundle docs/specifications/api/openapi.yml --output temp-openapi.yml

# Step 3: Serve the bundled specification
npx redoc-cli serve temp-openapi.yml

# Step 4: Clean up (optional)
rm temp-openapi.yml
```

### Local Installation (Project Scripts)

Add these scripts to your `package.json` for convenience:

```json
{
  "scripts": {
    "docs:lint": "npx @redocly/cli lint docs/specifications/api/openapi.yml",
    "docs:build": "npx @redocly/cli bundle docs/specifications/api/openapi.yml --output temp-openapi.yml",
    "docs:serve": "npm run docs:build && npx redoc-cli serve temp-openapi.yml",
    "docs:dev": "npm run docs:lint && npm run docs:serve",
    "docs:clean": "rm -f temp-openapi.yml"
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
   npx @redocly/cli bundle docs/specifications/api/openapi.yml --output temp-openapi.yml && npx redoc-cli serve temp-openapi.yml
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