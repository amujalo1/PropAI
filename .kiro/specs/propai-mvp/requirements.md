# PropAI MVP - Requirements Document

## Introduction

PropAI is a cloud-based SaaS platform MVP for real estate agencies, investors, and buyers. This MVP focuses on demonstrating architecture and providing a working skeleton with basic CRUD operations, dummy endpoints, simple database schema, and clean project structure. The platform enables users to manage properties, track incidents, and access AI-powered valuation estimates through a modern web interface.

## Glossary

- **Property**: A real estate asset (residential, commercial, land) managed in the system
- **CI (Configuration Item)**: A hierarchical component in the CMDB (Location → Complex → Building → Property → Component)
- **CMDB**: Configuration Management Database - hierarchical structure for organizing properties
- **Incident**: An issue or event related to a property requiring tracking and management
- **Lifecycle Status**: Current state of a property (DRAFT, PENDING_REVIEW, ACTIVE, RESERVED, SOLD, RENTED, SUSPENDED, ARCHIVED)
- **JWT**: JSON Web Token used for authentication
- **Role**: User permission level (admin, data_steward, ci_owner, agent)
- **Valuation**: AI-powered estimated property value
- **Mock Response**: Placeholder data returned by endpoints during MVP phase
- **SaaS**: Software as a Service - cloud-based delivery model
- **MVP**: Minimum Viable Product - focused on core features and architecture

## Requirements

### Requirement 1: User Authentication and Authorization

**User Story:** As a user, I want to register and log in to PropAI, so that I can access the platform securely and manage my properties.

#### Acceptance Criteria

1. WHEN a user submits valid registration credentials (email, password, name), THE System SHALL create a new user account and return a JWT token
2. WHEN a user submits valid login credentials (email, password), THE System SHALL authenticate the user and return a JWT token
3. WHEN a user provides an invalid email format during registration, THE System SHALL reject the registration and return a validation error
4. WHEN a user provides a password shorter than 8 characters, THE System SHALL reject the registration and return a validation error
5. WHEN a user logs in, THE System SHALL assign a default role (agent) if no role is specified
6. WHEN a user provides an invalid JWT token in a request, THE System SHALL return a 401 Unauthorized response
7. WHEN a user logs out, THE System SHALL invalidate their session (mock implementation for MVP)

### Requirement 2: Property Management - Create and List

**User Story:** As a real estate agent, I want to create new properties and view a list of all properties, so that I can manage my portfolio effectively.

#### Acceptance Criteria

1. WHEN a user submits a valid property creation request with required fields (name, type, location, status, price), THE System SHALL create a new property and return the created property object with a unique ID
2. WHEN a user attempts to create a property with missing required fields, THE System SHALL reject the request and return a validation error
3. WHEN a user requests the property list, THE System SHALL return all properties with pagination support (limit, offset)
4. WHEN a user requests properties with a specific status filter, THE System SHALL return only properties matching that status
5. WHEN a user requests the property list, THE System SHALL return properties sorted by creation date (newest first)
6. WHEN a property is created, THE System SHALL persist it to the database immediately
7. WHEN a user requests a property by ID, THE System SHALL return the complete property object or a 404 error if not found

### Requirement 3: Property Management - Update and Delete

**User Story:** As a real estate agent, I want to update property details and optionally delete properties, so that I can keep my portfolio current and remove outdated listings.

#### Acceptance Criteria

1. WHEN a user submits a valid property update request with new values, THE System SHALL update the property and return the updated object
2. WHEN a user attempts to update a non-existent property, THE System SHALL return a 404 error
3. WHEN a user updates a property's status, THE System SHALL validate the new status against allowed lifecycle statuses
4. WHEN a user requests to delete a property, THE System SHALL remove it from the database
5. WHEN a user attempts to delete a non-existent property, THE System SHALL return a 404 error
6. WHEN a property is updated, THE System SHALL preserve the creation timestamp and update the modification timestamp

### Requirement 4: Property Lifecycle Management

**User Story:** As a property manager, I want to track property status through its lifecycle, so that I can understand the current state of each property in my portfolio.

#### Acceptance Criteria

1. THE System SHALL support the following lifecycle statuses: DRAFT, PENDING_REVIEW, ACTIVE, RESERVED, SOLD, RENTED, SUSPENDED, ARCHIVED
2. WHEN a property is created, THE System SHALL set its initial status to DRAFT
3. WHEN a user updates a property's status, THE System SHALL accept any valid status value (no workflow enforcement in MVP)
4. WHEN a user requests property details, THE System SHALL include the current lifecycle status
5. WHEN a user filters properties by status, THE System SHALL return only properties with the matching status

### Requirement 5: CMDB Hierarchy Structure

**User Story:** As a system administrator, I want to organize properties in a hierarchical structure, so that I can manage complex real estate portfolios with multiple locations and buildings.

