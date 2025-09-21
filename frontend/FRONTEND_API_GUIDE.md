# Frontend API Integration Guide

## Overview

The frontend now supports both the existing backend and the new microservices architecture. This guide shows how to use the updated API configuration.

## Configuration Modes

### 1. Backend Mode (Traditional)
Uses the existing monolithic backend for all API calls.

```env
VITE_API_MODE=backend
VITE_API_BASE_URL=https://hush-backend-sepia.vercel.app
```

### 2. Microservices Mode
Routes all calls through individual microservices.

```env
VITE_API_MODE=microservices
VITE_GATEWAY_URL=https://hush-backend-sepia.vercel.app
VITE_ADDTOCALENDAR_URL=https://hush-backend-sepia.vercel.app
VITE_MAILERPANDA_URL=https://hush-backend-sepia.vercel.app
VITE_RESEARCH_URL=https://hush-backend-sepia.vercel.app
VITE_FINANCE_URL=https://hush-backend-sepia.vercel.app
VITE_MEMORY_URL=https://hush-backend-sepia.vercel.app
```

### 3. Hybrid Mode (Recommended)
Automatically chooses the best available endpoint.

```env
VITE_API_MODE=hybrid
# Include both backend and microservice URLs
```

## Usage Examples

### Method 1: Direct Endpoint Access (Simple)

```typescript
import { apiConfig } from '../config/api.config';

// Using existing backend endpoints (unchanged)
const backendResponse = await fetch(apiConfig.mailerPanda.execute, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(emailData)
});

// Using new microservice endpoints (explicit)
const microserviceResponse = await fetch(apiConfig.mailerPanda.microservice.execute, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(emailData)
});
```

### Method 2: Smart Endpoint Selection (Recommended)

```typescript
import { getEndpoint } from '../config/api.config';

// Automatically selects the best endpoint based on configuration mode
const endpoint = getEndpoint('mailerPanda', 'execute');
const response = await fetch(endpoint, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(emailData)
});
```

### Method 3: Using Helper Functions

```typescript
import { apiRequest } from '../config/api.config';

// Built-in error handling and response parsing
const result = await apiRequest(getEndpoint('research', 'searchArxiv'), {
  method: 'POST',
  body: JSON.stringify({ query: 'machine learning' })
});

if (result.success) {
  console.log('Research results:', result.data);
} else {
  console.error('API error:', result.error);
}
```

## Available Agents and Endpoints

### AddToCalendar Agent

```typescript
// Backend endpoints (existing)
apiConfig.addToCalendar.execute
apiConfig.addToCalendar.status

// Microservice endpoints (new)
apiConfig.addToCalendar.microservice.execute
apiConfig.addToCalendar.microservice.add_event
apiConfig.addToCalendar.microservice.status

// Smart selection
getEndpoint('addToCalendar', 'execute')
```

### MailerPanda Agent

```typescript
// Backend endpoints (existing)
apiConfig.mailerPanda.execute
apiConfig.mailerPanda.approve
apiConfig.mailerPanda.status
apiConfig.mailerPanda.massEmail
apiConfig.mailerPanda.analyzeExcel

// Microservice endpoints (new)
apiConfig.mailerPanda.microservice.execute
apiConfig.mailerPanda.microservice.upload
apiConfig.mailerPanda.microservice.process
apiConfig.mailerPanda.microservice.analyze
apiConfig.mailerPanda.microservice.status

// Smart selection
getEndpoint('mailerPanda', 'execute')
```

### Research Agent

```typescript
// Backend endpoints (existing)
apiConfig.research.searchArxiv
apiConfig.research.upload
apiConfig.research.summary('paper-id')
apiConfig.research.processSnippet('paper-id')
apiConfig.research.saveNotes
apiConfig.research.status

// Microservice endpoints (new)
apiConfig.research.microservice.searchArxiv
apiConfig.research.microservice.upload
apiConfig.research.microservice.summary('paper-id')
apiConfig.research.microservice.processSnippet('paper-id')
apiConfig.research.microservice.saveNotes
apiConfig.research.microservice.status

// Smart selection
getEndpoint('research', 'searchArxiv')
getEndpoint('research', 'summary', 'paper-123')
```

### Finance Agent

```typescript
// Backend endpoints (existing)
apiConfig.chanduFinance.execute
apiConfig.chanduFinance.status

// Microservice endpoints (new)
apiConfig.chanduFinance.microservice.execute
apiConfig.chanduFinance.microservice.search
apiConfig.chanduFinance.microservice.upload
apiConfig.chanduFinance.microservice.status

// Smart selection
getEndpoint('chanduFinance', 'execute')
```

### Memory Agent

