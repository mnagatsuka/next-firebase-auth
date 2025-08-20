# next-firebase-auth
- Next.js
- Firebase Auth

```
.
├── frontend/
├── backend/
├── infrastructure/
├── tests/
│   └── e2e/
└── docs/
    └── development-workflow/ 
    └── projects/
    └── specifications/
    └── coding-guidelines/
```

## Run Storybook (Docker Compose)
- Start: `docker compose -f docker-compose.storybook.yml up storybook`
- Open: `http://localhost:6006`
- With backend: run `docker compose up backend` separately, or combine with `docker compose -f docker-compose.yml -f docker-compose.storybook.yml up storybook`
- Notes: Reuses `frontend/Dockerfile`, runs in `/app/frontend`, no `depends_on` so mocks or separate backend are supported.
