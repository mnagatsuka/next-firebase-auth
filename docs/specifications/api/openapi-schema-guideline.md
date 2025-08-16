# OpenAPI Schema Guidelines

This document outlines best practices for maintaining the OpenAPI specification to prevent duplication errors and ensure clean code generation.

Our OpenAPI specification generates **FastAPI/Pydantic models** in `backend/src/app/generated/` and is designed to work with **Firebase Authentication** and **Orval** for frontend TypeScript types.

## 🎯 Core Principles

### 1. **One Schema Per File**
- Each `.yml` file in `components/schemas/` should define exactly one reusable schema
- Use kebab-case naming for file names (e.g., `blog-post-summary.yml`)
- Use PascalCase for schema references in `openapi/openapi.yml` (e.g., `BlogPostSummary`)
- Generated Python models use snake_case for field names (e.g., `published_at` from `publishedAt`)

### 2. **No Inline Schemas**
- ❌ **Don't** define schemas inline within other schemas
- ✅ **Do** extract reusable components to separate files and use `$ref`

```yaml
# ❌ Bad: Inline schema
properties:
  pagination:
    type: object
    properties:
      page:
        type: integer

# ✅ Good: Reference to external schema
properties:
  pagination:
    $ref: "./pagination.yml"
```

### 3. **Consistent Reference Patterns**
- **Within openapi.yml**: Use relative paths to schema files: `$ref: "./components/schemas/filename.yml"`
- **Within external files**: Use relative paths back to openapi.yml: `$ref: "../../openapi.yml#/components/schemas/SchemaName"`
- **Component references**: Always use `#/components/schemas/PascalCaseName` format for internal references
- Use descriptive names that match the schema purpose
- Group related schemas logically in the main `openapi/openapi.yml`

## 📁 File Organization

```
components/
  schemas/
    # Core data models
    blog-post.yml                # Full blog post entity
    blog-post-summary.yml        # Lightweight version for lists
    comment.yml                  # Comment entity
    
    # Request/Response wrappers
    blog-post-response.yml       # Wraps BlogPost with status
    blog-post-list-response.yml  # Wraps blog post list with pagination
    blog-post-list-data.yml      # Contains array of summaries + pagination
    comments-response.yml        # Wraps comment array with status
    
    # Common reusable components
    api-response-status.yml      # Enum: [success, error]
    pagination.yml               # Page metadata (page, limit, total, hasNext)
    error-detail.yml             # Error details structure
    error.yml                    # Error response wrapper
    
    # Request models
    create-post-request.yml      # Blog post creation payload
    create-comment-request.yml   # Comment creation payload
```

## 🔍 Required Fields Guidelines

### Always Specify Required Fields
```yaml
type: object
properties:
  id:
    type: string
    description: Unique identifier
    example: "post-123"
  name:
    type: string
    description: Display name
    example: "My Blog Post"
required:  # ✅ Always include this
  - id
  - name
```

### Include Descriptions and Examples
Every field must have:
- **description**: Clear explanation of the field's purpose
- **example**: Realistic sample value
- **format**: For dates, use `format: date-time`
- **enum**: For restricted values (e.g., `[draft, published]`)

### Common Patterns
- **Core entities**: Include all essential identifying fields (id, title, author, etc.)
- **Request models**: Include only fields that must be provided (no auto-generated fields like id, publishedAt)
- **Response models**: Include fields that are always returned
- **Wrapper patterns**: Use consistent response structure with `status` + `data` or `status` + `error`
- **camelCase in JSON**: Use camelCase for property names (e.g., `publishedAt`, `hasNext`)
- **Enum validation**: Always specify allowed values for status fields

## 🚫 Anti-Patterns to Avoid

### 1. **Duplicate Schema Names**
```yaml
# ❌ Don't have both of these:
schemas:
  BlogPost:
    $ref: './blog-post.yml'
  blog-post:  # This creates a duplicate!
    type: object
    properties: ...
```

### 2. **Mixing Naming Conventions**
```yaml
# ❌ Inconsistent naming
schemas:
  BlogPost:      # PascalCase
    $ref: './blog-post.yml'
  comment_data:  # snake_case - don't mix!
    $ref: './comment-data.yml'
```

### 3. **Overly Nested Inline Definitions**
```yaml
# ❌ Too much nesting
properties:
  data:
    type: object
    properties:
      posts:
        type: array
        items:
          type: object  # Extract this!
          properties:
            id:
              type: string

# ✅ Good: Use references
properties:
  data:
    $ref: "./blog-post-list-data.yml"
```

### 4. **Inconsistent Response Patterns**
```yaml
# ❌ Don't mix response structures
successResponse:
  properties:
    data:
      $ref: "./blog-post.yml"

errorResponse:
  properties:
    message:  # Inconsistent with success pattern
      type: string

# ✅ Good: Consistent structure
both_responses:
  properties:
    status:
      $ref: "./api-response-status.yml"  # Always include status
    data:  # or error field
      $ref: "./blog-post.yml"
```

## 🔧 Validation Workflow

### Before Committing Changes:

