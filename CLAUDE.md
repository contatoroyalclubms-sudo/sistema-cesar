# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack event management system called "Sistema de Gestão de Eventos" with the following architecture:

- **Backend**: Python FastAPI application with PostgreSQL database
- **Frontend**: React + TypeScript application using Vite build tool
- **Architecture**: Separate frontend and backend deployments with API communication

## Development Commands

### Backend (Python/FastAPI)
```bash
cd backend
poetry install                    # Install dependencies
poetry run uvicorn app.main:app --reload --port 8000  # Run development server
poetry run pytest --cov=app --cov-report=html -v      # Run tests with coverage
poetry run pytest tests/test_specific.py -v           # Run specific test file
poetry run python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"  # Create database tables

# Alternative startup methods
python run_server.py               # Alternative server startup
python start_backend.py            # Another alternative startup method

# Database migrations (if needed)
python apply_postgresql_migration.py                   # Apply PostgreSQL migrations
python apply_remove_empresa_migration.py               # Remove empresa_id column (if needed)
python make_empresa_optional_migration.py              # Make empresa_id optional
```

### Frontend (React/TypeScript)
```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Run development server (port 5173, proxies to backend:8000 or Railway)
npm run build        # Build for production  
npm run build-with-types  # Build with TypeScript compilation
npm run lint         # Run ESLint
npm run preview      # Preview production build (port 4173)
npm start           # Alias for preview

# Testing - NOTE: No test script currently configured
# npm test would need to be added to package.json
```

### Full Stack Deployment
```bash
./deploy-pdv.sh     # Deploy both backend and frontend with tests
```

## Code Architecture

### Backend Structure (`/backend`)
- **FastAPI Application**: Main app in `app/main.py` with modular routers
- **Database**: PostgreSQL with SQLAlchemy ORM, models in `app/models.py`
- **Authentication**: JWT-based auth with role-based permissions (admin, promoter, cliente)
- **Key Modules**:
  - Event management (`routers/eventos.py`)
  - User management with CPF-based identification (`routers/usuarios.py`)
  - Check-in system (`routers/checkins.py`)
  - Point-of-sale (PDV) system (`routers/pdv.py`)
  - Financial tracking (`routers/financeiro.py`)
  - Gamification system (`routers/gamificacao.py`)
  - WhatsApp integration (`routers/whatsapp.py`)
  - N8N automation integration (`routers/n8n.py`)
- **WebSocket Support**: Real-time features for PDV and check-ins
- **Services**: Alert service, receipt service, WhatsApp service

### Frontend Structure (`/frontend`)
- **React Router**: Role-based route protection and navigation
- **UI Framework**: Custom components using Radix UI primitives with Tailwind CSS  
- **PWA Support**: Progressive Web App with service worker via Vite PWA plugin
- **Key Features**:
  - Dashboard with real-time metrics
  - Event management interface
  - Check-in system (regular and mobile-optimized)
  - Point-of-sale interface  
  - Guest list management
  - Financial reporting
  - Gamification/ranking system
  - Landing page for public access
  - Inventory/Stock management system
- **State Management**: Context API for authentication and theming
- **Build Optimization**: Manual chunk splitting (vendor, radix, charts, router, forms, ui)
- **Development Proxy**: Configured to proxy `/api` requests to Railway production backend (`https://backend-painel-universal-production.up.railway.app`)
- **Testing**: Ready for Jest with React Testing Library (dependencies installed but no test script configured)

### Database Schema
- **User System**: Independent user accounts based on CPF (Brazilian tax ID) for security
- **Multi-tenant Support**: `Empresa` (Company) entity exists but users are NOT required to have company association
- **Event Management**: Different list types (VIP, FREE, PAGANTE, PROMOTER, etc.) with flexible pricing
- **Transaction Tracking**: Complete financial flow with status management
- **PDV System**: Complete point-of-sale with products, comandas, sales, and inventory management
- **Inventory Management**: Stock control with movements, locations, categories, and automated tracking
- **Gamification System**: Achievements, rankings, and badges for promoters
- **Real-time Data**: WebSocket support for live updates in PDV and check-in systems
- **MEEP Integration**: Advanced analytics, equipment monitoring, and AI predictions
- **Import/Export**: Bulk operations with validation, templates, and detailed logging

