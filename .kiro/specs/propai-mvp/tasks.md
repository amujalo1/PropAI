# PropAI MVP - Implementation Plan

## Overview

This implementation plan breaks down the PropAI MVP into discrete, manageable coding tasks. Each task builds incrementally on previous work, starting with project setup and core infrastructure, then implementing backend services, followed by frontend components, and finally integration and testing. The plan focuses on skeleton implementation with mock data and basic CRUD operations.

## Tasks

- [-] 1. Project Setup and Infrastructure
  - [x] 1.1 Initialize monorepo structure with backend and frontend directories
    - Create `/backend` and `/frontend` directories
    - Create root `docker-compose.yml` file
    - Create `.env.example` files for backend and frontend
    - Create root `README.md` with setup instructions
    - _Requirements: 16.1, 16.2, 16.5, 16.6, 16.7_

  - [x] 1.2 Set up backend project structure
    - Create FastAPI project with directories: `app/`, `models/`, `routes/`, `schemas/`, `utils/`, `config/`
    - Create `requirements.txt` with dependencies (FastAPI, SQLAlchemy, Pydantic, PyJWT, python-dotenv)
    - Create `main.py` entry point
    - Create `config.py` for environment configuration
    - _Requirements: 16.1, 16.3_

  - [x] 1.3 Set up frontend project structure
    - Initialize Vite React project with TypeScript
    - Create directory structure: `src/pages/`, `src/components/`, `src/hooks/`, `src/services/`, `src/types/`
    - Configure TailwindCSS and shadcn/ui
    - Configure TanStack Query
    - _Requirements: 16.2, 16.4_

  - [x] 1.4 Set up Docker environment
    - Create `Dockerfile` for FastAPI backend
    - Create `Dockerfile` for Vite frontend
    - Configure `docker-compose.yml` with services: backend, frontend, PostgreSQL, Redis
    - Set up environment variable passing in docker-compose
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [-] 2. Database Setup and Models
  - [x] 2.1 Create database schema and models
    - Create SQLAlchemy models for User, Property, Incident, CI
    - Define all fields according to design (timestamps, enums, relationships)
    - Create database initialization script
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

  - [x] 2.2 Set up database connection and session management
    - Configure SQLAlchemy engine and session factory
    - Create database utility functions for connection pooling
    - Set up database initialization on startup
    - _Requirements: 14.1, 15.4_

  - [ ]* 2.3 Write property tests for database models
    - **Property 54: Database tables exist**
    - **Property 55: User fields stored**
    - **Property 56: Property fields stored**
    - **Property 57: Incident fields stored**
    - **Property 58: CI fields stored**
    - **Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5**

- [-] 3. Authentication Service Implementation
  - [x] 3.1 Implement user registration endpoint
    - Create User model and schema
    - Implement password hashing
    - Create `POST /auth/register` endpoint
    - Validate email format and password length
    - Return JWT token on success
    - _Requirements: 1.1, 1.3, 1.4, 1.5_

  - [x] 3.2 Implement user login endpoint
    - Create `POST /auth/login` endpoint
    - Verify credentials against hashed password
    - Return JWT token on success
    - Return 401 on invalid credentials
    - _Requirements: 1.2_

  - [x] 3.3 Implement JWT authentication middleware
    - Create middleware to verify JWT tokens
    - Extract user claims from token
    - Return 401 for invalid/missing tokens
    - Apply middleware to protected routes
    - _Requirements: 1.6_

  - [x] 3.4 Implement logout endpoint (mock)
    - Create `POST /auth/logout` endpoint
    - Return success response (mock implementation)
    - _Requirements: 1.7_

  - [ ]* 3.5 Write property tests for authentication
    - **Property 1: Valid registration creates user with token**
    - **Property 2: Valid login returns token**
    - **Property 3: Invalid email rejected**
    - **Property 4: Short password rejected**
    - **Property 5: Default role assignment**
    - **Property 6: Invalid JWT rejected**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6**

