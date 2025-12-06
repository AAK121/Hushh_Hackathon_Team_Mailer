# ============================================
# Stage 1: Build React/Vite Application
# ============================================
FROM node:20-alpine as frontend-build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including devDependencies needed for build)
RUN npm ci && npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# ============================================
# Stage 2: Production with Nginx
# ============================================
FROM nginx:alpine as frontend-production

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from build stage
COPY --from=frontend-build /app/dist /usr/share/nginx/html

# Copy .env.production for runtime environment variables
COPY .env.production /usr/share/nginx/html/.env.production

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
