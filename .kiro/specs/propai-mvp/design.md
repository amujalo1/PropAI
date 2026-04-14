# PropAI MVP - Design Document

## Overview

PropAI is a cloud-based SaaS platform MVP for real estate management. The architecture follows a modern three-tier design: a FastAPI backend providing RESTful APIs, a React frontend with TypeScript for type safety, and PostgreSQL for persistent data storage. The MVP focuses on demonstrating clean architecture, basic CRUD operations, and a working skeleton with mock implementations for AI features.

The design prioritizes:
- **Simplicity**: Minimal business logic, focus on structure
- **Scalability**: Clean separation of concerns enabling future expansion
- **Developer Experience**: Clear patterns and organized code structure
- **MVP Scope**: Dummy endpoints, mock responses, no complex workflows

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + TS)                   │
│  Pages: Login, Dashboard, Properties, Incidents             │
│  State: TanStack Query (caching, sync)                      │
│  Styling: TailwindCSS + shadcn/ui                           │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────────┐
│                  Backend (FastAPI)                          │
│  Routes: /auth, /properties, /incidents, /ci, /ai          │
│  Middleware: JWT authentication, CORS, error handling       │
│  Services: Business logic layer (thin for MVP)              │
└────────────────────┬────────────────────────────────────────┘
                     │ SQL
┌────────────────────▼────────────────────────────────────────┐
│              Database (PostgreSQL)                          │
│  Tables: users, properties, incidents, ci_hierarchy         │
│  Indexes: On frequently queried columns                     │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend**:
- FastAPI 0.104+ (async web framework)
- SQLAlchemy 2.0+ (ORM)
- Pydantic (data validation)
- PyJWT (JWT authentication)
- python-dotenv (configuration)

**Frontend**:
- React 19 (UI library)
- TypeScript 5+ (type safety)
- Vite (build tool)
- TanStack Query v5 (state management)
- TailwindCSS (styling)
- shadcn/ui (component library)
- Axios (HTTP client)

**Database**:
- PostgreSQL 15+ (primary data store)
- Redis (mock for MVP, placeholder for caching)

**Infrastructure**:
- Docker & Docker Compose (containerization)
- Arch Linux (development environment)

## Components and Interfaces

### Backend Components

#### 1. Authentication Service

**Purpose**: Handle user registration, login, and JWT token management

**Key Functions**:
- `register_user(email, password, name) -> User`: Create new user account
- `login_user(email, password) -> str`: Authenticate and return JWT token
- `verify_token(token) -> dict`: Validate JWT and extract claims
- `hash_password(password) -> str`: Securely hash passwords
- `create_jwt_token(user_id, role) -> str`: Generate JWT token

**Dependencies**: User model, JWT library, password hashing library

#### 2. Property Service

**Purpose**: Manage property CRUD operations and queries

**Key Functions**:
- `create_property(data) -> Property`: Create new property
- `get_property(id) -> Property`: Retrieve property by ID
- `list_properties(filters, pagination) -> List[Property]`: List with filtering
- `update_property(id, data) -> Property`: Update property details
- `delete_property(id) -> bool`: Delete property
- `filter_by_status(status) -> List[Property]`: Filter by lifecycle status

**Dependencies**: Property model, database session

#### 3. Incident Service

**Purpose**: Manage incident CRUD operations and queries

**Key Functions**:
- `create_incident(data) -> Incident`: Create new incident
- `get_incident(id) -> Incident`: Retrieve incident by ID
- `list_incidents(filters, pagination) -> List[Incident]`: List with filtering
- `get_incidents_by_property(property_id) -> List[Incident]`: Get property incidents
- `filter_by_priority(priority) -> List[Incident]`: Filter by priority

**Dependencies**: Incident model, database session

#### 4. CMDB Service

**Purpose**: Manage hierarchical CI structure and ID generation

**Key Functions**:
- `create_ci(type, region, parent_id) -> CI`: Create CI with auto-generated ID
- `generate_ci_id(type, region) -> str`: Generate PROP-[TYPE]-[REGION]-[SEQUENCE]
- `get_ci_hierarchy(ci_id) -> List[CI]`: Get full hierarchy path
- `get_ci_by_level(level) -> List[CI]`: Query by hierarchy level
- `validate_parent(parent_id) -> bool`: Verify parent exists

**Dependencies**: CI model, database session, ID generation logic

#### 5. AI Valuation Service

**Purpose**: Provide mock AI-powered property valuations

**Key Functions**:
- `get_valuation(property_id) -> Valuation`: Return mock valuation
- `generate_mock_valuation(property) -> dict`: Generate placeholder estimate