#### Acceptance Criteria

1. THE System SHALL support a five-level hierarchy: Location → Complex → Building → Property → Component
2. WHEN a CI (Configuration Item) is created, THE System SHALL generate a unique CI ID in format PROP-[TYPE]-[REGION]-[SEQUENCE]
3. WHEN a CI is created, THE System SHALL store the hierarchy level and parent reference
4. WHEN a user requests CI details, THE System SHALL return the complete hierarchy path
5. WHEN a user creates a child CI, THE System SHALL validate that the parent CI exists
6. THE System SHALL support querying CIs by hierarchy level

### Requirement 6: Incident Management - Create and List

**User Story:** As a property manager, I want to create and track incidents related to properties, so that I can manage issues and maintain property quality.

#### Acceptance Criteria

1. WHEN a user submits a valid incident creation request with required fields (title, description, property_id, priority), THE System SHALL create a new incident and return the created incident object
2. WHEN a user attempts to create an incident with missing required fields, THE System SHALL reject the request and return a validation error
3. WHEN a user requests the incident list, THE System SHALL return all incidents with pagination support
4. WHEN a user requests incidents for a specific property, THE System SHALL return only incidents related to that property
5. WHEN a user requests incidents with a specific priority filter, THE System SHALL return only incidents matching that priority
6. WHEN an incident is created, THE System SHALL set its status to OPEN (mock implementation)
7. WHEN a user requests an incident by ID, THE System SHALL return the complete incident object or a 404 error if not found

### Requirement 7: Incident Priority Classification

**User Story:** As an incident manager, I want to classify incidents by priority level, so that I can prioritize response and resolution efforts.

#### Acceptance Criteria

1. THE System SHALL support the following priority levels: P1 (Critical), P2 (High), P3 (Medium), P4 (Low)
2. WHEN an incident is created, THE System SHALL require a valid priority value
3. WHEN a user filters incidents by priority, THE System SHALL return only incidents matching that priority
4. WHEN a user requests incident details, THE System SHALL include the priority level
5. THE System SHALL accept priority values as enum (P1, P2, P3, P4)

### Requirement 8: AI Valuation Endpoint

**User Story:** As a real estate analyst, I want to get AI-powered property valuations, so that I can make data-driven decisions about property pricing and investment.

#### Acceptance Criteria

1. WHEN a user submits a valuation request with a property ID, THE System SHALL return an estimated property value
2. WHEN a user submits a valuation request, THE System SHALL return a response with fields: estimated_value (number), currency (string), note (string)
3. WHEN a user submits a valuation request for a non-existent property, THE System SHALL return a 404 error
4. WHEN a user submits a valuation request, THE System SHALL return a mock response (placeholder AI implementation)
5. THE System SHALL return valuations in EUR currency for MVP
6. WHEN a valuation is requested, THE System SHALL include a note field explaining the mock nature of the response

### Requirement 9: Frontend Authentication UI

**User Story:** As a user, I want to log in and register through a web interface, so that I can access PropAI from my browser.

#### Acceptance Criteria

1. WHEN a user visits the application, THE UI SHALL display a login page if the user is not authenticated
2. WHEN a user clicks the register link, THE UI SHALL display a registration form with fields for email, password, name
3. WHEN a user submits the registration form with valid data, THE UI SHALL create the account and redirect to the dashboard
4. WHEN a user submits the login form with valid credentials, THE UI SHALL authenticate and redirect to the dashboard
5. WHEN a user submits invalid credentials, THE UI SHALL display an error message
6. WHEN a user is authenticated, THE UI SHALL store the JWT token in local storage
7. WHEN a user clicks logout, THE UI SHALL clear the token and redirect to the login page

### Requirement 10: Frontend Dashboard

**User Story:** As a user, I want to see a dashboard with an overview of my properties and incidents, so that I can quickly understand my portfolio status.

#### Acceptance Criteria

1. WHEN a user logs in, THE UI SHALL display a dashboard page
2. WHEN the dashboard loads, THE UI SHALL display a summary section with property and incident counts
3. WHEN the dashboard loads, THE UI SHALL display a recent properties table showing the latest 5 properties
4. WHEN the dashboard loads, THE UI SHALL display a recent incidents table showing the latest 5 incidents
5. WHEN a user clicks on a property in the table, THE UI SHALL navigate to the property details page
6. WHEN a user clicks on an incident in the table, THE UI SHALL navigate to the incident details page
7. WHEN the dashboard loads, THE UI SHALL fetch data using TanStack Query for caching and state management

### Requirement 11: Frontend Properties Management UI

**User Story:** As a real estate agent, I want to manage properties through the web interface, so that I can create, view, and update my listings.

#### Acceptance Criteria

