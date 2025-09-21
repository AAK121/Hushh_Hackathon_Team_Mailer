# Microservices Architecture - HushMCP
## Overview
This directory contains the microservices architecture implementation for HushMCP agents.

### Architecture Components

1. **Gateway API** (`/gateway/`)
   - Main entry point for all requests
   - Routes requests to appropriate agent microservices
   - Handles authentication and load balancing
   - Port: 8000

2. **Agent Microservices** (`/agents/`)
   - **AddToCalendar** (Port 8001): Calendar event extraction and Google Calendar integration
   - **MailerPanda** (Port 8002): Email personalization and mass mailing
   - **Research** (Port 8003): Research paper analysis and academic research
   - **Finance** (Port 8004): Financial analysis and investment operations
   - **Memory** (Port 8005): Relationship memory and proactive interactions

### Local Development Setup

#### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

#### Quick Start
1. Install dependencies for each service:
```bash
# Gateway
cd gateway
pip install -r requirements.txt

# Each agent
cd agents/addtocalendar && pip install -r requirements.txt
cd ../mailerpanda && pip install -r requirements.txt
cd ../research && pip install -r requirements.txt
cd ../finance && pip install -r requirements.txt
cd ../memory && pip install -r requirements.txt
```

2. Configure environment variables:
   - Copy `.env` files in each directory
   - Update API keys and service URLs

3. Start all services:
```bash
# Start each service in separate terminals
cd gateway && python api.py
cd agents/addtocalendar && python api.py
cd agents/mailerpanda && python api.py
cd agents/research && python api.py
cd agents/finance && python api.py
cd agents/memory && python api.py
```

#### Using Docker (Optional)
```bash
# Build and run all services
docker-compose up --build
```

### Production Deployment

#### Service Distribution
- **Vercel**: Gateway + Light agents (AddToCalendar, MailerPanda)
- **Railway/Render**: Heavy agents (Research, Finance, Memory)

#### Environment Configuration
Update service URLs in gateway/.env for production:
```env
ADDTOCALENDAR_SERVICE_URL=https://hush-backend-sepia.vercel.app
MAILERPANDA_SERVICE_URL=https://hush-backend-sepia.vercel.app
RESEARCH_SERVICE_URL=https://hush-backend-sepia.vercel.app
FINANCE_SERVICE_URL=https://hush-backend-sepia.vercel.app
MEMORY_SERVICE_URL=https://hush-backend-sepia.vercel.app
```

### API Documentation
- Gateway API: https://hush-backend-sepia.vercel.app/docs
- Individual agents: http://localhost:800X/docs (where X is the agent port)

### Service Communication
All communication between gateway and agents uses HTTP REST APIs with JSON payloads.

### Security
- Token-based authentication
- Service-to-service authentication
- Encrypted vault storage
- CORS protection

### Monitoring
- Health check endpoints: `/health`
- Service status: Gateway `/health` aggregates all services
- Logging: Configurable per service

### Scaling
- Horizontal scaling: Multiple instances per service
- Load balancing: Gateway handles distribution
- Database: Distributed vault system