**Dependencies**: Property model, mock data generator

#### 6. API Routes

**Authentication Routes**:
- `POST /auth/register`: Register new user
- `POST /auth/login`: Login and get JWT token
- `POST /auth/logout`: Logout (mock for MVP)

**Property Routes**:
- `POST /properties`: Create property
- `GET /properties`: List properties with filters
- `GET /properties/{id}`: Get property by ID
- `PUT /properties/{id}`: Update property
- `DELETE /properties/{id}`: Delete property

**Incident Routes**:
- `POST /incidents`: Create incident
- `GET /incidents`: List incidents with filters
- `GET /incidents/{id}`: Get incident by ID
- `GET /incidents/property/{property_id}`: Get incidents for property

**CMDB Routes**:
- `POST /ci`: Create CI
- `GET /ci/{ci_id}`: Get CI details
- `GET /ci/hierarchy/{ci_id}`: Get full hierarchy

**AI Routes**:
- `POST /ai/valuation`: Get property valuation

### Frontend Components

#### 1. Authentication Pages

**LoginPage**:
- Form with email and password fields
- Submit button and register link
- Error message display
- Redirect to dashboard on success

**RegisterPage**:
- Form with email, password, name fields
- Submit button and login link
- Validation error display
- Redirect to dashboard on success

#### 2. Dashboard Page

**Components**:
- Header with user info and logout button
- Summary cards: Total Properties, Total Incidents
- Recent Properties table (5 latest)
- Recent Incidents table (5 latest)
- Navigation sidebar

#### 3. Properties Management

**PropertiesPage**:
- Table with columns: name, type, location, status, price
- Create Property button
- Filter by status dropdown
- Pagination controls
- Row click navigation to details

**PropertyCreateForm**:
- Fields: name, type, location, status, price, description
- Validation feedback
- Submit and cancel buttons

**PropertyDetailsPage**:
- Display all property information
- Edit button
- Delete button (optional)
- Back to list button

**PropertyEditForm**:
- Pre-filled form with current values
- Submit and cancel buttons

#### 4. Incidents Management

**IncidentsPage**:
- Table with columns: title, property, priority, status
- Create Incident button
- Filter by priority dropdown
- Pagination controls
- Row click navigation to details

**IncidentCreateForm**:
- Fields: title, description, property_id, priority
- Property dropdown selector
- Priority dropdown selector
- Submit and cancel buttons

**IncidentDetailsPage**:
- Display all incident information
- Back to list button

#### 5. Shared Components

**Header**: Navigation, user menu, logout
**Sidebar**: Navigation links to pages
**Table**: Reusable table with sorting, filtering, pagination
**Form**: Reusable form with validation
**Modal**: Reusable modal for dialogs
**Toast**: Notification system for feedback

## Data Models

### User Model

```
User:
  - id: UUID (primary key)
  - email: String (unique, indexed)
  - password_hash: String
  - name: String
  - role: Enum (admin, data_steward, ci_owner, agent)
  - created_at: DateTime
  - updated_at: DateTime
```

### Property Model

```
Property:
  - id: UUID (primary key)
  - name: String (indexed)
  - type: String (residential, commercial, land)
  - location: String
  - status: Enum (DRAFT, PENDING_REVIEW, ACTIVE, RESERVED, SOLD, RENTED, SUSPENDED, ARCHIVED)
  - price: Decimal
  - description: String (optional)
  - created_at: DateTime
  - updated_at: DateTime
```

### Incident Model

```
Incident:
  - id: UUID (primary key)
  - title: String (indexed)
  - description: String
  - property_id: UUID (foreign key to Property)
  - priority: Enum (P1, P2, P3, P4)
  - status: String (OPEN, IN_PROGRESS, RESOLVED, CLOSED)
  - created_at: DateTime
  - updated_at: DateTime
```

### CI (Configuration Item) Model

```
CI:
  - id: UUID (primary key)
  - ci_id: String (unique, indexed) - Format: PROP-[TYPE]-[REGION]-[SEQUENCE]
  - type: Enum (Location, Complex, Building, Property, Component)
  - region: String
  - sequence: Integer
  - hierarchy_level: Integer (1-5)
  - parent_id: UUID (foreign key, nullable)
  - created_at: DateTime
  - updated_at: DateTime
```

### Valuation Model (Response Only)

```
Valuation:
  - estimated_value: Decimal
  - currency: String (EUR for MVP)
  - note: String (explanation of mock nature)
```

## API Response Format

### Success Response (200/201)

