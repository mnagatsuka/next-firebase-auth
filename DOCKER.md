# Docker Development Setup

This document explains how to run the frontend and backend services using Docker containers.

## Prerequisites

- Docker and Docker Compose installed
- No local services running on ports 3000, 6006, or 8000

## Quick Start

### Start All Services

```bash
# Build and start both frontend and backend
docker compose up --build

# Or run in detached mode
docker compose up --build -d
```

### Access the Services

- **Frontend (Next.js)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Storybook**: http://localhost:6006

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```

## Individual Service Commands

### Backend Only

```bash
# Start backend service
docker compose up backend

# View backend logs
docker compose logs -f backend
```

### Frontend Only

```bash
# Start frontend service (requires backend to be running)
docker compose up frontend

# View frontend logs
docker compose logs -f frontend
```

## Development Workflow

1. **Code Changes**: Both frontend and backend code are mounted as volumes, so changes will be reflected automatically
2. **Package Updates**: If you add new dependencies, rebuild the containers:
   ```bash
   docker compose down
   docker compose up --build
   ```
3. **Database/Storage**: The backend uses in-memory storage, so data resets on container restart

## Configuration

### Environment Variables

The services are configured with the following environment variables:

**Backend**:
- `APP_ENVIRONMENT=development`
- `APP_DEBUG=true`
- `ALLOWED_ORIGINS=http://localhost:3000,http://frontend:3000`

**Frontend**:
- `NODE_ENV=development`
- `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
- `CHOKIDAR_USEPOLLING=true` (for file watching in containers)

### API Communication

- Frontend communicates with backend via `http://localhost:8000`
- Services are connected via Docker network `app-network`
- CORS is configured to allow requests from the frontend

## Troubleshooting

### Port Conflicts
If you get port binding errors, check that ports 3000, 6006, and 8000 are not in use:
```bash
lsof -i :3000
lsof -i :6006
lsof -i :8000
```

### File Watching Issues
If hot reload isn't working:
- The containers use polling for file watching on macOS/Windows
- Make sure `CHOKIDAR_USEPOLLING=true` is set in docker compose.yml

### Container Issues
```bash
# View all container logs
docker compose logs

# Restart specific service
docker compose restart frontend

# Rebuild specific service
docker compose up --build backend
```