# EmergentIntelliTest Codebase Baseline

## Project Overview
EmergentIntelliTest is an AI-powered test automation platform designed to help teams create, manage, and execute automated tests using artificial intelligence.

## Technology Stack
- **Backend**: FastAPI (Python 3.8+), SQLAlchemy ORM, PostgreSQL, Redis, Celery, OpenAI API
- **Frontend**: Next.js (React) with TypeScript, React Query, Chakra UI, React Hook Form
- **Database**: PostgreSQL (Supabase)
- **Authentication**: JWT
- **Infrastructure**: Docker, Docker Compose

## Directory Structure

```
.
├── backend/
│   ├── app/
│   │   ├── ai_service.py          # AI service implementation
│   │   ├── main.py                # FastAPI application entry point
│   │   ├── api/                   # API routes
│   │   │   └── v1/
│   │   │       └── routes/        # API route handlers
│   │   ├── auth/                  # Authentication modules
│   │   ├── core/                  # Core application configuration
│   │   ├── db/                    # Database session management
│   │   ├── mcp/                   # MCP (Model Coordination Protocol) components
│   │   ├── models/                # Database models
│   │   ├── schemas/               # Pydantic schemas
│   │   ├── services/              # Business logic services
│   │   └── websocket/             # WebSocket handlers
│   ├── database/                  # Database management
│   └── scripts/                   # Utility scripts
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── pages/                 # Page components
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── services/              # API service clients
│   │   └── utils/                 # Utility functions
│   └── public/                    # Static assets
└── docs/                          # Documentation
```

## Key Components

### Backend Components

1. **Main Application** (`backend/app/main.py`)
   - FastAPI application setup with lifespan management
   - Middleware configuration including CORS
   - API route registration
   - Database initialization and table creation
   - WebSocket management
   - Error handling and logging

2. **Database Layer** (`backend/app/db/`)
   - Session management for both sync and async operations
   - Database engine configuration with PgBouncer compatibility
   - Connection pooling and error handling
   - Test user creation for development

3. **Authentication** (`backend/app/auth/`)
   - User authentication and authorization
   - JWT token management
   - Password hashing and verification

4. **API Routes** (`backend/app/api/v1/routes/`)
   - User management endpoints
   - Project management endpoints
   - Test case management endpoints
   - Test plan management endpoints
   - AI service integration endpoints

5. **AI Service** (`backend/app/ai_service.py`)
   - OpenAI API integration
   - Test case generation using AI
   - Natural language processing for test creation
   - Test failure debugging and analysis
   - Test case prioritization

6. **Website Test Generator** (`backend/app/mcp/website_test_generator.py`)
   - Website analysis and test case generation
   - Form detection and validation
   - Navigation element identification
   - Page type classification

7. **Database Models** (`backend/app/models/db_models.py`)
   - User model
   - Project model
   - Test case model
   - Test plan model
   - Test execution model
   - Test steps model
   - Comments model
   - Teams and environments models

8. **MCP Components** (`backend/app/mcp/`)
   - Website test case generator
   - Test automation protocols

### Frontend Components

1. **Pages** (`frontend/src/pages/`)
   - Dashboard
   - Project management
   - Test case management
   - AI test generation interface
   - User authentication pages

2. **Components** (`frontend/src/components/`)
   - UI components for test management
   - Forms for test case creation
   - Navigation components
   - Data visualization components

3. **Services** (`frontend/src/services/`)
   - API client implementations
   - Authentication service
   - WebSocket connections

## Database Schema

### Core Tables
1. **Users** - User accounts and authentication
   - id (String, primary key)
   - email (String, unique)
   - full_name (String)
   - hashed_password (String)
   - role (String, default: "tester")
   - is_active (Boolean, default: True)
   - created_at (DateTime)
   - updated_at (DateTime)

2. **Projects** - Test projects and organization
   - id (String, primary key)
   - name (String)
   - description (Text)
   - created_by (ForeignKey to Users)
   - team_id (ForeignKey to Teams)
   - is_active (Boolean, default: True)
   - created_at (DateTime)
   - updated_at (DateTime)

3. **TestCases** - Individual test cases
   - id (String, primary key)
   - title (String)
   - description (Text)
   - project_id (ForeignKey to Projects)
   - test_type (Enum: functional, api, visual, performance, security, integration, unit)
   - priority (Enum: low, medium, high, critical)
   - status (Enum: draft, active, inactive, archived)
   - expected_result (Text)
   - created_by (ForeignKey to Users)
   - assigned_to (ForeignKey to Users)
   - tags (JSON)
   - ai_generated (Boolean)
   - self_healing_enabled (Boolean)
   - prerequisites (Text)
   - test_data (JSON)
   - automation_config (JSON)
   - created_at (DateTime)
   - updated_at (DateTime)