```json
{
  "data": {
    "id": "uuid",
    "name": "Property Name",
    ...
  }
}
```

### List Response with Pagination

```json
{
  "data": [
    { "id": "uuid", "name": "Property 1" },
    { "id": "uuid", "name": "Property 2" }
  ],
  "pagination": {
    "total": 100,
    "limit": 10,
    "offset": 0
  }
}
```

### Error Response

```json
{
  "error": "Validation error",
  "details": {
    "email": "Invalid email format",
    "password": "Password too short"
  }
}
```

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Authentication Properties

**Property 1: Valid registration creates user with token**
*For any* valid registration request with email, password, and name, the system should create a user account and return a non-empty JWT token.
**Validates: Requirements 1.1**

**Property 2: Valid login returns token**
*For any* user account and valid login credentials, the system should return a non-empty JWT token.
**Validates: Requirements 1.2**

**Property 3: Invalid email rejected**
*For any* registration request with an invalid email format, the system should reject the request with a validation error.
**Validates: Requirements 1.3**

**Property 4: Short password rejected**
*For any* registration request with a password shorter than 8 characters, the system should reject the request with a validation error.
**Validates: Requirements 1.4**

**Property 5: Default role assignment**
*For any* new user created without an explicit role, the system should assign the default role "agent".
**Validates: Requirements 1.5**

**Property 6: Invalid JWT rejected**
*For any* request with an invalid or malformed JWT token, the system should return a 401 Unauthorized response.
**Validates: Requirements 1.6**

### Property Management Properties

**Property 7: Valid property creation**
*For any* valid property creation request with required fields (name, type, location, status, price), the system should create the property and return it with a unique ID.
**Validates: Requirements 2.1**

**Property 8: Missing fields rejected**
*For any* property creation request with missing required fields, the system should reject the request with a validation error.
**Validates: Requirements 2.2**

**Property 9: Pagination works correctly**
*For any* property list request with limit and offset parameters, the system should return the correct subset of properties.
**Validates: Requirements 2.3**

**Property 10: Status filtering works**
*For any* property list request with a status filter, the system should return only properties matching that status.
**Validates: Requirements 2.4**

**Property 11: Properties sorted by creation date**
*For any* property list request, properties should be sorted by creation date in descending order (newest first).
**Validates: Requirements 2.5**

**Property 12: Property persistence**
*For any* created property, querying the database should return the same property with all fields intact.
**Validates: Requirements 2.6**

**Property 13: Get property by ID**
*For any* existing property ID, the system should return the complete property object; for non-existent IDs, it should return a 404 error.
**Validates: Requirements 2.7**

**Property 14: Property update**
*For any* valid property update request, the system should update the property and return the updated object.
**Validates: Requirements 3.1**

**Property 15: Update non-existent property returns 404**
*For any* update request for a non-existent property, the system should return a 404 error.
**Validates: Requirements 3.2**

**Property 16: Status validation**
*For any* property update with an invalid status value, the system should reject the request with a validation error.
**Validates: Requirements 3.3**

**Property 17: Property deletion**
*For any* existing property, deleting it should remove it from the database.
**Validates: Requirements 3.4**

**Property 18: Delete non-existent property returns 404**
*For any* delete request for a non-existent property, the system should return a 404 error.
**Validates: Requirements 3.5**

**Property 19: Timestamp preservation**
*For any* property update, the creation timestamp should remain unchanged while the modification timestamp should be updated.
**Validates: Requirements 3.6**

### Lifecycle Status Properties

**Property 20: All lifecycle statuses supported**
*For any* valid lifecycle status (DRAFT, PENDING_REVIEW, ACTIVE, RESERVED, SOLD, RENTED, SUSPENDED, ARCHIVED), the system should accept it.
**Validates: Requirements 4.1**

**Property 21: Default status is DRAFT**
*For any* newly created property, the initial status should be DRAFT.
**Validates: Requirements 4.2**

**Property 22: Status update acceptance**
*For any* property and valid status value, the system should accept the status update without workflow enforcement.
**Validates: Requirements 4.3**

**Property 23: Status included in response**
*For any* property details request, the response should include the current lifecycle status.
**Validates: Requirements 4.4**

**Property 24: Status filter consistency**
*For any* status filter applied to property list, all returned properties should have the matching status.
**Validates: Requirements 4.5**

### CMDB Hierarchy Properties

**Property 25: Five-level hierarchy supported**
*For any* CI type (Location, Complex, Building, Property, Component), the system should support creating CIs at all five hierarchy levels.
**Validates: Requirements 5.1**

