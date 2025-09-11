# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack event management system "Sistema de Gestão de Eventos" with CPF-based authentication and multiple services:
- **Backend**: FastAPI (Python 3.12+) with PostgreSQL/SQLite 
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + Radix UI
- **Authentication**: JWT-based with CPF (Brazilian tax ID) as primary identifier
- **Additional Services**: MEEP analytics (Node.js), Landing page, Mobile app (React Native), PDV mobile

## Critical Notes for Future Sessions

### Authentication System
- **NO GOOGLE AUTH**: The system uses CPF-based authentication exclusively
- Login component: `LoginFormFixed.tsx` (NOT the old `LoginForm.tsx`)
- Test credentials available in `auth_server.py` or backend test files
- Default test admin: CPF "00000000000", password "admin123"

### Import Dependencies Issue
If you encounter "Failed to resolve import" errors for `@/lib/utils` or `@/lib/api`:
1. Check if `frontend/src/lib/utils.ts` and `frontend/src/lib/api.ts` exist
2. If missing, create them using the template versions from other working directories
3. Restart Vite dev server with fresh cache to resolve import errors
4. The `@/` alias maps to `src/` directory in `vite.config.ts`

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
npm run dev                 # Start dev server (port 5173, auto-switches if occupied)
npm run build               # Production build
npm run build-with-types    # Build with TypeScript checking
npm run lint                # Run ESLint
npm run preview             # Preview production build

# If Vite cache issues occur:
rm -rf node_modules/.vite   # Clear Vite cache
npm run dev                 # Restart fresh
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
- **Path Aliases**: `@/` maps to `src/` directory

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
poetry run pytest tests/test_integration_complete.py -v  # Integration tests
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

### Required Environment Variables
- **DATABASE_URL**: PostgreSQL connection string (production)
- **SECRET_KEY**: JWT secret key
- **FRONTEND_URL**: For CORS configuration
- **RAILWAY_ENVIRONMENT**: Indicates Railway deployment

### Optional Environment Variables
- **REDIS_URL**: Redis connection for caching
- **EMAIL_HOST**, **EMAIL_USER**, **EMAIL_PASSWORD**: Email service configuration
- **WHATSAPP_TOKEN**: WhatsApp integration
- **N8N_WEBHOOK_URL**: n8n automation webhook
- **CORS_ORIGINS**: Allowed CORS origins (comma-separated)

### Development Notes
- Development uses SQLite by default (`eventos.db`)
- Frontend dev server proxies `/api` to Railway backend: `https://backend-painel-universal-production.up.railway.app`
- Proxy configuration in `frontend/vite.config.ts`

## Build Optimization
- Frontend uses manual chunk splitting: vendor, radix, charts, router, forms, ui
- TypeScript strict mode enabled
- PWA with offline support via Vite PWA plugin
- Vite optimized dependencies with custom rollup configuration
- Chunk size warning limit: 1000kb

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
cd backend
python test_complete_authenticated.py           # Full API test suite
python debug_login.py                          # Debug authentication issues
python system_diagnostic.py                    # System health check
python performance_validator.py                # Performance testing
python auth_server.py                          # Simple auth server for testing

# API Testing
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"cpf":"00000000000","senha":"admin123"}'
```

### Quick Start Troubleshooting

#### Backend Not Starting
1. Check if port 8000 is already in use
2. Verify Python virtual environment is activated
3. Check `pyproject.toml` dependencies installed via Poetry
4. Try alternative startup scripts: `auth_server.py` or `complete_server.py`

#### Frontend Import Errors
1. Verify `src/lib/utils.ts` and `src/lib/api.ts` exist
2. Check `vite.config.ts` for `@/` path alias configuration  
3. Clear Vite cache and restart dev server
4. Install missing dependencies: `clsx`, `tailwind-merge`, `axios`

#### Authentication Issues
1. Use test credentials: CPF "00000000000", password "admin123"  
2. Verify backend auth server is running on port 8000
3. Check browser network tab for API call responses
4. Ensure `LoginFormFixed.tsx` is being used (not `LoginForm.tsx`)

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
├── e2e/                       # E2E tests
└── tests/                     # Additional test suites
```

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

## Important Notes
- **Authentication**: System uses CPF-based JWT authentication exclusively (NO Google OAuth)
- **Import Resolution**: The `@/lib/utils` and `@/lib/api` files are commonly missing and need to be recreated
- **Vite Dev Server**: May auto-switch ports if 5173 is occupied (check terminal output)
- **CORS**: Currently set to ultra-permissive mode (`*`) for debugging
- **Auto-migrations**: Temporarily disabled in production (line 49 in `main.py`)
- **CPF Primary Key**: Brazilian tax ID used as primary identifier for all user operations
- **WebSockets**: Require proper authentication tokens for connections
- **Build Output**: Frontend builds to `frontend/dist/`, backend serves static files in production
- **Multiple Directories**: Project has multiple similar directory structures - ensure you're working in the correct one