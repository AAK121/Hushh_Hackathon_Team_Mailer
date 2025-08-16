# HushhMCP Agents - Quick Reference

## 🚀 Base URL
```
http://127.0.0.1:8001
```

## 🤖 All Agents Summary

| Agent | Endpoint | Purpose | Key Scopes |
|-------|----------|---------|------------|
| **AddToCalendar** | `/agents/addtocalendar/execute` | Email → Calendar events | `vault.read.email`, `vault.write.calendar` |
| **MailerPanda** | `/agents/mailerpanda/execute` | AI email campaigns | `vault.read.email`, `vault.write.email`, `custom.temporary` |
| **ChanduFinance** | `/agents/chandufinance/execute` | Financial analysis & DCF | `vault.read.finance`, `agent.finance.analyze` |
| **Relationship Memory** | `/agents/relationship_memory/execute` | Contact & memory management | `vault.read.contacts`, `vault.read.memory` |

## ⚡ Quick Test Commands

### Get All Agents
```bash
curl http://127.0.0.1:8001/agents
```

### Test ChanduFinance
```javascript
fetch('/agents/chandufinance/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'test_user',
    token: 'HCT:test_token',
    ticker: 'AAPL',
    command: 'run_valuation',
    market_price: 175.50
  })
})
```

### Test Relationship Memory
```javascript
fetch('/agents/relationship_memory/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'test_user',
    tokens: { 'vault.read.contacts': 'HCT:test_token' },
    user_input: 'Add contact John Doe with email john@example.com'
  })
})
```

## 🔑 Required Environment
- Python 3.8+
- HushhMCP consent tokens
- API server running: `python api.py`

## 📖 Full Documentation
See `AGENTS_API_README.md` for complete integration guide with examples, error handling, and best practices.
