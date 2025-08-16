#!/bin/bash
# OpenAPI Schema Validation Script
# Prevents duplication errors and ensures consistent structure

echo "🔍 Validating OpenAPI schema structure..."

# Check for duplicate schema names in bundled output
echo "📦 Bundling OpenAPI spec..."
pnpm oas:bundle > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Bundling failed! Check your OpenAPI structure."
    exit 1
fi

echo "✅ Bundling successful"

# Extract schema names from bundled file
BUNDLED_FILE="../../../openapi/dist/openapi.yml"
if [ ! -f "$BUNDLED_FILE" ]; then
    echo "❌ Bundled file not found at $BUNDLED_FILE"
    exit 1
fi

# Check for duplicate schema names in the bundled output
echo "🔍 Checking for duplicate schema names..."
SCHEMA_NAMES=$(grep -A 1000 "components:" "$BUNDLED_FILE" | grep -A 1000 "schemas:" | grep "^  [a-zA-Z]" | grep -v "^  schemas:" | cut -d':' -f1 | sed 's/^  //' | sort)

DUPLICATES=$(echo "$SCHEMA_NAMES" | uniq -d)
if [ ! -z "$DUPLICATES" ]; then
    echo "❌ Duplicate schema names found:"
    echo "$DUPLICATES"
    exit 1
fi

echo "✅ No duplicate schema names found"

# Check for inline schemas (basic check)
echo "🔍 Checking for potential inline schemas..."
INLINE_SCHEMAS=$(find components/schemas -name "*.yml" -exec grep -l "type: object" {} \; | xargs grep -l "properties:" | xargs grep -c "type: object" | grep -v ":1$")

if [ ! -z "$INLINE_SCHEMAS" ]; then
    echo "⚠️  Potential inline schemas detected (files with multiple 'type: object'):"
    echo "$INLINE_SCHEMAS"
    echo "   Review these files to ensure proper separation"
fi

# Test Orval generation
echo "🔍 Testing Orval generation..."
pnpm orval:gen > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Orval generation failed! Check the bundled OpenAPI spec for issues."
    exit 1
fi

echo "✅ Orval generation successful"
echo "🎉 All validation checks passed!"