1. WHEN a user navigates to the properties page, THE UI SHALL display a table of all properties with columns: name, type, location, status, price
2. WHEN a user clicks the "Create Property" button, THE UI SHALL display a form with fields for name, type, location, status, price, description
3. WHEN a user submits the property creation form with valid data, THE UI SHALL create the property and refresh the table
4. WHEN a user clicks on a property row, THE UI SHALL navigate to the property details page
5. WHEN a user is on the property details page, THE UI SHALL display all property information and an edit button
6. WHEN a user clicks the edit button, THE UI SHALL display an editable form with current property values
7. WHEN a user submits the edit form, THE UI SHALL update the property and return to the details page
8. WHEN the properties page loads, THE UI SHALL use TanStack Query to fetch and cache property data

### Requirement 12: Frontend Incidents Management UI

**User Story:** As a property manager, I want to manage incidents through the web interface, so that I can track and resolve property issues.

#### Acceptance Criteria

1. WHEN a user navigates to the incidents page, THE UI SHALL display a table of all incidents with columns: title, property, priority, status
2. WHEN a user clicks the "Create Incident" button, THE UI SHALL display a form with fields for title, description, property_id, priority
3. WHEN a user submits the incident creation form with valid data, THE UI SHALL create the incident and refresh the table
4. WHEN a user clicks on an incident row, THE UI SHALL navigate to the incident details page
5. WHEN a user is on the incident details page, THE UI SHALL display all incident information
6. WHEN a user filters incidents by priority, THE UI SHALL update the table to show only matching incidents
7. WHEN the incidents page loads, THE UI SHALL use TanStack Query to fetch and cache incident data

### Requirement 13: API Response Format Consistency

**User Story:** As a frontend developer, I want consistent API response formats, so that I can reliably parse and handle responses across the application.

#### Acceptance Criteria

1. WHEN the API returns a successful response, THE System SHALL use HTTP status 200 for GET/PUT requests and 201 for POST requests
2. WHEN the API returns a successful response, THE System SHALL include a data field containing the response payload
3. WHEN the API returns an error response, THE System SHALL include an error field with a descriptive message
4. WHEN the API returns a paginated response, THE System SHALL include pagination metadata (total, limit, offset)
5. WHEN the API returns validation errors, THE System SHALL include a details field with field-level error messages
6. WHEN the API returns a 404 error, THE System SHALL include a message indicating the resource was not found

### Requirement 14: Database Schema and Persistence

**User Story:** As a system architect, I want a well-structured database schema, so that I can reliably store and retrieve property and incident data.

#### Acceptance Criteria

1. WHEN the system starts, THE Database SHALL have tables for users, properties, incidents, and ci_hierarchy
2. WHEN a user is created, THE Database SHALL store email, hashed password, name, role, created_at, updated_at
3. WHEN a property is created, THE Database SHALL store name, type, location, status, price, description, created_at, updated_at
4. WHEN an incident is created, THE Database SHALL store title, description, property_id, priority, status, created_at, updated_at
5. WHEN a CI is created, THE Database SHALL store ci_id, type, region, sequence, hierarchy_level, parent_id, created_at, updated_at
6. WHEN a property is deleted, THE Database SHALL remove the record (soft delete optional for MVP)
7. WHEN data is queried, THE Database SHALL support filtering, sorting, and pagination

### Requirement 15: Docker Containerization

**User Story:** As a developer, I want to run the entire application stack with a single command, so that I can quickly set up the development environment.

#### Acceptance Criteria

1. WHEN a developer runs `docker compose up`, THE System SHALL start all required containers (FastAPI backend, Vite frontend, PostgreSQL, Redis)
2. WHEN containers start, THE Backend SHALL be accessible at http://localhost:8000
3. WHEN containers start, THE Frontend SHALL be accessible at http://localhost:5173
4. WHEN containers start, THE Database SHALL be initialized with schema and ready for connections
5. WHEN containers start, THE System SHALL create necessary environment variables and configuration
6. WHEN a developer runs `docker compose down`, THE System SHALL stop and remove all containers
7. WHEN containers restart, THE Database SHALL persist data across restarts

### Requirement 16: Project Structure and Code Organization

**User Story:** As a developer, I want a clean, organized project structure, so that I can easily navigate and maintain the codebase.

#### Acceptance Criteria

1. THE Backend SHALL have a clear directory structure: app/, models/, routes/, schemas/, utils/, config/
2. THE Frontend SHALL have a clear directory structure: src/pages/, src/components/, src/hooks/, src/services/, src/types/
3. WHEN the backend starts, THE System SHALL load configuration from environment variables
4. WHEN the frontend builds, THE System SHALL use Vite for fast development and optimized production builds
5. THE Project SHALL include a docker-compose.yml file at the root level
6. THE Project SHALL include .env.example files for both backend and frontend
7. THE Project SHALL include README.md with setup and running instructions