```typescript
// Backend endpoints (existing)
apiConfig.relationshipMemory.execute
apiConfig.relationshipMemory.proactive
apiConfig.relationshipMemory.status
apiConfig.relationshipMemory.chat.start
apiConfig.relationshipMemory.chat.message
apiConfig.relationshipMemory.chat.history('session-id')
apiConfig.relationshipMemory.chat.end('session-id')
apiConfig.relationshipMemory.chat.sessions

// Microservice endpoints (new)
apiConfig.relationshipMemory.microservice.execute
apiConfig.relationshipMemory.microservice.proactive
apiConfig.relationshipMemory.microservice.status
apiConfig.relationshipMemory.microservice.chat.start
apiConfig.relationshipMemory.microservice.chat.message
apiConfig.relationshipMemory.microservice.chat.history('session-id')
apiConfig.relationshipMemory.microservice.chat.end('session-id')
apiConfig.relationshipMemory.microservice.chat.sessions

// Smart selection
getEndpoint('relationshipMemory', 'execute')
```

## Health Monitoring

### Check Backend Health

```typescript
import { checkBackendHealth } from '../config/api.config';

const isBackendHealthy = await checkBackendHealth();
if (!isBackendHealthy) {
  console.warn('Backend is not responding, consider switching to microservices');
}
```

### Check Microservices Health

```typescript
import { checkMicroservicesHealth } from '../config/api.config';

const healthStatus = await checkMicroservicesHealth();
console.log('Service health status:', healthStatus);

// Example output:
// {
//   gateway: true,
//   addtocalendar: true,
//   mailerpanda: false,
//   research: true,
//   finance: true,
//   memory: true
// }
```

### Get Available Services

```typescript
import { getAvailableServices } from '../config/api.config';

const services = getAvailableServices();
console.log('Available services:', services);
// Output: ['backend', 'gateway', 'addtocalendar', 'mailerpanda', 'research', 'finance', 'memory']
```

## Error Handling Best Practices

### Using Built-in Error Handling

```typescript
import { apiRequest } from '../config/api.config';

const result = await apiRequest('/some/endpoint', {
  method: 'POST',
  body: JSON.stringify(data)
});

if (result.success) {
  // Handle success
  console.log('Success:', result.data);
} else {
  // Handle error
  console.error('Error:', result.error);
  // Show user-friendly error message
}
```

### Manual Error Handling

```typescript
try {
  const endpoint = getEndpoint('mailerPanda', 'execute');
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const result = await response.json();
  return result;
} catch (error) {
  console.error('API call failed:', error);
  // Fallback or error handling logic
}
```

## Migration Strategy

### Step 1: Update Environment Variables
Add the new microservice URLs to your `.env` file while keeping existing backend URLs.

### Step 2: Start with Hybrid Mode
Set `VITE_API_MODE=hybrid` to automatically choose the best endpoint.

### Step 3: Test Both Modes
Verify that both backend and microservice endpoints work correctly.

### Step 4: Gradual Migration
Once confident in microservice stability, switch to `VITE_API_MODE=microservices`.

## Component Integration Examples

### React Component with API Calls

```typescript
import React, { useState, useEffect } from 'react';
import { getEndpoint, checkBackendHealth } from '../config/api.config';

export const MailerComponent: React.FC = () => {
  const [isHealthy, setIsHealthy] = useState<boolean>(false);
  const [emailData, setEmailData] = useState<any>(null);

  useEffect(() => {
    // Check health on component mount
    checkBackendHealth().then(setIsHealthy);
  }, []);

  const sendEmail = async (data: any) => {
    try {
      const endpoint = getEndpoint('mailerPanda', 'execute');
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        const result = await response.json();
        setEmailData(result);
      }
    } catch (error) {
      console.error('Email sending failed:', error);
    }
  };

  return (
    <div>
      <div>API Status: {isHealthy ? '✅' : '❌'}</div>
      {/* Your component UI */}
    </div>
  );
};
```

## Environment Setup

### Development
```env
VITE_API_MODE=hybrid
VITE_API_BASE_URL=http://localhost:8000
VITE_GATEWAY_URL=http://localhost:8001
# ... other local URLs
```

### Staging
```env
VITE_API_MODE=hybrid
VITE_API_BASE_URL=https://hush-backend-sepia.vercel.app
VITE_GATEWAY_URL=https://hush-backend-sepia.vercel.app
# ... other staging URLs
```

### Production
```env
VITE_API_MODE=hybrid
VITE_API_BASE_URL=https://hush-backend-sepia.vercel.app
VITE_GATEWAY_URL=https://hush-backend-sepia.vercel.app
# ... other production URLs
```

This configuration provides maximum flexibility while maintaining backward compatibility with existing code.