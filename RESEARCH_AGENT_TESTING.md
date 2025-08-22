# Research Agent Manual Testing Guide

## Prerequisites
Make sure the API server is running:
```bash
C:\Python310\python.exe api.py
```
You should see: "Uvicorn running on http://127.0.0.1:8001"

## Test Commands

### 1. Health Check
```bash
curl http://127.0.0.1:8001/health
```
Expected: `{"status": "healthy", "service": "Research Agent API"}`

### 2. List All Agents
```bash
curl http://127.0.0.1:8001/agents
```
Look for "agent_research" in the response

### 3. Research Agent Status
```bash
curl http://127.0.0.1:8001/agents/research/status
```
Expected: Agent details with required scopes

### 4. Test ArXiv Search (with mock tokens)
```bash
curl -X POST http://127.0.0.1:8001/agents/research/search/arxiv \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "consent_tokens": {
      "custom.temporary": "mock_token"
    },
    "query": "machine learning healthcare"
  }'
```
Expected: Error due to invalid tokens (this is normal for testing)

## PowerShell Alternative (Windows)
```powershell
# Health Check
Invoke-RestMethod -Uri http://127.0.0.1:8001/health

# Agents List
Invoke-RestMethod -Uri http://127.0.0.1:8001/agents

# Research Status
Invoke-RestMethod -Uri http://127.0.0.1:8001/agents/research/status
```

## Understanding the Responses

### Success Response Format:
```json
{
  "status": "success",
  "agent_id": "research_agent", 
  "user_id": "test_user_123",
  "session_id": "search_abc123",
  "results": {
    "query": "optimized search terms",
    "papers": [...],
    "total_found": 10
  },
  "processing_time": 2.34
}
```

### Error Response Format:
```json
{
  "status": "error",
  "agent_id": "research_agent",
  "user_id": "test_user_123", 
  "errors": ["Invalid consent token for scope: custom.temporary"],
  "processing_time": 0.12
}
```

## Next Steps for Full Testing

To test the full workflow with real consent tokens:
1. Implement proper consent token generation
2. Upload actual PDF files
3. Test paper summarization
4. Test snippet processing with different instructions
5. Test note saving functionality
