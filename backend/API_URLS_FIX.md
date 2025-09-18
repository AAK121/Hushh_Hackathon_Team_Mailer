# API URLs Configuration Fix

## Overview
Fixed hardcoded API URLs in the Research Agent and AddToCalendar Agent to make them configurable through environment variables.

## Changes Made

### 1. Research Agent (`backend/hushh_mcp/agents/research_agent/index.py`)

**Before:**
```python
# Hardcoded URLs
base_url = "http://export.arxiv.org/api/query?"
pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
abs_url = f"https://arxiv.org/abs/{arxiv_id}"
```

**After:**
```python
# Configurable URLs from environment
response = requests.get(f"{ARXIV_API_BASE_URL}?{params}", timeout=API_REQUEST_TIMEOUT)
pdf_url = f"{ARXIV_PDF_BASE_URL}/{arxiv_id}.pdf"
abs_url = f"{ARXIV_ABS_BASE_URL}/{arxiv_id}"
```

### 2. AddToCalendar Agent (`backend/hushh_mcp/agents/addtocalendar/index.py`)

**Before:**
```python
# Hardcoded OAuth URLs
token_uri="https://oauth2.googleapis.com/token"
['https://www.googleapis.com/auth/calendar.events']
```

**After:**
```python
# Configurable OAuth URLs from environment
token_uri=GOOGLE_OAUTH_TOKEN_URI
[GOOGLE_CALENDAR_SCOPE]
```

### 3. Configuration File (`backend/hushh_mcp/config.py`)

Added new environment variable configurations:

```python
# ArXiv API URLs
ARXIV_API_BASE_URL = os.getenv("ARXIV_API_BASE_URL", "http://export.arxiv.org/api/query")
ARXIV_PDF_BASE_URL = os.getenv("ARXIV_PDF_BASE_URL", "https://arxiv.org/pdf")
ARXIV_ABS_BASE_URL = os.getenv("ARXIV_ABS_BASE_URL", "https://arxiv.org/abs")

# Google OAuth URLs
GOOGLE_OAUTH_TOKEN_URI = os.getenv("GOOGLE_OAUTH_TOKEN_URI", "https://oauth2.googleapis.com/token")
GOOGLE_CALENDAR_SCOPE = os.getenv("GOOGLE_CALENDAR_SCOPE", "https://www.googleapis.com/auth/calendar.events")

# API Configuration
API_REQUEST_TIMEOUT = int(os.getenv("API_REQUEST_TIMEOUT", "15"))
ARXIV_MAX_RESULTS = int(os.getenv("ARXIV_MAX_RESULTS", "10"))
```

### 4. Environment Example (`backend/.env.example`)

Added example configuration values:

```bash
# External API URLs (Research Agent)
ARXIV_API_BASE_URL=http://export.arxiv.org/api/query
ARXIV_PDF_BASE_URL=https://arxiv.org/pdf
ARXIV_ABS_BASE_URL=https://arxiv.org/abs
API_REQUEST_TIMEOUT=15
ARXIV_MAX_RESULTS=10

# Google OAuth URLs (AddToCalendar Agent)
GOOGLE_OAUTH_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_CALENDAR_SCOPE=https://www.googleapis.com/auth/calendar.events
```

## Benefits

1. **Flexibility**: API URLs can now be changed without code modifications
2. **Testing**: Easy to point to test/staging environments
3. **Security**: Can use internal/proxy URLs if needed
4. **Maintenance**: Centralized URL management
5. **Deployment**: Different environments can use different APIs

## Usage

### Default Behavior
If no environment variables are set, the system uses the original hardcoded URLs as defaults, ensuring backward compatibility.

### Custom Configuration
Set any of these environment variables in your `.env` file to override defaults:

```bash
# Example: Use different ArXiv mirror
ARXIV_API_BASE_URL=https://arxiv-mirror.example.com/api/query
ARXIV_PDF_BASE_URL=https://arxiv-mirror.example.com/pdf

# Example: Use different timeout for slow networks
API_REQUEST_TIMEOUT=30
ARXIV_MAX_RESULTS=20
```

### For Development/Testing
```bash
# Example: Use test servers
GOOGLE_OAUTH_TOKEN_URI=https://test-oauth2.googleapis.com/token
ARXIV_API_BASE_URL=http://localhost:8080/mock-arxiv/query
```

## Files Modified

1. `backend/hushh_mcp/config.py` - Added URL configurations
2. `backend/hushh_mcp/agents/research_agent/index.py` - Updated to use configurable URLs
3. `backend/hushh_mcp/agents/addtocalendar/index.py` - Updated OAuth URLs
4. `backend/.env.example` - Added example configurations

## Deployment

After this fix, your Vercel deployment will continue to work with the default URLs, but you can now configure them through Vercel's environment variables dashboard if needed.

## Next Steps

Consider adding similar configurability for:
- Other external API endpoints in different agents
- API rate limits and retry configurations
- Custom user-agent strings
- Proxy settings for corporate environments
