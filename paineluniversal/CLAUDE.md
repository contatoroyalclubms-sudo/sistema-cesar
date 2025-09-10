# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sistema Universal v6 - Enterprise event management platform (100-50,000+ participants)
- **Backend**: FastAPI (Python 3.12+) with SQLAlchemy ORM, supports PostgreSQL/SQLite
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + Radix UI + Material UI
- **Authentication**: JWT-based with CPF (Brazilian tax ID) as primary identifier
- **Deployment**: Railway platform with auto-migration system
- **Code Stats**: 103,633 lines across 1,282 files (60,266 functional lines)
- **Completeness**: ~85% complete - production-ready with minor enhancements needed

## Critical Implementation Notes

### Authentication
- **CPF-Only Auth**: No Google OAuth - system uses Brazilian CPF exclusively
- Test credentials: CPF "00000000000", password "admin123"
- Main auth component: `LoginFormFixed.tsx` (NOT `LoginForm.tsx`)
- Roles: admin, promoter, cliente

### Common Issues & Solutions
- **Import errors** (`@/lib/utils`, `@/lib/api`): Check if files exist in `frontend/src/lib/`, recreate if missing
- **Vite cache issues**: Run `rm -rf frontend/node_modules/.vite && npm run dev`
- **Port conflicts**: Frontend auto-switches from 5173 if occupied
- **CORS issues**: Backend uses `UltimateCORSMiddleware` for maximum compatibility

## Development Commands

### Backend
```bash
cd paineluniversal/backend

# Setup
poetry install                                         # Install dependencies
poetry shell                                           # Activate virtual environment

# Development
poetry run uvicorn app.main:app --reload --port 8000   # Start dev server
poetry run uvicorn app.main:app --reload --port 8001   # Alternative port

# Testing
poetry run pytest -v                                   # Run all tests
poetry run pytest tests/test_eventos.py -v             # Run specific test
poetry run pytest --cov=app --cov-report=html          # Coverage report

# Database
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Alternative startup scripts
python auth_server.py                                  # Simple auth server (port 8000)
python simple_server.py                                # Minimal server
python run_server.py                                   # Standard server
```

### Frontend
```bash
cd paineluniversal/frontend

# Setup
npm install                     # Install dependencies

# Development
npm run dev                     # Start dev server (port 5173)
npm run build                   # Production build
npm run build-with-types        # Build with TypeScript checking
npm run lint                    # Run ESLint
npm run preview                 # Preview production build

# Troubleshooting
rm -rf node_modules/.vite       # Clear Vite cache
npm install --force              # Reinstall dependencies
```

### Full Stack
```bash
# Run both frontend and backend
cd paineluniversal/backend && poetry run uvicorn app.main:app --reload --port 8000 &
cd paineluniversal/frontend && npm run dev
```

## Architecture Details

### Backend Structure (`paineluniversal/backend/`)
```
app/
├── main.py              # FastAPI app with WebSocket support, auto-migration
├── models.py            # SQLAlchemy ORM models (30+ entities)
├── schemas.py           # Pydantic validation schemas
├── database.py          # Database connection and session management
├── auth.py              # JWT authentication logic
├── auth_functions.py    # Authentication utilities
├── routers/            # API endpoints (30+ modules)
│   ├── eventos.py      # Event management
│   ├── usuarios.py     # User management
│   ├── pdv.py          # Point of sale
│   ├── checkins.py     # Check-in system
│   ├── produtos.py     # Product catalog
│   ├── estoque.py      # Inventory management
│   ├── financeiro.py   # Financial module
│   └── ...             # 20+ more modules
├── services/           # Business logic
│   ├── alert.py        # Alert system
│   ├── email.py        # Email service
│   ├── printer.py      # Printer integration
│   └── whatsapp.py     # WhatsApp integration
└── migrations/         # Database migrations
    └── auto_migrate.py # Railway auto-migration system
```

### Frontend Structure (`paineluniversal/frontend/`)
```
src/
├── main.tsx            # Entry point
├── App.tsx             # Main app component with routing
├── components/         # React components
│   ├── ui/            # Reusable UI components (Radix/shadcn)
│   ├── auth/          # Authentication components
│   ├── eventos/       # Event management
│   ├── pdv/           # Point of sale
│   ├── dashboard/     # Dashboard components
│   └── ...            # 20+ module directories
├── contexts/          # React contexts
│   ├── AuthContext.tsx
│   ├── EventoContext.tsx
│   └── ThemeContext.tsx
├── lib/               # Utilities
│   ├── api.ts         # Axios API client
│   └── utils.ts       # Helper functions
└── types/             # TypeScript definitions
```

## Key Features & Modules

- **Event Management**: Create, manage events with multiple ticket types (VIP, FREE, PAGANTE)
- **Check-in System**: Real-time WebSocket-based check-in with QR codes
- **PDV (Point of Sale)**: Complete sales system with inventory tracking
- **Inventory Management**: Stock control with movements, locations, categories
- **Financial Module**: Revenue tracking, reports, payment processing
- **Cashless System**: Digital wallet and NFC/QR payment system
- **KDS (Kitchen Display)**: Real-time order management for food service
- **Gamification**: Rankings, badges, achievements for promoters
- **WhatsApp Integration**: Automated messaging and notifications
- **Printer Services**: Receipt and ticket printing
- **Import/Export**: Bulk data operations with CSV/Excel support
- **Multi-tenant**: Optional empresa (company) association