4. **TestSteps** - Individual steps within test cases
   - id (String, primary key)
   - test_case_id (ForeignKey to TestCases)
   - step_number (Integer)
   - description (Text)
   - expected_result (Text)
   - actual_result (Text)
   - status (String)
   - created_at (DateTime)
   - updated_at (DateTime)

5. **TestPlans** - Collections of test cases
   - id (String, primary key)
   - name (String)
   - description (Text)
   - project_id (ForeignKey to Projects)
   - created_by (ForeignKey to Users)
   - status (Enum: draft, active, inactive, archived)
   - scheduled_start (DateTime)
   - scheduled_end (DateTime)
   - created_at (DateTime)
   - updated_at (DateTime)

6. **TestExecutions** - Test execution records
   - id (String, primary key)
   - test_case_id (ForeignKey to TestCases)
   - test_plan_id (ForeignKey to TestPlans)
   - executed_by (ForeignKey to Users)
   - environment_id (ForeignKey to Environments)
   - status (Enum: pending, running, completed, failed, cancelled)
   - started_at (DateTime)
   - completed_at (DateTime)
   - duration (Integer)
   - result (JSON)
   - logs (Text)
   - screenshots (JSON)
   - error_message (Text)
   - ai_analysis (JSON)
   - created_at (DateTime)
   - updated_at (DateTime)

7. **Comments** - Comments on test cases
   - id (String, primary key)
   - test_case_id (ForeignKey to TestCases)
   - user_id (ForeignKey to Users)
   - content (Text)
   - created_at (DateTime)
   - updated_at (DateTime)

## Configuration Files

### Environment Variables (`.env`)
- Database connection strings (both sync and async)
- JWT secret key
- OpenAI API key
- Server configuration

### Application Configuration
- `backend/app/core/config.py` - Application settings
- `backend/app/core/security.py` - Security utilities

## Deployment Configuration

### Docker
- `Dockerfile` - Application containerization
- `docker-compose.yml` - Multi-container setup
- `nginx/` - Reverse proxy configuration

## Key Features

1. **AI-Powered Test Generation**
   - Natural language test case creation
   - Automated test case suggestions
   - Website test case generation
   - Test failure debugging and analysis

2. **Test Management**
   - Hierarchical project organization
   - Test case version control
   - Test plan creation and execution
   - Test step management

3. **Collaboration**
   - Team-based access control
   - Activity logging
   - Commenting system

4. **Execution & Reporting**
   - Parallel test execution
   - Real-time reporting
   - Test result analytics
   - AI-powered test analysis

5. **Website Analysis**
   - Automatic website crawling and analysis
   - Form detection and validation
   - Navigation element identification
   - Page type classification

## Security Considerations

1. **Authentication**
   - JWT-based authentication
   - Password hashing with bcrypt
   - Role-based access control

2. **Data Protection**
   - Environment variable management
   - Secure database connections
   - Input validation and sanitization

## Performance Optimizations

1. **Database**
   - Connection pooling
   - Query optimization
   - Indexing strategies

2. **Caching**
   - Redis for session storage
   - API response caching

3. **Async Operations**
   - Asynchronous database operations
   - Background task processing with Celery

## Testing

1. **Backend Testing**
   - Unit tests for API endpoints
   - Integration tests for database operations
   - AI service testing

2. **Frontend Testing**
   - Component testing with Jest
   - End-to-end testing

## Known Issues & Resolutions

1. **PgBouncer Compatibility**
   - Issue: Prepared statement conflicts with PgBouncer
   - Resolution: Set `statement_cache_size=0` in async engine configuration

2. **Database Connection Management**
   - Issue: Connection pooling with async operations
   - Resolution: Proper session management with rollback/commit patterns

3. **Authentication Integration**
   - Issue: Frontend-backend authentication flow
   - Resolution: JWT token handling and refresh mechanisms

## Best Practices Implemented

1. **Code Organization**
   - Modular architecture with clear separation of concerns
   - Consistent naming conventions
   - Comprehensive error handling

2. **Database Management**
   - Proper transaction handling
   - Connection lifecycle management
   - Schema migration strategies

3. **API Design**
   - RESTful API principles
   - Consistent response formats
   - Proper HTTP status codes

4. **Security**
   - Input validation
   - Secure password handling
   - CORS configuration

## Dependencies

### Backend
- FastAPI - Web framework
- SQLAlchemy - ORM
- PostgreSQL - Database
- Redis - Caching
- Celery - Task queue
- OpenAI - AI services
- PyJWT - JWT handling
- bcrypt - Password hashing

### Frontend
- Next.js - React framework
- React Query - Server state management
- Chakra UI - Component library
- React Hook Form - Form handling
- Axios - HTTP client

This baseline document provides a comprehensive overview of the EmergentIntelliTest codebase as of the current state, capturing the key components, architecture, and implementation details.