- [ ] 4. Property Management Service Implementation
  - [x] 4.1 Implement property creation endpoint
    - Create Property schema with validation
    - Create `POST /properties` endpoint
    - Validate required fields
    - Set default status to DRAFT
    - Return created property with ID
    - _Requirements: 2.1, 2.2, 4.2_

  - [x] 4.2 Implement property list endpoint with pagination and filtering
    - Create `GET /properties` endpoint
    - Implement pagination (limit, offset)
    - Implement status filtering
    - Sort by creation date (newest first)
    - Return paginated response with metadata
    - _Requirements: 2.3, 2.4, 2.5, 13.4_

  - [x] 4.3 Implement property retrieval endpoint
    - Create `GET /properties/{id}` endpoint
    - Return complete property object
    - Return 404 if not found
    - _Requirements: 2.7_

  - [x] 4.4 Implement property update endpoint
    - Create `PUT /properties/{id}` endpoint
    - Validate status against allowed values
    - Preserve creation timestamp, update modification timestamp
    - Return updated property
    - Return 404 if not found
    - _Requirements: 3.1, 3.2, 3.3, 3.6, 4.3_

  - [x] 4.5 Implement property deletion endpoint
    - Create `DELETE /properties/{id}` endpoint
    - Remove property from database
    - Return 404 if not found
    - _Requirements: 3.4, 3.5, 14.6_

  - [ ]* 4.6 Write property tests for property management
    - **Property 7: Valid property creation**
    - **Property 8: Missing fields rejected**
    - **Property 9: Pagination works correctly**
    - **Property 10: Status filtering works**
    - **Property 11: Properties sorted by creation date**
    - **Property 12: Property persistence**
    - **Property 13: Get property by ID**
    - **Property 14: Property update**
    - **Property 15: Update non-existent property returns 404**
    - **Property 16: Status validation**
    - **Property 17: Property deletion**
    - **Property 18: Delete non-existent property returns 404**
    - **Property 19: Timestamp preservation**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

- [ ] 5. Lifecycle Status Implementation
  - [x] 5.1 Define lifecycle status enum and validation
    - Create Enum with all statuses: DRAFT, PENDING_REVIEW, ACTIVE, RESERVED, SOLD, RENTED, SUSPENDED, ARCHIVED
    - Implement status validation in Property schema
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ]* 5.2 Write property tests for lifecycle status
    - **Property 20: All lifecycle statuses supported**
    - **Property 21: Default status is DRAFT**
    - **Property 22: Status update acceptance**
    - **Property 23: Status included in response**
    - **Property 24: Status filter consistency**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

- [ ] 6. CMDB Hierarchy Implementation
  - [x] 6.1 Implement CI model and ID generation
    - Create CI model with hierarchy support
    - Implement CI ID generation: PROP-[TYPE]-[REGION]-[SEQUENCE]
    - Create sequence counter for ID generation
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 6.2 Implement CI creation endpoint
    - Create `POST /ci` endpoint
    - Validate parent CI exists
    - Generate unique CI ID
    - Store hierarchy level and parent reference
    - _Requirements: 5.1, 5.2, 5.3, 5.5_

  - [x] 6.3 Implement CI retrieval endpoints
    - Create `GET /ci/{ci_id}` endpoint
    - Create `GET /ci/hierarchy/{ci_id}` endpoint to return full hierarchy path
    - Create `GET /ci/level/{level}` endpoint to query by hierarchy level
    - _Requirements: 5.4, 5.6_

  - [ ]* 6.4 Write property tests for CMDB hierarchy
    - **Property 25: Five-level hierarchy supported**
    - **Property 26: CI ID format**
    - **Property 27: Hierarchy metadata stored**
    - **Property 28: Hierarchy path retrieval**
    - **Property 29: Parent validation**
    - **Property 30: Query by hierarchy level**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6**

- [ ] 7. Incident Management Service Implementation
  - [x] 7.1 Implement incident creation endpoint
    - Create Incident schema with validation
    - Create `POST /incidents` endpoint
    - Validate required fields and priority enum
    - Set default status to OPEN
    - Return created incident with ID
    - _Requirements: 6.1, 6.2, 6.6, 7.2_

  - [x] 7.2 Implement incident list endpoint with pagination and filtering
    - Create `GET /incidents` endpoint
    - Implement pagination (limit, offset)
    - Implement property_id filtering
    - Implement priority filtering
    - Return paginated response with metadata
    - _Requirements: 6.3, 6.4, 6.5_

  - [x] 7.3 Implement incident retrieval endpoint
    - Create `GET /incidents/{id}` endpoint
    - Return complete incident object
    - Return 404 if not found
    - _Requirements: 6.7_

  - [ ]* 7.4 Write property tests for incident management
    - **Property 31: Valid incident creation**
    - **Property 32: Missing incident fields rejected**
    - **Property 33: Incident pagination**
    - **Property 34: Property incident filtering**
    - **Property 35: Priority incident filtering**
    - **Property 36: Default incident status**
    - **Property 37: Get incident by ID**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7**