## Database & Migrations

### Development (SQLite)
```bash
# Default database: paineluniversal/backend/eventos.db
cd paineluniversal/backend
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"
```

### Production (PostgreSQL)
```bash
# Migrations for Railway deployment
cd paineluniversal/backend
python apply_postgresql_migration.py            # Main migration
python migrate_to_postgresql.py                 # SQLite to PostgreSQL
python migrate_production_railway.py            # Production migration
python auto_migrate_railway.py                  # Auto-migration script
```

### Environment Variables
```bash
# Required
DATABASE_URL=postgresql://user:pass@host/db     # PostgreSQL connection
SECRET_KEY=your-secret-key                      # JWT signing key
FRONTEND_URL=https://your-frontend.com          # For CORS

# Optional
RAILWAY_ENVIRONMENT=production                  # Triggers auto-migrations
REDIS_URL=redis://...                          # Caching
EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD         # Email service
WHATSAPP_TOKEN=...                             # WhatsApp API
```

## Testing

### Backend Tests
```bash
cd paineluniversal/backend
poetry run pytest -v                           # All tests
poetry run pytest tests/test_eventos.py -v     # Specific module
poetry run pytest --cov=app --cov-report=html  # Coverage report

# Integration testing
python test_complete_authenticated.py          # Full API test suite
python system_diagnostic.py                    # System health check
python performance_validator.py                # Performance testing
```

### E2E Tests
```bash
cd paineluniversal/e2e
npm install
npx playwright test                            # Run all tests
npx playwright test --ui                       # Interactive mode
```

## Deployment

### Railway Deployment
```bash
# Automatic deployment
cd paineluniversal
./deploy-pdv.sh                                # Full deployment script
./deploy-auto-recovery.sh                      # With auto-recovery
python railway_auto_deploy.py                  # Python deployment

# Manual deployment
railway up                                     # Deploy current branch
```

### Docker Deployment
```bash
cd paineluniversal
docker-compose up -d                           # Start all services
```

## API Endpoints

- Base URL: `/api`
- Documentation: `/docs` (Swagger UI), `/redoc` (ReDoc)
- Auth: `/api/auth/login`, `/api/auth/register`, `/api/auth/refresh`
- WebSockets: `/api/pdv/ws/{evento_id}`, `/api/checkin/ws/{evento_id}`

## Common Tasks

### Create Admin User
```bash
cd paineluniversal/backend
python create_admin_user.py                    # Interactive creation
python create_admin_bcrypt.py                  # With bcrypt hashing
```

### Debug Authentication
```bash
cd paineluniversal/backend
python debug_login.py                          # Test login flow
python test_auth_direct.py                     # Direct auth testing

# API test
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"cpf":"00000000000","senha":"admin123"}'
```

### Import/Export Data
```bash
cd paineluniversal/backend
python import_produtos.py exemplo_produtos.csv # Import products
python export_data.py                          # Export all data
```

## Troubleshooting Guide

### Backend Issues
- **Port already in use**: Kill process on port 8000 or use port 8001
- **Poetry not found**: Install with `pip install poetry`
- **Database locked**: Stop other processes accessing eventos.db
- **Import errors**: Run `poetry install` to install dependencies

### Frontend Issues  
- **Module not found**: Run `npm install` in frontend directory
- **@/lib/utils missing**: Create file in `src/lib/utils.ts`
- **Vite port conflict**: Check terminal for actual port used
- **Build errors**: Run `npm run build-with-types` to see TypeScript errors

### Authentication Issues
- **Login fails**: Verify backend is running on expected port
- **CORS errors**: Check FRONTEND_URL environment variable
- **Token invalid**: Clear localStorage and try again
- **CPF validation**: Must be 11 digits, can be formatted or not

## Performance Optimization

- Frontend uses code splitting with manual chunks (vendor, radix, charts, etc.)
- PWA with service worker for offline support
- Vite optimized dependencies with rollup configuration
- Backend uses Redis caching when available
- Database indexes on frequently queried columns
- WebSocket connections for real-time features

## Security Notes

- CPF is primary identifier - ensure proper validation
- JWT tokens expire after 24 hours
- Passwords hashed with bcrypt
- CORS configured per environment
- SQL injection prevention via SQLAlchemy ORM
- XSS protection in React components
- Environment variables for sensitive data

## Known Limitations & TODOs

### Critical (Security/Infrastructure)
- **2FA Authentication**: Not implemented (3 days work)
- **Automated Backup**: PostgreSQL backup not configured (2 days)
- **CI/CD Pipeline**: No GitHub Actions, manual deploy only (3 days)

### Important (Performance/Scale)
- **Message Queue**: RabbitMQ/Kafka not configured, Celery missing (2 days)
- **APM Monitoring**: No New Relic/Datadog, basic metrics only (2 days)
- **Test Coverage**: <50% coverage, missing integration tests (5 days)
- **Advanced Caching**: Redis underutilized, no query cache (2 days)

### Features Not Implemented
- **PIX Integration**: Manual only, no dynamic QR codes (3 days)
- **i18n**: Portuguese only, no localization (3 days)
- **Webhooks**: Not configurable via UI (2 days)
- **Audit Trail**: Basic logging only, no compliance features (2 days)
- **CDN**: Assets served locally, no image optimization (1 day)