**Property 26: CI ID format**
*For any* created CI, the generated CI ID should follow the format PROP-[TYPE]-[REGION]-[SEQUENCE].
**Validates: Requirements 5.2**

**Property 27: Hierarchy metadata stored**
*For any* created CI, the system should store the hierarchy level and parent reference.
**Validates: Requirements 5.3**

**Property 28: Hierarchy path retrieval**
*For any* CI request, the system should return the complete hierarchy path from root to the CI.
**Validates: Requirements 5.4**

**Property 29: Parent validation**
*For any* child CI creation request with a non-existent parent, the system should reject the request with a validation error.
**Validates: Requirements 5.5**

**Property 30: Query by hierarchy level**
*For any* hierarchy level query, the system should return only CIs at that level.
**Validates: Requirements 5.6**

### Incident Management Properties

**Property 31: Valid incident creation**
*For any* valid incident creation request with required fields (title, description, property_id, priority), the system should create the incident and return it.
**Validates: Requirements 6.1**

**Property 32: Missing incident fields rejected**
*For any* incident creation request with missing required fields, the system should reject the request with a validation error.
**Validates: Requirements 6.2**

**Property 33: Incident pagination**
*For any* incident list request with limit and offset parameters, the system should return the correct subset of incidents.
**Validates: Requirements 6.3**

**Property 34: Property incident filtering**
*For any* incident list request filtered by property_id, the system should return only incidents related to that property.
**Validates: Requirements 6.4**

**Property 35: Priority incident filtering**
*For any* incident list request filtered by priority, the system should return only incidents matching that priority.
**Validates: Requirements 6.5**

**Property 36: Default incident status**
*For any* newly created incident, the initial status should be OPEN.
**Validates: Requirements 6.6**

**Property 37: Get incident by ID**
*For any* existing incident ID, the system should return the complete incident object; for non-existent IDs, it should return a 404 error.
**Validates: Requirements 6.7**

### Incident Priority Properties

**Property 38: All priorities supported**
*For any* valid priority level (P1, P2, P3, P4), the system should accept it.
**Validates: Requirements 7.1**

**Property 39: Priority validation on creation**
*For any* incident creation request with an invalid priority value, the system should reject the request with a validation error.
**Validates: Requirements 7.2**

**Property 40: Priority filter consistency**
*For any* priority filter applied to incident list, all returned incidents should have the matching priority.
**Validates: Requirements 7.3**

**Property 41: Priority included in response**
*For any* incident details request, the response should include the priority level.
**Validates: Requirements 7.4**

**Property 42: Priority enum validation**
*For any* incident, the priority field should only accept enum values (P1, P2, P3, P4).
**Validates: Requirements 7.5**

### AI Valuation Properties

**Property 43: Valuation endpoint returns value**
*For any* valuation request with an existing property ID, the system should return an estimated property value.
**Validates: Requirements 8.1**

**Property 44: Valuation response format**
*For any* valuation response, it should include fields: estimated_value (number), currency (string), note (string).
**Validates: Requirements 8.2**

**Property 45: Valuation non-existent property returns 404**
*For any* valuation request for a non-existent property, the system should return a 404 error.
**Validates: Requirements 8.3**

**Property 46: Valuation currency is EUR**
*For any* valuation response, the currency field should be "EUR".
**Validates: Requirements 8.5**

**Property 47: Valuation note explains mock**
*For any* valuation response, the note field should explain the mock nature of the response.
**Validates: Requirements 8.6**

### API Response Format Properties

**Property 48: HTTP status codes correct**
*For any* successful API response, GET/PUT requests should return 200 and POST requests should return 201.
**Validates: Requirements 13.1**

**Property 49: Success response has data field**
*For any* successful API response, the response should include a data field containing the payload.
**Validates: Requirements 13.2**

**Property 50: Error response has error field**
*For any* error API response, the response should include an error field with a descriptive message.
**Validates: Requirements 13.3**

**Property 51: Paginated response has metadata**
*For any* paginated API response, the response should include pagination metadata (total, limit, offset).
**Validates: Requirements 13.4**

**Property 52: Validation errors have details**
*For any* validation error response, the response should include a details field with field-level error messages.
**Validates: Requirements 13.5**

**Property 53: 404 response has message**
*For any* 404 error response, the response should include a message indicating the resource was not found.
**Validates: Requirements 13.6**

### Database Schema Properties

**Property 54: Database tables exist**
*For any* system startup, the database should have tables for users, properties, incidents, and ci_hierarchy.
**Validates: Requirements 14.1**