- [ ] 8. Incident Priority Implementation
  - [x] 8.1 Define priority enum and validation
    - Create Enum with priorities: P1, P2, P3, P4
    - Implement priority validation in Incident schema
    - _Requirements: 7.1, 7.2_

  - [ ]* 8.2 Write property tests for incident priority
    - **Property 38: All priorities supported**
    - **Property 39: Priority validation on creation**
    - **Property 40: Priority filter consistency**
    - **Property 41: Priority included in response**
    - **Property 42: Priority enum validation**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

- [ ] 9. AI Valuation Service Implementation
  - [x] 9.1 Implement mock valuation endpoint
    - Create `POST /ai/valuation` endpoint
    - Accept property_id parameter
    - Return mock valuation response with estimated_value, currency (EUR), note
    - Return 404 if property not found
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [ ]* 9.2 Write property tests for AI valuation
    - **Property 43: Valuation endpoint returns value**
    - **Property 44: Valuation response format**
    - **Property 45: Valuation non-existent property returns 404**
    - **Property 46: Valuation currency is EUR**
    - **Property 47: Valuation note explains mock**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.5, 8.6**

- [ ] 10. API Response Format Standardization
  - [x] 10.1 Implement response wrapper middleware
    - Create response wrapper for all endpoints
    - Implement success response format with data field
    - Implement error response format with error and details fields
    - Implement pagination metadata format
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_

  - [ ]* 10.2 Write property tests for API response format
    - **Property 48: HTTP status codes correct**
    - **Property 49: Success response has data field**
    - **Property 50: Error response has error field**
    - **Property 51: Paginated response has metadata**
    - **Property 52: Validation errors have details**
    - **Property 53: 404 response has message**
    - **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5, 13.6**

- [ ] 11. Backend Checkpoint - Ensure all tests pass
  - Ensure all backend property tests pass (minimum 100 iterations each)
  - Verify all endpoints are accessible
  - Check database persistence
  - Ask the user if questions arise

- [ ] 12. Frontend Authentication Pages
  - [x] 12.1 Create LoginPage component
    - Create form with email and password fields
    - Implement form validation
    - Call login API endpoint
    - Store JWT token in local storage
    - Redirect to dashboard on success
    - Display error messages on failure
    - _Requirements: 9.1, 9.4, 9.6_

  - [x] 12.2 Create RegisterPage component
    - Create form with email, password, name fields
    - Implement form validation
    - Call register API endpoint
    - Store JWT token in local storage
    - Redirect to dashboard on success
    - Display error messages on failure
    - _Requirements: 9.1, 9.2, 9.3, 9.6_

  - [x] 12.3 Create logout functionality
    - Implement logout button in header
    - Clear JWT token from local storage
    - Redirect to login page
    - _Requirements: 9.7_

  - [ ]* 12.4 Write property tests for authentication UI
    - **Property 3: Invalid email rejected**
    - **Property 4: Short password rejected**
    - **Property 9.3: Registration with valid data redirects**
    - **Property 9.4: Login with valid credentials redirects**
    - **Property 9.5: Invalid credentials show error**
    - **Property 9.6: Token stored in local storage**
    - **Property 9.7: Logout clears token and redirects**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7**

