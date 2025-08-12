# Repository Guidelines

## Project Structure & Module Organization

- Root: `README.md` (overview) and `CLAUDE.md` (assistant notes).
- Docs live under `docs/`:
  - `docs/coding-guidelines/frontend/NN_topic.md` — numbered sections (e.g., `01_introduction.md`, `05_fetching-caching.md`).
  - `docs/specifications/` — product/feature specifications (e.g., `frontend/README.md`).
- Add new pages in the appropriate folder, keep the numeric ordering, and update the nearest `README.md` index when adding or renaming files.

## Build, Test, and Development Commands

- No build step — content is plain Markdown rendered by GitHub.
- Preview locally using your editor’s Markdown preview (e.g., VS Code: “Open Preview to the Side”).
- Optional linting (if available locally): `npx markdownlint-cli2 "**/*.md"` to check style and common issues.

## Coding Style & Naming Conventions

- Headings: one `#` title per file; use Title Case for headings; keep sections short and scannable.
- Filenames: `NN_<kebab-case-topic>.md` (number + underscore + kebab-case), matching existing patterns.
- Tone: professional, instructional, and concise. Prefer short paragraphs and bulleted lists.
- Code: use fenced blocks with language hints (e.g., ```ts, ```bash). Wrap identifiers and paths in backticks.
- Links: prefer relative links within the repo; use descriptive link text and valid anchors.

## Validation Guidelines

- Links resolve: follow each added/changed link from the GitHub UI.
- Examples compile conceptually: shell snippets run without missing steps; Next.js examples align with the guidance (Next 15, TS 5, App Router, RSC).
- Consistency: follow `pnpm` in commands and libraries named in the guidelines (Zustand, TanStack Query, Zod, Tailwind, etc.).

## Commit & Pull Request Guidelines

- Commits: prefer Conventional Commits (e.g., `docs: add navigation rules`, `docs: fix typos`). Keep them focused and descriptive.
- PRs must include: brief summary, why the change is needed, affected pages/sections, and any links to related specs. Include before/after examples for modified conventions when helpful.
- Checklist before opening: passes Markdown preview, optional `markdownlint` clean, no broken anchors, indices updated where applicable.

## Agent-Specific Tips

- Preserve numbering and anchors; do not reorder existing sections without justification.
- Mirror the established tone and terminology; prefer `pnpm` in commands.
- Do not introduce tools or stacks not already referenced in this repository without prior discussion.

