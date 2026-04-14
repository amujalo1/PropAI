# PropAI MVP - Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Port 8000 (backend) and 5173 (frontend) available

### Running the Application

```bash
# Clone or navigate to the project directory
cd propai

# Start all services
docker compose up

# The application will be available at:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
```

### First Time Setup

1. Wait for all containers to be healthy (check with `docker compose ps`)
2. Navigate to http://localhost:5173
3. Register a new account or use test credentials
4. Start exploring the application

### Stopping the Application

```bash
# Stop all services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

## Local Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp ../.env.example .env

# Run tests
pytest

# Start development server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp ../.env.example .env.local

# Start development server
npm run dev

# Run tests
npm run test:run
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://propai:propai@postgres:5432/propai
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
REDIS_URL=redis://redis:6379
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=PropAI
```

## Database

### Accessing PostgreSQL

```bash
# Connect to PostgreSQL container
docker exec -it propai-postgres psql -U propai -d propai

# Common commands
\dt                    # List tables
\d table_name         # Describe table
SELECT * FROM users;  # Query data
```

### Database Migrations

The database schema is automatically created on backend startup. To reset:

```bash
docker compose down -v
docker compose up
```

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

**Authentication**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/logout` - Logout

**Properties**
- `POST /properties` - Create property
- `GET /properties` - List properties
- `GET /properties/{id}` - Get property details
- `PUT /properties/{id}` - Update property
- `DELETE /properties/{id}` - Delete property

**Incidents**
- `POST /incidents` - Create incident
- `GET /incidents` - List incidents
- `GET /incidents/{id}` - Get incident details

**AI**
- `POST /ai/valuation` - Get property valuation (mock)

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Find process using port 5173
lsof -i :5173

# Kill process
kill -9 <PID>
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker compose ps

# View logs
docker compose logs postgres

# Restart database
docker compose restart postgres
```

### Frontend Not Loading

```bash
# Clear node modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend API Errors

```bash
# View backend logs
docker compose logs backend

# Restart backend
docker compose restart backend
```

## Performance Optimization

### For Production

1. Build frontend for production:
```bash
cd frontend
npm run build
```

2. Update docker-compose.yml to serve built frontend
3. Set strong JWT_SECRET
4. Configure database connection pooling
5. Enable Redis caching
6. Set up proper logging and monitoring

## Next Steps

- Implement real AI valuation model
- Add user role-based access control
- Implement CMDB hierarchy workflows
- Add incident SLA tracking
- Set up CI/CD pipeline
- Configure monitoring and alerting
