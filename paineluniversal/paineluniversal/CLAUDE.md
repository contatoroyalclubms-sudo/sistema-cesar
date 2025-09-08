# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack event management system "Sistema de Gestão de Eventos" with multiple services:
- **Backend**: FastAPI (Python 3.12+) with PostgreSQL/SQLite 
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Additional Services**: MEEP analytics (Node.js), Landing page, Mobile app (React Native), PDV mobile

## Development Commands

### Backend
```bash
cd backend
poetry install                                         # Install dependencies
poetry run uvicorn app.main:app --reload --port 8000   # Start dev server
poetry run pytest --cov=app --cov-report=html -v       # Run tests with coverage
poetry run pytest tests/test_specific.py -v            # Run specific test

# Database setup
poetry run python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Alternative startup
python run_server.py        # Or: python start_backend.py
```

### Frontend  
```bash
cd frontend
npm install                 # Install dependencies
npm run dev                 # Start dev server (port 5173)
npm run build               # Production build
npm run lint                # Run ESLint
npm run preview             # Preview production build
```

### Additional Services
```bash
# MEEP Service
cd meep-service && npm install && npm run dev

# Landing Page  
cd landing-unique && npm install && npm run dev

# Mobile App
cd mobile-app && npm install && npm start

# PDV Mobile
cd pdv-mobile-limpo && npm install && npm start

# Full stack deployment
./deploy-pdv.sh             # Deploy backend + frontend
```

## Architecture

### Backend (`/backend`)
- **Main**: `app/main.py` - FastAPI with WebSocket support, auto-migration system
- **Models**: `app/models.py` - SQLAlchemy ORM models
- **Schemas**: `app/schemas.py` - Pydantic validation schemas
- **Auth**: JWT with CPF-based identification (admin/promoter/cliente roles) in `app/auth.py`, `app/auth_functions.py`
- **Routers**: eventos, usuarios, checkins, pdv, financeiro, gamificacao, whatsapp, n8n, estoque, cashless, kds, mesas, fidelidade, colaboradores, and more
- **Services**: alert, email, receipt, whatsapp, printer, import_export
- **Database**: SQLite (dev) / PostgreSQL (prod) via DATABASE_URL
- **CORS**: Custom `UltimateCORSMiddleware` for maximum compatibility
- **Middleware**: Logging middleware for request/response tracking

### Frontend (`/frontend`)
- **Entry**: `src/main.tsx` → `src/App.tsx`
- **Routing**: React Router v7 with role-based protection
- **UI Components**: 
  - Radix UI primitives (`@radix-ui/*`)
  - Material UI (`@mui/material`)
  - Custom components in `src/components/ui/`
  - Module-specific components in `src/components/{module}/`
- **State**: Context API (`AuthContext`, `ThemeContext`, `EventoContext`)
- **API**: `src/lib/api.ts` - Axios client proxying to Railway backend in dev
- **Key Modules**: Dashboard, Eventos, PDV, Checkin, Estoque, Financeiro, Listas, Ranking, Cashless, KDS, Fidelidade
- **PWA**: Service worker via Vite PWA plugin with offline support
- **Forms**: React Hook Form with Yup/Zod validation

### Key Features
- **CPF Security**: Brazilian tax ID for all user operations
- **Multi-tenant**: Optional empresa (company) association
- **Real-time**: WebSockets for PDV/checkin (`/api/pdv/ws/{evento_id}`)
- **Event Lists**: VIP, FREE, PAGANTE, PROMOTER with flexible pricing
- **Inventory**: Stock control with movements, locations, categories
- **Gamification**: Rankings, badges, achievements for promoters
- **Import/Export**: Bulk operations with validation and templates
- **Cashless System**: Digital wallet and payment processing
- **KDS (Kitchen Display System)**: Real-time order management
- **Printer Integration**: Receipt printing via multiple printer services

## Database Migrations