- [ ] 13. Frontend Dashboard Page
  - [x] 13.1 Create Dashboard layout and structure
    - Create Header component with user info and logout button
    - Create Sidebar component with navigation links
    - Create main dashboard content area
    - _Requirements: 10.1, 10.2_

  - [x] 13.2 Create summary cards component
    - Display total properties count
    - Display total incidents count
    - Fetch counts from API
    - _Requirements: 10.2_

  - [x] 13.3 Create recent properties table
    - Display latest 5 properties
    - Show columns: name, type, location, status, price
    - Implement row click navigation to property details
    - Use TanStack Query for data fetching and caching
    - _Requirements: 10.3, 10.5, 10.7_

  - [x] 13.4 Create recent incidents table
    - Display latest 5 incidents
    - Show columns: title, property, priority, status
    - Implement row click navigation to incident details
    - Use TanStack Query for data fetching and caching
    - _Requirements: 10.4, 10.6, 10.7_

  - [ ]* 13.5 Write property tests for dashboard
    - **Property 10.3: Recent properties table displays latest 5**
    - **Property 10.4: Recent incidents table displays latest 5**
    - **Property 10.5: Property row click navigates to details**
    - **Property 10.6: Incident row click navigates to details**
    - **Property 10.7: TanStack Query used for data fetching**
    - **Validates: Requirements 10.3, 10.4, 10.5, 10.6, 10.7**

- [ ] 14. Frontend Properties Management
  - [x] 14.1 Create PropertiesPage component
    - Create table with columns: name, type, location, status, price
    - Implement pagination controls
    - Implement status filter dropdown
    - Implement row click navigation to property details
    - Use TanStack Query for data fetching
    - _Requirements: 11.1, 11.8_

  - [ ] 14.2 Create PropertyCreateForm component
    - Create form with fields: name, type, location, status, price, description
    - Implement form validation
    - Call create property API endpoint
    - Refresh properties table on success
    - Display error messages on failure
    - _Requirements: 11.2, 11.3_

  - [ ] 14.3 Create PropertyDetailsPage component
    - Display all property information
    - Create edit button
    - Implement navigation back to properties list
    - _Requirements: 11.4, 11.5_

  - [ ] 14.4 Create PropertyEditForm component
    - Pre-fill form with current property values
    - Implement form validation
    - Call update property API endpoint
    - Navigate back to details page on success
    - Display error messages on failure
    - _Requirements: 11.6, 11.7_

  - [ ]* 14.5 Write property tests for properties management
    - **Property 11.1: Properties table displays all columns**
    - **Property 11.3: Valid form submission creates property**
    - **Property 11.4: Row click navigates to details**
    - **Property 11.5: Details page displays all information**
    - **Property 11.6: Edit form pre-filled with current values**
    - **Property 11.7: Edit form submission updates property**
    - **Property 11.8: TanStack Query used for data fetching**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8**

- [ ] 15. Frontend Incidents Management
  - [x] 15.1 Create IncidentsPage component
    - Create table with columns: title, property, priority, status
    - Implement pagination controls
    - Implement priority filter dropdown
    - Implement row click navigation to incident details
    - Use TanStack Query for data fetching
    - _Requirements: 12.1, 12.7_

  - [ ] 15.2 Create IncidentCreateForm component
    - Create form with fields: title, description, property_id, priority
    - Implement property dropdown selector
    - Implement priority dropdown selector
    - Implement form validation
    - Call create incident API endpoint
    - Refresh incidents table on success
    - Display error messages on failure
    - _Requirements: 12.2, 12.3_

  - [ ] 15.3 Create IncidentDetailsPage component
    - Display all incident information
    - Implement navigation back to incidents list
    - _Requirements: 12.4, 12.5_

  - [ ]* 15.4 Write property tests for incidents management
    - **Property 12.1: Incidents table displays all columns**
    - **Property 12.3: Valid form submission creates incident**
    - **Property 12.4: Row click navigates to details**
    - **Property 12.5: Details page displays all information**
    - **Property 12.6: Priority filter updates table**
    - **Property 12.7: TanStack Query used for data fetching**
    - **Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7**

