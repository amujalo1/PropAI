# PropAI - Real Estate Management Platform MVP

A modern cloud-based SaaS platform for real estate agencies, investors, and buyers. This MVP demonstrates architecture and provides a working skeleton with basic CRUD operations, dummy endpoints, and clean project structure.

## Overview

PropAI is built with:
- **Backend**: FastAPI (Python 3.12)
- **Frontend**: React 19 + TypeScript + Vite
- **Database**: PostgreSQL
- **Cache**: Redis (optional)
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.12+ (for local development)
- Node.js 18+ (for local frontend development)

### Running with Docker (Recommended)

```bash
# Start all services
docker compose up

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:5173
# API docs at http://localhost:8000/docs
```

The application will automatically:
- Initialize the PostgreSQL database
- Create all required tables
- Start the FastAPI backend
- Start the Vite frontend dev server

### First Time Usage

1. Open http://localhost:5173 in your browser
2. Click "Register" to create a new account
3. Use the dashboard to manage properties and incidents

## Project Structure

```
propai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── db.py                   # Database connection
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── property.py
│   │   │   ├── incident.py
│   │   │   └── ci.py
│   │   ├── routes/                 # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── properties.py
│   │   │   ├── incidents.py
│   │   │   ├── ci.py
│   │   │   └── ai.py
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── utils/                  # Utilities
│   │   └── config/                 # Configuration
│   ├── tests/                       # Unit tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── pages/                  # Page components
│   │   ├── components/             # Reusable components
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── services/               # API client
│   │   ├── types/                  # TypeScript types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── __tests__/                  # Component tests
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── .env.local
├── docker-compose.yml
├── .env.example
├── README.md
└── DEPLOYMENT.md
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/logout` - Logout (mock)

### Properties
- `POST /properties` - Create property
- `GET /properties` - List properties with pagination and filtering
- `GET /properties/{id}` - Get property by ID
- `PUT /properties/{id}` - Update property
- `DELETE /properties/{id}` - Delete property

### Incidents
- `POST /incidents` - Create incident
- `GET /incidents` - List incidents with pagination and filtering
- `GET /incidents/{id}` - Get incident by ID

### CMDB
- `POST /ci` - Create CI
- `GET /ci/{ci_id}` - Get CI details
- `GET /ci/hierarchy/{ci_id}` - Get full hierarchy
- `GET /ci/level/{level}` - Get CIs by hierarchy level

### AI
- `POST /ai/valuation` - Get property valuation (mock)

## Features

### Authentication
- User registration with email validation
- Password hashing with bcrypt
- JWT-based authentication
- Role-based user types (admin, data_steward, ci_owner, agent)

### Property Management
- Create, read, update, delete properties
- Property lifecycle status tracking
- Pagination and filtering
- Property types: residential, commercial, land

### Incident Management
- Create and track incidents
- Priority levels: P1, P2, P3, P4
- Incident status tracking
- Property-incident relationships

### CMDB Hierarchy
- Five-level hierarchy: Location → Complex → Building → Property → Component
- Automatic CI ID generation (PROP-[TYPE]-[REGION]-[SEQUENCE])
- Hierarchy path retrieval

### AI Valuation
- Mock AI endpoint for property valuations
- Returns estimated value in EUR
- Placeholder for future ML integration

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm run test:run
```

## Local Development Setup

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp ../.env.example .env

# Start server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp ../.env.example .env.local

# Start dev server
npm run dev
```

## Environment Variables

See `.env.example` for all available configuration options.

### Backend Configuration
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Secret key for JWT tokens
- `JWT_ALGORITHM` - Algorithm for JWT (default: HS256)
- `JWT_EXPIRATION_HOURS` - Token expiration time
- `REDIS_URL` - Redis connection string

### Frontend Configuration
- `VITE_API_URL` - Backend API URL
- `VITE_APP_NAME` - Application name

## Development

### Adding Dependencies

**Backend**:
```bash
cd backend
pip install <package>
pip freeze > requirements.txt
```

**Frontend**:
```bash
cd frontend
npm install <package>
```

## Troubleshooting

### Docker Issues

```bash
# Clean up containers and volumes
docker compose down -v

# Rebuild images
docker compose build --no-cache

# Start fresh
docker compose up
```

### Database Connection Issues

- Ensure PostgreSQL container is running: `docker compose ps`
- Check database URL in `.env`
- Verify network connectivity between containers

### Frontend Build Issues

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend Errors

```bash
# View logs
docker compose logs backend

# Restart backend
docker compose restart backend
```

## MVP Scope

This is a skeleton implementation focusing on:
- ✅ Architecture demonstration
- ✅ Working API endpoints
- ✅ Basic CRUD operations
- ✅ UI layout and structure
- ✅ Docker setup
- ✅ Authentication system
- ✅ Database models
- ❌ Production-ready features
- ❌ Complex business logic
- ❌ Real AI/ML implementation
- ❌ Advanced security features
- ❌ Performance optimization

## Next Steps (Sprint 2+)

- Implement real AI valuation model
- Add user role-based access control enforcement
- Implement CMDB hierarchy workflows
- Add incident SLA tracking
- Set up CI/CD pipeline
- Configure monitoring and alerting
- Add comprehensive error handling
- Implement caching strategies
- Add API rate limiting
- Set up logging infrastructure

## Documentation

- See `DEPLOYMENT.md` for deployment instructions
- See `.kiro/specs/propai-mvp/` for detailed specifications
- API documentation available at http://localhost:8000/docs

## License

Proprietary - PropAI