### PostgreSQL Production
```bash
cd backend
python apply_postgresql_migration.py            # Main migration
python apply_remove_empresa_migration.py        # Remove empresa_id
python make_empresa_optional_migration.py       # Make empresa_id optional
python migrate_to_postgresql.py                 # SQLite to PostgreSQL migration
```

### Auto-migration System
The backend includes an auto-migration system that runs on Railway deployment:
- Detects Railway environment via `RAILWAY_ENVIRONMENT` env var
- Automatically applies pending migrations on startup
- Located in `app/migrations/auto_migrate.py`

## Testing

### Backend
```bash
cd backend
poetry run pytest                               # All tests
poetry run pytest tests/test_eventos.py -v      # Specific test
poetry run pytest --cov=app --cov-report=html   # Coverage report
```

### Frontend
Testing dependencies installed but no test script configured. Jest and Testing Library available for future implementation.

### E2E Testing
```bash
npx playwright test                             # Run Playwright tests
npx playwright test --ui                        # Interactive UI mode
```

## API Reference
- Base: `/api`
- Auth: `/api/auth` (login, register, refresh, verify-token)
- Docs: `/docs` (Swagger), `/redoc` 
- WebSockets: `/api/pdv/ws/{evento_id}`, `/api/checkin/ws/{evento_id}`

## Environment Configuration
- **DATABASE_URL**: PostgreSQL connection string (production)
- **SECRET_KEY**: JWT secret key
- **FRONTEND_URL**: For CORS configuration
- **RAILWAY_ENVIRONMENT**: Indicates Railway deployment
- Development uses SQLite by default (`eventos.db`)
- Frontend proxies `/api` to Railway backend: `https://backend-painel-universal-production.up.railway.app`

## Build Optimization
- Frontend uses manual chunk splitting: vendor, radix, charts, router, forms, ui
- TypeScript strict mode enabled
- PWA with offline support via Vite PWA plugin
- Vite optimized dependencies with custom rollup configuration

## Common Tasks

### Create Admin User
```bash
cd backend
python create_admin_user.py                     # Interactive admin creation
python create_admin_bcrypt.py                   # With bcrypt password hashing
```

### Run Database Migrations
```bash
cd backend
python migrate_to_postgresql.py                 # SQLite → PostgreSQL
python apply_migration.py                        # Apply pending migrations
python migrate_production_railway.py            # Production Railway migration
```

### Deploy to Railway
```bash
./deploy-pdv.sh                                 # Full deployment
./deploy-auto-recovery.sh                       # With auto-recovery
python railway_auto_deploy.py                   # Python deployment script
```

### Debug & Testing Tools
```bash
python test_complete_authenticated.py           # Full API test suite
python debug_login.py                          # Debug authentication issues
python system_diagnostic.py                    # System health check
python performance_validator.py                # Performance testing
```

## Project Structure
```
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry
│   │   ├── models.py          # Database models  
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── auth.py            # Authentication
│   │   ├── database.py        # Database connection
│   │   ├── routers/           # API endpoints (30+ modules)
│   │   ├── services/          # Business logic services
│   │   └── migrations/        # Database migrations
│   ├── tests/                 # Test suite
│   └── pyproject.toml         # Poetry dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components (20+ modules)
│   │   ├── contexts/          # React contexts
│   │   ├── lib/               # Utilities and API client
│   │   ├── types/             # TypeScript definitions
│   │   └── main.tsx          # Entry point
│   ├── vite.config.ts        # Vite configuration
│   └── package.json          # NPM dependencies
├── meep-service/              # Analytics service
├── landing-unique/            # Marketing landing page
├── mobile-app/                # React Native mobile app
├── pdv-mobile-limpo/          # PDV mobile app
└── tests/                     # E2E tests
```

## Important Notes
- CORS is currently set to ultra-permissive mode (`*`) for debugging
- Some modules are temporarily commented in `main.py` to avoid conflicts (estoque, multi_cardapio, permissoes)
- Auto-migrations are temporarily disabled in production (line 49 in `main.py`)
- The system uses CPF (Brazilian tax ID) as primary identifier for all user operations
- WebSocket connections require proper authentication tokens