# Full-Stack Blog Application

A modern full-stack blog application with real-time comments, built with Next.js, FastAPI, and AWS serverless infrastructure.

## ✨ Features

- **🎨 Modern Frontend**: Next.js 15 + React + TypeScript + Tailwind CSS
- **⚡ Fast Backend**: FastAPI + Python 3.13 + DynamoDB
- **🔄 Real-time Features**: WebSocket API for live comments
- **🔐 Authentication**: Firebase Auth integration
- **☁️ Serverless Infrastructure**: AWS SAM + Lambda + API Gateway
- **🐳 Containerized Development**: Docker Compose for local setup
- **📚 Component Library**: Storybook for UI documentation
- **🧪 Comprehensive Testing**: Unit, Integration, and E2E tests

## 🚀 Quick Start

### Development (Docker)

```bash
# Clone repository
git clone <repository-url>
cd next-firebase-auth

# Start all services
docker compose up

# Access applications
# Frontend:    http://localhost:3000
# Backend:     http://localhost:8000/docs
# WebSocket:   ws://localhost:3001
# Storybook:   http://localhost:6006
```

### Development (Local)

```bash
# Start WebSocket service
cd infrastructure/serverless && pnpm install && pnpm run dev

# Start backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Start frontend
cd frontend && pnpm install && pnpm dev
```

## 📁 Project Structure

```
next-firebase-auth/
├── 📱 frontend/              # Next.js application
│   ├── src/components/       # React components
│   ├── src/app/             # App Router pages
│   ├── src/lib/             # Utilities and API
│   └── .storybook/          # Storybook configuration
├── 🔧 backend/              # FastAPI application  
│   ├── src/app/             # Application code
│   ├── src/app/api/         # API routes
│   ├── src/app/domain/      # Business logic
│   └── Dockerfile           # Container configuration
├── ☁️ infrastructure/        # AWS infrastructure
│   ├── aws-sam/             # Production deployment
│   │   ├── template.yml     # SAM template
│   │   ├── websocket-handlers/  # WebSocket Lambda functions
│   │   └── parameters/      # Environment configurations
│   └── serverless/          # WebSocket development
├── 🧪 tests/                # Test suites
│   ├── backend/             # Backend tests
│   ├── e2e/                 # End-to-end tests
│   └── frontend/            # Frontend tests (in progress)
└── 📚 docs/                 # Documentation
    ├── coding-guidelines/   # Development standards
    ├── specifications/      # Feature specifications
    └── DEVELOPMENT.md       # Development guide
```

## 🛠️ Architecture

### Development Environment
```
┌─────────────────────────────────────────────────────────────┐
│                    LOCAL DEVELOPMENT                        │
├─────────────────────────────────────────────────────────────┤
│ Next.js (3000) ←→ FastAPI (8000) ←→ WebSocket (3001)      │
│      ↓                   ↓                   ↓             │
│ React/TypeScript    Python/FastAPI    Node.js/Serverless   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│            ServerlessFramework DynamoDB (3001)              │
└─────────────────────────────────────────────────────────────┘
```

### Production Environment
```
┌─────────────────────────────────────────────────────────────┐
│                   CLIENT APPLICATIONS                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│          API Gateway v2 (HTTP + WebSocket)                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│    Lambda Functions (FastAPI + WebSocket Handlers)         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    DynamoDB Tables                         │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Development

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Node.js 20+** and **pnpm**
- **Python 3.13** and **uv**
- **AWS CLI** (for deployment)

### Environment Setup

```bash
# Backend configuration
cp backend/.env.example backend/.env.development

# Frontend configuration  
cp frontend/.env.example frontend/.env.development

# WebSocket configuration
cp infrastructure/serverless/.env.example infrastructure/serverless/.env.development
```

Optional: Additional Env Examples
- `infrastructure/aws-sam/.env.example`: convenience for parameter overrides; SAM reads values via flags, not `.env`.

### Common Commands

```bash
# Development
docker compose up -d                   # Start all services
docker compose up backend frontend  # Start specific services
docker compose logs -f backend      # View service logs

# Building
docker compose build                 # Rebuild all images
docker compose up --build backend   # Rebuild and start service

