# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm ci --no-audit --no-fund

# Copy source code
COPY . .

# Build arguments (Railway will pass these via environment)
ARG VITE_API_URL
ARG VITE_MEEP_API_URL  
ARG VITE_WS_URL

# Set environment variables for build with defaults
ENV VITE_API_URL=${VITE_API_URL:-https://backend-painel-universal-production.up.railway.app}
ENV VITE_MEEP_API_URL=${VITE_MEEP_API_URL:-https://meep-service-production.up.railway.app}
ENV VITE_WS_URL=${VITE_WS_URL:-wss://backend-painel-universal-production.up.railway.app}
ENV NODE_ENV=production

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port (Railway will set PORT env var)
EXPOSE 3000

# Create startup script that handles dynamic port
RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'PORT=${PORT:-3000}' >> /docker-entrypoint.sh && \
    echo 'sed -i "s/listen 3000/listen $PORT/g" /etc/nginx/nginx.conf' >> /docker-entrypoint.sh && \
    echo 'exec nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-3000}/health || exit 1

# Use custom entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