1. **Validate and bundle the OpenAPI specification:**
   ```bash
   # Validate the OpenAPI structure
   pnpm oas:lint
   
   # Bundle with unused component removal (prevents duplication)
   pnpm oas:bundle
   
   # Generate frontend types to test Orval integration
   pnpm oas:fe
   
   # View the documentation to verify
   pnpm oas:docs:api
   ```

2. **Test with your backend implementation:**
   ```bash
   # Run backend tests to ensure generated models work
   cd backend
   uv run --active pytest ../tests/backend -q
   
   # Start the backend to test API endpoints
   uv run --active uvicorn app.main:app --reload --port 8000
   ```

3. **Quick validation check:**
   ```bash
   # One-liner to validate, bundle, and generate types
   pnpm oas:lint && pnpm oas:bundle && pnpm oas:fe
   ```

### Validation Workflow

Manual validation ensures:
- ✅ **OpenAPI validity**: `pnpm oas:lint` validates structure and references using Redocly
- ✅ **Bundling success**: All `$ref` references resolve correctly with `--remove-unused-components`
- ✅ **No schema duplication**: Bundled spec has unique PascalCase schema keys only
- ✅ **Frontend compatibility**: Orval generates clean TypeScript types without errors
- ✅ **MSW integration**: Mock data uses example values (no faker dependency)
- ✅ **Documentation quality**: ReDoc can render the specification properly
- ✅ **Backend compatibility**: Generated FastAPI models work with your implementation

**Generated outputs to verify:**
- **Frontend types**: `frontend/src/lib/api/generated/schemas/` (PascalCase TypeScript interfaces)
- **MSW mocks**: `frontend/src/lib/api/generated/client.msw.ts` (using OpenAPI examples)
- **React Query hooks**: `frontend/src/lib/api/generated/client.ts` (typed API functions)
- **Bundled spec**: `openapi/dist/openapi.yml` (resolved references, no duplicates)
- **FastAPI models**: `backend/src/app/generated/src/generated_fastapi_server/models/`
- **API documentation**: ReDoc-compatible bundled specification

## 📝 Schema Evolution

### Adding New Schemas
1. **Create the schema file** in `components/schemas/` using kebab-case naming
2. **Add reference** in main `openapi/openapi.yml` under appropriate section (use PascalCase)
3. **Create examples** in `components/examples/` with same base name
4. **Validate the changes** using redocly commands
5. **Test backend integration** to verify Pydantic model creation

**Example workflow:**
```bash
# 1. Create schema with proper structure
cat > components/schemas/new-entity.yml << 'EOF'
type: object
properties:
  id:
    type: string
    description: Unique identifier
    example: "entity-123"
  name:
    type: string
    description: Display name
    example: "My Entity"
required:
  - id
  - name
EOF

# 2. Add to openapi/openapi.yml schemas section
# NewEntity:
#   $ref: './components/schemas/new-entity.yml'

# 3. Create example
cat > components/examples/new-entity.yml << 'EOF'
value:
  id: "entity-123"
  name: "Example Entity"
EOF

# 4. Validate
pnpm oas:lint
```

### Modifying Existing Schemas
1. Never change existing field names (breaking change)
2. Add new optional fields as needed
3. Mark new required fields carefully
4. Update related examples and documentation

### Removing Schemas
1. Check all references before removal
2. Ensure no external consumers depend on it
3. Remove from main `openapi/openapi.yml` references
4. Archive or delete the file

## 🎉 Success Criteria

A well-maintained schema structure should:
- ✅ Bundle without errors using `pnpm oas:bundle` (with `--remove-unused-components`)
- ✅ Generate clean Pydantic models in `backend/src/app/generated/`
- ✅ Generate clean TypeScript types via Orval in `frontend/src/lib/api/generated/`
- ✅ Generate MSW mocks using OpenAPI examples (no faker dependency)
- ✅ Have no duplicate schema names across all components
- ✅ Use consistent naming patterns (kebab-case files, PascalCase references, camelCase properties)
- ✅ Have proper required field specifications with descriptions and examples
- ✅ Follow consistent response wrapper patterns (`status` + `data`/`error`)
- ✅ Pass validation with `pnpm oas:lint`
- ✅ Use proper reference patterns (relative paths from external files to openapi.yml)
- ✅ Be compatible with Firebase Authentication integration
- ✅ Be easy to understand and maintain for the development team

## 🚨 Common Issues and Solutions

### Schema Duplication Errors
**Problem**: Orval reports "Duplicate schema names detected"
**Solution**: Follow the [schema-fix.md](./schema-fix.md) playbook:
1. Ensure PascalCase schema keys in `openapi.yml` 
2. Use proper relative references from external files
3. Bundle with `--remove-unused-components` flag
4. Verify no duplicate schema definitions exist

### Faker Dependency in MSW Mocks
**Problem**: Generated MSW file imports `@faker-js/faker`
**Solution**: Configure Orval properly:
```typescript
// orval.config.ts
mock: {
  type: "msw",
  useExamples: true,
  generateEachHttpStatus: false, // Prevents faker usage for error responses
}
```

### Reference Resolution Errors
**Problem**: Bundling fails with "Can't resolve $ref"
**Solution**: Check reference patterns:
- From `openapi.yml`: `$ref: "./components/schemas/filename.yml"`
- From external files: `$ref: "../../openapi.yml#/components/schemas/SchemaName"`