**Property 55: User fields stored**
*For any* created user, the database should store email, hashed password, name, role, created_at, updated_at.
**Validates: Requirements 14.2**

**Property 56: Property fields stored**
*For any* created property, the database should store name, type, location, status, price, description, created_at, updated_at.
**Validates: Requirements 14.3**

**Property 57: Incident fields stored**
*For any* created incident, the database should store title, description, property_id, priority, status, created_at, updated_at.
**Validates: Requirements 14.4**

**Property 58: CI fields stored**
*For any* created CI, the database should store ci_id, type, region, sequence, hierarchy_level, parent_id, created_at, updated_at.
**Validates: Requirements 14.5**

**Property 59: Property deletion removes record**
*For any* deleted property, the database should no longer contain the record.
**Validates: Requirements 14.6**

**Property 60: Query operations supported**
*For any* data query, the system should support filtering, sorting, and pagination operations.
**Validates: Requirements 14.7**

### Infrastructure Properties

**Property 61: Backend accessible on startup**
*For any* Docker container startup, the backend should be accessible at http://localhost:8000.
**Validates: Requirements 15.2**

**Property 62: Frontend accessible on startup**
*For any* Docker container startup, the frontend should be accessible at http://localhost:5173.
**Validates: Requirements 15.3**

**Property 63: Database initialized on startup**
*For any* Docker container startup, the database should be initialized with schema and ready for connections.
**Validates: Requirements 15.4**

**Property 64: Data persists across restarts**
*For any* data created before container restart, the data should still exist after containers restart.
**Validates: Requirements 15.7**

### Project Structure Properties

**Property 65: Backend directory structure**
*For any* backend project, the directory structure should include app/, models/, routes/, schemas/, utils/, config/.
**Validates: Requirements 16.1**

**Property 66: Frontend directory structure**
*For any* frontend project, the directory structure should include src/pages/, src/components/, src/hooks/, src/services/, src/types/.
**Validates: Requirements 16.2**

**Property 67: Configuration from environment**
*For any* backend startup, the system should load configuration from environment variables.
**Validates: Requirements 16.3**

**Property 68: Docker compose file exists**
*For any* project, a docker-compose.yml file should exist at the root level.
**Validates: Requirements 16.5**

**Property 69: Environment example files exist**
*For any* project, .env.example files should exist for both backend and frontend.
**Validates: Requirements 16.6**

**Property 70: README exists**
*For any* project, a README.md file should exist with setup and running instructions.
**Validates: Requirements 16.7**

## Error Handling

### Backend Error Handling

**Validation Errors (400)**:
- Missing required fields
- Invalid data types
- Invalid enum values
- Email format validation
- Password length validation

**Authentication Errors (401)**:
- Invalid JWT token
- Expired token
- Missing authorization header

**Not Found Errors (404)**:
- Property not found
- Incident not found
- CI not found
- User not found

**Server Errors (500)**:
- Database connection failures
- Unexpected exceptions
- Configuration errors

### Frontend Error Handling

**Network Errors**:
- Display toast notification with error message
- Retry mechanism for failed requests
- Graceful degradation

**Validation Errors**:
- Display field-level error messages
- Highlight invalid fields
- Prevent form submission

**Authentication Errors**:
- Redirect to login page
- Clear stored token
- Display error message

## Testing Strategy

### Unit Testing Approach

**Backend Unit Tests**:
- Test each service function independently
- Mock database layer
- Test validation logic
- Test error handling
- Test edge cases (empty strings, null values, boundary values)
- Use pytest framework

**Frontend Unit Tests**:
- Test React components in isolation
- Mock API calls
- Test form validation
- Test state management
- Use Vitest framework

### Property-Based Testing Approach

**Property-Based Testing Library**: 
- Backend: Hypothesis (Python)
- Frontend: fast-check (TypeScript)

**Property Test Configuration**:
- Minimum 100 iterations per property test
- Each test references a design document property
- Tag format: `Feature: propai-mvp, Property {number}: {property_text}`

**Property Test Coverage**:
- Authentication: Properties 1-6
- Property Management: Properties 7-19
- Lifecycle Status: Properties 20-24
- CMDB Hierarchy: Properties 25-30
- Incident Management: Properties 31-42
- AI Valuation: Properties 43-47
- API Response Format: Properties 48-53
- Database Schema: Properties 54-60
- Infrastructure: Properties 61-64
- Project Structure: Properties 65-70

**Testing Dual Approach**:
- Unit tests validate specific examples and edge cases
- Property tests validate universal properties across all inputs
- Together they provide comprehensive coverage