- [ ] 16. Frontend Shared Components
  - [x] 16.1 Create Header component
    - Display user information
    - Create logout button
    - Implement navigation links
    - _Requirements: 9.7_

  - [x] 16.2 Create Sidebar component
    - Display navigation links to pages
    - Highlight active page
    - _Requirements: 10.1_

  - [x] 16.3 Create reusable Table component
    - Support columns configuration
    - Support sorting
    - Support filtering
    - Support pagination
    - _Requirements: 11.1, 12.1_

  - [x] 16.4 Create reusable Form component
    - Support field validation
    - Display error messages
    - Support submit and cancel buttons
    - _Requirements: 11.2, 12.2_

  - [ ] 16.5 Create reusable Modal component
    - Support title and content
    - Support action buttons
    - _Requirements: 11.2, 12.2_

  - [x] 16.6 Create Toast notification component
    - Display success messages
    - Display error messages
    - Auto-dismiss after timeout
    - _Requirements: 11.3, 12.3_

- [ ] 17. Frontend Routing and Navigation
  - [x] 17.1 Set up React Router
    - Create route configuration
    - Create protected routes for authenticated pages
    - Redirect unauthenticated users to login
    - _Requirements: 9.1, 10.1_

  - [x] 17.2 Create navigation between pages
    - Implement navigation from dashboard to properties
    - Implement navigation from dashboard to incidents
    - Implement navigation from properties to details
    - Implement navigation from incidents to details
    - _Requirements: 10.5, 10.6, 11.4, 12.4_

- [ ] 18. Frontend API Integration
  - [x] 18.1 Create API client service
    - Set up Axios with base URL
    - Implement request/response interceptors
    - Handle JWT token in headers
    - _Requirements: 9.4, 11.3, 12.3_

  - [x] 18.2 Create API hooks using TanStack Query
    - Create useLogin hook
    - Create useRegister hook
    - Create useProperties hook
    - Create useIncidents hook
    - Create useValuation hook
    - _Requirements: 10.7, 11.8, 12.7_

- [ ] 19. Frontend Checkpoint - Ensure all tests pass
  - Ensure all frontend property tests pass (minimum 100 iterations each)
  - Verify all pages are accessible
  - Verify navigation works correctly
  - Verify API integration works
  - Ask the user if questions arise

- [ ] 20. Integration Testing
  - [x] 20.1 Test end-to-end authentication flow
    - Register new user
    - Login with credentials
    - Verify token is stored
    - Verify dashboard is accessible
    - Logout and verify redirect
    - _Requirements: 1.1, 1.2, 9.3, 9.4, 9.7_

  - [x] 20.2 Test end-to-end property management flow
    - Create property from UI
    - Verify property appears in list
    - Update property from UI
    - Verify update is reflected
    - Delete property from UI
    - Verify property is removed
    - _Requirements: 2.1, 2.3, 3.1, 3.4_

  - [x] 20.3 Test end-to-end incident management flow
    - Create incident from UI
    - Verify incident appears in list
    - Filter incidents by priority
    - Verify filtering works
    - _Requirements: 6.1, 6.3, 6.5_

  - [x] 20.4 Test Docker environment
    - Run `docker compose up`
    - Verify all containers start
    - Verify backend is accessible at http://localhost:8000
    - Verify frontend is accessible at http://localhost:5173
    - Verify database is initialized
    - Run `docker compose down`
    - Verify containers stop
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

- [ ] 21. Final Checkpoint - Ensure all tests pass
  - Ensure all property tests pass (minimum 100 iterations each)
  - Ensure all unit tests pass
  - Ensure all integration tests pass
  - Verify Docker environment works end-to-end
  - Ask the user if questions arise

- [ ] 22. Documentation and Cleanup
  - [x] 22.1 Update README with complete setup instructions
    - Add prerequisites section
    - Add installation steps
    - Add running instructions
    - Add testing instructions
    - Add troubleshooting section
    - _Requirements: 16.7_

  - [x] 22.2 Create API documentation
    - Document all endpoints
    - Include request/response examples
    - Include error codes
    - _Requirements: 13.1, 13.2, 13.3_

  - [x] 22.3 Clean up code and remove debug statements
    - Remove console.log statements
    - Remove debug code
    - Ensure consistent code style
    - _Requirements: 16.1, 16.2_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP (focus on core features first)
- Each task references specific requirements for traceability
- Property tests should run with minimum 100 iterations for comprehensive coverage
- Checkpoints ensure incremental validation and early error detection
- All property tests must be implemented using Hypothesis (backend) and fast-check (frontend)
- Each property test must include a comment tag: `Feature: propai-mvp, Property {number}: {property_text}`

