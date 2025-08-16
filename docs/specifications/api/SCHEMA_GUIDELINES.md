# OpenAPI Schema Guidelines

This document outlines best practices for maintaining the OpenAPI specification to prevent duplication errors and ensure clean code generation.

## 🎯 Core Principles

### 1. **One Schema Per File**
- Each `.yml` file in `components/schemas/` should define exactly one reusable schema
- Use kebab-case naming for file names (e.g., `blog-post-summary.yml`)
- Use PascalCase for schema references in `openapi.yml` (e.g., `BlogPostSummary`)

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
- Always use relative paths: `$ref: "./filename.yml"`
- Use descriptive names that match the schema purpose
- Group related schemas logically in the main `openapi.yml`

## 📁 File Organization

```
components/
  schemas/
    # Core data models
    blog-post.yml
    blog-post-summary.yml
    comment.yml
    
    # Request/Response wrappers
    blog-post-response.yml
    blog-post-list-response.yml
    comments-response.yml
    
    # Common reusable components
    api-response-status.yml
    pagination.yml
    error-detail.yml
    error.yml
    
    # Request models
    create-post-request.yml
    create-comment-request.yml
```

## 🔍 Required Fields Guidelines

### Always Specify Required Fields
```yaml
type: object
properties:
  id:
    type: string
  name:
    type: string
required:  # ✅ Always include this
  - id
  - name
```

### Common Patterns
- **Core entities**: Include all essential identifying fields
- **Request models**: Include only fields that must be provided
- **Response models**: Include fields that are always returned

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
```

## 🔧 Validation Workflow

### Before Committing Changes:

1. **Run the validation script:**
   ```bash
   cd docs/specifications/api
   ./validate-schema.sh
   ```

2. **Check bundling:**
   ```bash
   pnpm oas:bundle
   ```

3. **Test code generation:**
   ```bash
   pnpm orval:gen
   ```

### Automated Checks

The validation script checks for:
- ✅ Successful OpenAPI bundling
- ✅ No duplicate schema names
- ✅ Successful Orval generation
- ⚠️  Potential inline schema issues

## 📝 Schema Evolution

### Adding New Schemas
1. Create the schema file in `components/schemas/`
2. Add reference in main `openapi.yml` under appropriate section
3. Run validation script
4. Update examples if needed

### Modifying Existing Schemas
1. Never change existing field names (breaking change)
2. Add new optional fields as needed
3. Mark new required fields carefully
4. Update related examples and documentation

### Removing Schemas
1. Check all references before removal
2. Ensure no external consumers depend on it
3. Remove from main `openapi.yml` references
4. Archive or delete the file

## 🎉 Success Criteria

A well-maintained schema structure should:
- ✅ Bundle without errors
- ✅ Generate clean TypeScript types via Orval
- ✅ Have no duplicate schema names
- ✅ Use consistent naming patterns
- ✅ Have proper required field specifications
- ✅ Be easy to understand and maintain