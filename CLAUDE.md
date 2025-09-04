# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack event management system "Sistema de Gestão de Eventos" with:
- **Backend**: FastAPI (Python 3.12+) with PostgreSQL/SQLite 
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Additional Services**: MEEP analytics (Node.js), Landing page, Mobile app (React Native)

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

# Full stack deployment
./deploy-pdv.sh             # Deploy backend + frontend
```

## Architecture

### Backend (`/backend`)
- **Main**: `app/main.py` - FastAPI with WebSocket support
- **Models**: `app/models.py` - SQLAlchemy ORM models
- **Auth**: JWT with CPF-based identification (admin/promoter/cliente roles)
- **Routers**: eventos, usuarios, checkins, pdv, financeiro, gamificacao, whatsapp, n8n, estoque, import_export
- **Services**: alert, email, receipt, whatsapp, printer
- **Database**: SQLite (dev) / PostgreSQL (prod) via DATABASE_URL
- **CORS**: Custom `UltimateCORSMiddleware` for maximum compatibility

### Frontend (`/frontend`)
- **Entry**: `src/main.tsx` → `src/App.tsx`
- **Routing**: React Router with role-based protection
- **UI**: Radix UI primitives + Tailwind CSS + custom components in `src/components/ui/`
- **State**: Context API (`AuthContext`, `ThemeContext`, `EventoContext`)
- **API**: `src/lib/api.ts` - Axios client proxying to Railway backend in dev
- **Key Modules**: Dashboard, Eventos, PDV, Checkin, Estoque, Financeiro, Listas, Ranking
- **PWA**: Service worker via Vite PWA plugin

### Key Features
- **CPF Security**: Brazilian tax ID for all user operations
- **Multi-tenant**: Optional empresa (company) association
- **Real-time**: WebSockets for PDV/checkin (`/api/pdv/ws/{evento_id}`)
- **Event Lists**: VIP, FREE, PAGANTE, PROMOTER with flexible pricing
- **Inventory**: Stock control with movements, locations, categories
- **Gamification**: Rankings, badges, achievements for promoters
- **Import/Export**: Bulk operations with validation and templates

## Database Migrations

### PostgreSQL Production
```bash
cd backend
python apply_postgresql_migration.py            # Main migration
python apply_remove_empresa_migration.py        # Remove empresa_id
python make_empresa_optional_migration.py       # Make empresa_id optional
```

### SQLite Development
Migrations handled automatically via SQLAlchemy metadata.

## Testing

### Backend
```bash
cd backend
poetry run pytest                               # All tests
poetry run pytest tests/test_eventos.py -v      # Specific test
poetry run pytest --cov=app --cov-report=html   # Coverage report
```

### Frontend
Testing dependencies installed but no test script configured. To add:
```json
"scripts": {
  "test": "jest",
  "test:watch": "jest --watch"
}
```

## API Reference
- Base: `/api`
- Auth: `/api/auth` (login, register, refresh)
- Docs: `/docs` (Swagger), `/redoc`
- WebSockets: `/api/pdv/ws/{evento_id}`, `/api/checkin/ws/{evento_id}`

## Environment Configuration
- **DATABASE_URL**: PostgreSQL connection string (production)
- **SECRET_KEY**: JWT secret key
- **FRONTEND_URL**: For CORS configuration
- Development uses SQLite by default (`eventos.db`)
- Frontend proxies `/api` to Railway backend: `https://backend-painel-universal-production.up.railway.app`

## Build Optimization
- Frontend uses manual chunk splitting: vendor, radix, charts, router, forms, ui
- TypeScript strict mode enabled
- PWA with offline support
- Vite optimized dependencies

## Common Tasks

### Create Admin User
```bash
cd backend
python create_admin_user.py
```

### Run Database Migrations
```bash
cd backend
python migrate_to_postgresql.py                 # SQLite → PostgreSQL
python apply_migration.py                        # Apply pending migrations
```

### Deploy to Railway
```bash
./deploy-pdv.sh                                 # Full deployment
./deploy-auto-recovery.sh                       # With auto-recovery
```

## Project Structure
```
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry
│   │   ├── models.py          # Database models
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── auth.py            # Authentication
│   │   ├── routers/           # API endpoints
│   │   └── services/          # Business logic
│   └── pyproject.toml         # Poetry dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── contexts/          # React contexts
│   │   ├── lib/               # Utilities
│   │   └── main.tsx          # Entry point
│   └── package.json          # NPM dependencies
├── meep-service/              # Analytics service
└── landing-unique/            # Marketing landing
```