import { defineConfig } from "orval";

export default defineConfig({
  api: {
    input: {
      // Use bundled OpenAPI (preserving components) for multi-file $ref support
      target: "openapi/dist/openapi.yml",
    },
    output: {
      target: "frontend/src/lib/api/generated/client.ts",
      schemas: "frontend/src/lib/api/generated/schemas",
      client: "react-query",
      httpClient: "fetch",
      mode: "split",
      clean: true,
      mock: {
        type: "msw",
        delay: false,
        useExamples: true,
        generateEachHttpStatus: false,
      },
      override: {
        query: {
          useQuery: true,
          useMutation: true,
        },
        mutator: {
          path: "frontend/src/lib/api/customFetch.ts",
          name: "customFetch",
        },
        fetch: {
          includeHttpResponseReturnType: false,
        },
        mock: {
          required: true,
        },
      },
    },
    // Hooks disabled in CI/sandbox to avoid networked formatter
    // hooks: {
    //   afterAllFilesWrite: "cd frontend && npx @biomejs/biome format --write src/lib/api/generated/",
    // },
  },
});
