#!/bin/bash
# Script para iniciar o sistema completo

echo "🚀 Iniciando Sistema de Eventos..."

# Backend
echo "Starting Backend..."
cd paineluniversal/backend
poetry run uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Frontend
echo "Starting Frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# MEEP Service
echo "Starting MEEP Service..."
cd ../meep-service
npm start &
MEEP_PID=$!

echo "✅ Sistema iniciado!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "MEEP: http://localhost:3333"

# Aguardar Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID $MEEP_PID" INT
wait
