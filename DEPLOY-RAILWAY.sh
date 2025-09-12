#!/bin/bash
# Deploy automático para Railway

echo "🚂 Deploying to Railway..."

# Backend
cd paineluniversal/backend
railway up

# Frontend
cd ../frontend
railway up

echo "✅ Deploy completo!"