# Cleanup  
docker compose down                  # Stop services
docker compose down -v              # Stop and remove volumes
```

### Tail Logs

```bash
# Tail last 50 lines and follow for an individual service
docker compose logs -f --tail=50 localstack   # LocalStack (DynamoDB Local)
docker compose logs -f --tail=50 serverless   # Serverless
docker compose logs -f --tail=50 backend      # FastAPI backend
docker compose logs -f --tail=50 frontend     # Next.js frontend
docker compose logs -f --tail=50 storybook    # Storybook

# Tail multiple at once
docker compose logs -f --tail=50 serverless backend
docker compose logs -f --tail=50 serverless backend frontend

# Tail all primary services (press Ctrl+C to stop)
docker compose logs -f --tail=50 serverless backend frontend storybook

# Optional: handy Bash/Zsh function (paste into your shell profile)
tail-logs() {
  local lines="${TAIL_LINES:-50}"
  if [ "$#" -eq 0 ]; then
    set -- serverless backend frontend storybook
  fi
  docker compose logs -f --tail="$lines" "$@"
}

# Usage examples:
tail-logs backend
TAIL_LINES=500 tail-logs serverless backend
tail-logs    # tails serverless, backend, frontend, storybook
```

## 🚢 Deployment

### Production Deployment

```bash
# Deploy to AWS (requires AWS CLI setup)
cd infrastructure/aws-sam/
./build-websocket-handlers.sh
sam build
sam deploy --guided
```

### Environment Configuration

The application supports three environments with different configurations:

- **Development**: Local testing with relaxed settings
- **Staging**: Pre-production testing environment  
- **Production**: Live environment with optimized settings

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

## 📚 Documentation

- **[Deployment Guide](./DEPLOYMENT.md)**: Production deployment to AWS
- **[Infrastructure Architecture](./infrastructure/aws-sam/ARCHITECTURE.md)**: Technical details
- **[Coding Guidelines](./docs/coding-guidelines/)**: Development standards
- **[API Specifications](./docs/specifications/api/)**: API documentation

## 🧪 Testing

```bash
# Backend tests
cd backend && uv run pytest

# Frontend tests (Storybook)
cd frontend && pnpm storybook

# E2E tests
cd tests/e2e && pnpm test

# Infrastructure tests
cd infrastructure/serverless && pnpm test
```

## 🔍 Troubleshooting

### Common Issues

```bash
# Port conflicts
lsof -i :3000 :3001 :4566 :6006 :8000  # Check port usage
kill -9 $(lsof -t -i:3000)             # Kill process on port 3000

# Container issues
docker compose ps                       # Check service status
docker compose logs -f backend          # View service logs
docker compose restart backend         # Restart specific service

# Clean restart
docker compose down -v                 # Stop and remove volumes
docker compose up --build              # Rebuild and start
```

### Health Checks

```bash
# Verify services are running
curl http://localhost:8000/api/health     # Backend
wscat -c ws://localhost:3001              # WebSocket (install wscat first)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the [coding guidelines](./docs/coding-guidelines/)
4. Run tests: `pnpm test` and `uv run pytest`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🔗 Technology Stack

### Frontend
- **Framework**: Next.js 15 with App Router
- **UI**: React 18, TypeScript 5, Tailwind CSS
- **Components**: shadcn/ui, Storybook
- **State**: Zustand, TanStack Query
- **Auth**: Firebase Auth

### Backend  
- **Framework**: FastAPI with Python 3.13
- **Database**: DynamoDB
- **Runtime**: AWS Lambda with Web Adapter
- **Validation**: Pydantic, dependency injection

### Infrastructure
- **IaC**: AWS SAM (CloudFormation)
- **Compute**: AWS Lambda (Python + Node.js)
- **APIs**: API Gateway v2 (HTTP + WebSocket)  
- **Database**: DynamoDB with TTL
- **Monitoring**: CloudWatch Logs

### Development
- **Containerization**: Docker Compose
- **Package Managers**: pnpm (Node.js), uv (Python)
- **Testing**: Pytest, Vitest, Playwright
- **Code Quality**: Biome, Ruff, TypeScript strict mode