### Key Business Logic
- **CPF-based Security**: All operations use CPF for user identification
- **Role-based Access**: Three main roles (admin, promoter, cliente) with different permissions  
- **Event Lists**: Multiple list types with different access levels and pricing
- **Real-time Updates**: WebSocket connections for live PDV and check-in updates
- **Financial Tracking**: Complete transaction and cash flow management per event
- **WhatsApp Integration**: Automated messaging for confirmations and updates

## API Structure
- Base URL: `/api`
- Authentication: JWT tokens via `/api/auth`
- WebSocket endpoints: `/api/pdv/ws/{evento_id}` and `/api/checkin/ws/{evento_id}`
- Documentation: Available at `/docs` (Swagger) and `/redoc`

## Development Notes
- **Environment**: Uses SQLite for development, PostgreSQL for production (configured via DATABASE_URL)
- **Frontend Proxy**: Proxies API calls to Railway production backend in development (`https://backend-painel-universal-production.up.railway.app`)
- **CORS**: Ultra-robust CORS implementation with custom `UltimateCORSMiddleware` for maximum compatibility
- **Database Setup**: Migrations handled via direct model metadata creation and dedicated migration scripts
- **Testing**: Backend uses pytest with async support and coverage reporting
- **TypeScript**: Strict configuration with comprehensive type checking
- **PWA**: Progressive Web App capabilities with service worker caching and offline support
- **Authentication**: JWT-based with CPF validation and role-based access control
- **Error Handling**: Global exception handlers with CORS-aware responses and detailed logging
- **Build Process**: Manual chunk splitting and optimized bundle generation for better performance

## Recent Architecture Changes
- **User Independence**: Users can be created without company association (empresa_id removed from required fields)
- **Simplified Permissions**: Role-based access simplified to focus on user type rather than company relationships  
- **Database Flexibility**: Schema supports both standalone users and company-linked users for future extensibility

## Database Migrations
- **Production Setup**: Use `backend/apply_postgresql_migration.py` or `backend/remove_empresa_id_migration.sql` for PostgreSQL
- **Development**: SQLite migrations are handled automatically via SQLAlchemy metadata
- **Available Migration Scripts**:
  - `apply_migration.py` - General migration application
  - `make_empresa_optional_migration.py` - Make empresa_id optional for users
  - `migrate_empresa_id_nullable.py` - Update existing records to allow null empresa_id
  - `recreate_table_migration.py` - Recreate tables with new schema
  - Specific SQL files for PostgreSQL production environments

## Special Features
- **Landing Page Integration**: Includes a separate landing page module in `/landing-unique` for marketing
- **MEEP Service**: Dedicated Node.js microservice in `/meep-service` for analytics and validations
- **Multi-Environment Support**: Different configurations for development (SQLite) and production (PostgreSQL)
- **Real-time Communication**: WebSocket implementation for live updates in PDV and check-in systems  
- **CPF Security**: All user operations are tied to CPF for enhanced security and Brazilian compliance
- **QR Code Generation**: Automatic QR code generation for tickets and check-ins
- **Email Integration**: Email service for notifications and receipts
- **WhatsApp Integration**: Automated WhatsApp messaging capabilities
- **Deployment Scripts**: PowerShell (Windows) and Bash (Unix) scripts for easy deployment

## Additional Services
- **MEEP Service** (`/meep-service`): Node.js analytics service with Redis caching
  ```bash
  cd meep-service
  npm install          # Install dependencies
  npm start           # Start production server
  npm run dev         # Start development server with nodemon
  npm test            # Run Jest tests
  npm test:coverage   # Run tests with coverage
  npm run lint        # Run ESLint
  ```

- **Landing Page** (`/landing-unique`): Standalone React landing page
  ```bash
  cd landing-unique
  npm install          # Install dependencies
  npm run dev         # Run development server
  npm run build       # Build for production
  npm run preview     # Preview production build
  npm run lint        # Run ESLint
  ```