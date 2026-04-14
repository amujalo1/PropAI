# PropAI MVP - Quick Start Guide

## Start the Application

```bash
docker compose up
```

Wait for all containers to be healthy (2-3 minutes).

## Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Seed Test Data (Optional)

To populate the database with test data:

```bash
curl -X POST http://localhost:8000/test/seed
```

This creates:
- Test user: `test@example.com` / `testpass123`
- 3 sample properties
- 2 sample incidents

## First Login

1. Go to http://localhost:5173
2. Click "Register" to create an account, or use test credentials if seeded
3. Explore the dashboard, properties, and incidents

## Key Features

- **Dashboard**: Overview of properties and incidents
- **Properties**: Create, view, edit, and delete properties
- **Incidents**: Track issues related to properties
- **Authentication**: Secure login with JWT tokens

## API Examples

### Register User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe"
  }'
```

### Create Property
```bash
curl -X POST http://localhost:8000/properties \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "My Property",
    "type": "residential",
    "location": "City Center",
    "price": 250000,
    "description": "Beautiful property"
  }'
```

### List Properties
```bash
curl http://localhost:8000/properties
```

### Get Property Valuation
```bash
curl -X POST http://localhost:8000/ai/valuation \
  -H "Content-Type: application/json" \
  -d '{"property_id": "PROPERTY_ID"}'
```

## Troubleshooting

### Containers not starting
```bash
docker compose down -v
docker compose build --no-cache
docker compose up
```

### Database errors
```bash
docker compose restart postgres
```

### Frontend not loading
```bash
docker compose restart frontend
```

## Stop the Application

```bash
docker compose down
```

## Clean Everything

```bash
docker compose down -v
```

This removes all containers and volumes, giving you a fresh start.

## Next Steps

- Explore the API documentation at http://localhost:8000/docs
- Create properties and incidents through the UI
- Test the authentication system
- Review the code structure in `/backend` and `/frontend`

For more details, see README.md and DEPLOYMENT.md
