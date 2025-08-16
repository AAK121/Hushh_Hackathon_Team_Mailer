# ChanduFinance Agent - HushhMCP Financial Valuation Agent

## Overview

The ChanduFinance Agent is a sophisticated financial valuation and analysis agent built following the HushhMCP protocol. It provides comprehensive DCF (Discounted Cash Flow) analysis, sensitivity testing, and investment recommendations for publicly traded companies.

## Features

- **DCF Valuation**: Complete discounted cash flow analysis with enterprise and equity value calculations
- **Three-Statement Financial Modeling**: Automated income statement, balance sheet, and cash flow projections
- **Sensitivity Analysis**: Multi-variable sensitivity testing for WACC and terminal growth rates
- **Investment Recommendations**: AI-powered investment advice based on valuation results
- **Market Analysis**: Current market price comparison with fair value estimates
- **Vault Encryption**: Secure storage of financial data and valuation reports
- **Consent Management**: Full HushhMCP consent token validation

## Agent Capabilities

### Supported Commands

1. **run_valuation** - Complete DCF valuation analysis
2. **get_financials** - Retrieve and structure financial data
3. **run_sensitivity** - Perform sensitivity analysis on valuation models
4. **market_analysis** - Compare market price with intrinsic value

### Required Consent Scopes

- `VAULT_READ_FINANCIALS` - Access to read financial data from user vault
- `VAULT_WRITE_VALUATION` - Permission to store valuation reports
- `VAULT_READ_MARKET_DATA` - Access to market data and pricing information
- `VAULT_WRITE_REPORTS` - Permission to store analysis reports

## Installation and Setup

### Prerequisites

1. Python 3.8+ with required dependencies:
```bash
pip install -r requirements.txt
```

2. HushhMCP framework with consent and vault systems configured

3. Access to financial data APIs (optional - agent includes mock data for testing)

### Agent Registration

The agent is automatically registered when the HushhMCP system starts. Verify registration:

```python
from hushh_mcp.agents.chandufinance.index import ChanduFinanceAgent

agent = ChanduFinanceAgent()
print(f"Agent ID: {agent.agent_id}")
print(f"Version: {agent.version}")
```

## Usage Examples

### Basic DCF Valuation

```python
# Request consent tokens for financial operations
consent_tokens = {
    'VAULT_READ_FINANCIALS': get_user_consent_token('VAULT_READ_FINANCIALS'),
    'VAULT_WRITE_VALUATION': get_user_consent_token('VAULT_WRITE_VALUATION')
}

# Run complete DCF valuation
result = agent.handle(
    user_id="user123",
    token=consent_tokens['VAULT_READ_FINANCIALS'],
    parameters={
        'command': 'run_valuation',
        'ticker': 'AAPL',
        'market_price': 175.00,
        'wacc': 0.09,
        'terminal_growth_rate': 0.025
    }
)

# Process results
if result['status'] == 'success':
    dcf_analysis = result['results']['dcf_analysis']
    recommendation = result['results']['investment_recommendation']
    print(f"Fair Value: ${dcf_analysis['fair_value_per_share']:.2f}")
    print(f"Recommendation: {recommendation['recommendation']}")
```

### Sensitivity Analysis

```python
# Perform sensitivity analysis on key variables
result = agent.handle(
    user_id="user123",
    token=consent_token,
    parameters={
        'command': 'run_sensitivity',
        'ticker': 'MSFT',
        'wacc': 0.08,
        'terminal_growth_rate': 0.025,
        'wacc_range': (0.07, 0.09),      # WACC sensitivity range
        'growth_range': (0.02, 0.03)     # Terminal growth range
    }
)

# Analyze sensitivity matrix
sensitivity_data = result['sensitivity_analysis']['sensitivity_matrix']
for wacc_val, growth_scenarios in sensitivity_data.items():
    print(f"WACC {wacc_val}: {growth_scenarios}")
```

### Financial Data Retrieval

```python
# Get structured financial data
result = agent.handle(
    user_id="user123",
    token=consent_token,
    parameters={
        'command': 'get_financials',
        'ticker': 'GOOGL'
    }
)

financial_data = result['financial_data']
latest_revenue = financial_data['income_statements'][-1]['revenue']
print(f"Latest Revenue: ${latest_revenue:,.0f}")
```

### Market Analysis

```python
# Compare market price with intrinsic value
result = agent.handle(
    user_id="user123",
    token=consent_token,
    parameters={
        'command': 'market_analysis',
        'ticker': 'TSLA',
        'market_price': 250.00
    }
)

analysis = result['market_analysis']
print(f"Current Price: ${analysis['current_price']}")
print(f"Price Assessment: {analysis['price_assessment']}")
```

## API Integration

### HTTP API Endpoint

The agent integrates with the HushhMCP API server:

```bash
# POST request to analyze a stock
curl -X POST http://localhost:8000/api/agents/chandufinance/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <user_consent_token>" \
  -d '{
    "user_id": "user123",
    "parameters": {
      "command": "run_valuation",
      "ticker": "NVDA",
      "market_price": 450.00,
      "wacc": 0.10,
      "terminal_growth_rate": 0.025
    }
  }'
```

### Frontend Integration

```javascript
// JavaScript frontend integration
const analyzeStock = async (ticker, marketPrice) => {
  const response = await fetch('/api/agents/chandufinance/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userConsentToken}`
    },
    body: JSON.stringify({
      user_id: userId,
      parameters: {
        command: 'run_valuation',
        ticker: ticker,
        market_price: marketPrice,
        wacc: 0.09,
        terminal_growth_rate: 0.025
      }
    })
  });
  
  const result = await response.json();
  
  if (result.status === 'success') {
    displayValuationResults(result.results);
  } else {
    handleError(result.error);
  }
};
```

## Data Security and Privacy

### Vault Storage

All financial data and valuation reports are encrypted and stored in the user's vault:

```python
# Data is automatically encrypted before storage
vault_path = agent._get_vault_path(user_id, "valuation_report.enc")
encrypted_data = agent._encrypt_data(valuation_results, consent_tokens)
```

### Consent Validation

Every operation requires valid consent tokens:

```python
# Consent is validated before any data access
validation_result = agent._validate_consent(token)
if not validation_result['valid']:
    return agent._error_response(f"Consent validation failed: {validation_result['reason']}")
```

## Error Handling

The agent provides comprehensive error handling:

```python
# Example error responses
{
    "status": "error",
    "agent_id": "chandufinance",
    "error": "Missing required parameter: ticker",
    "timestamp": "2024-01-20T15:30:00Z"
}

{
    "status": "error", 
    "agent_id": "chandufinance",
    "error": "Token validation failed: Invalid token format",
    "timestamp": "2024-01-20T15:30:00Z"
}
```

## Testing

### Unit Tests

Run the complete test suite:

```bash
# Run all agent tests
pytest tests/unit/test_agents.py::TestChanduFinanceAgent -v

# Run specific test
pytest tests/unit/test_agents.py::TestChanduFinanceAgent::test_financial_agent_run_valuation -v
```

### Integration Tests

```bash
# Run operon tests
pytest tests/test_operons.py::TestFinancialModeling -v

# Run complete integration workflow
pytest tests/test_operons.py::TestFinancialModeling::test_complete_valuation_workflow -v
```

## Configuration

### Environment Variables

```bash
# Optional: Configure financial data sources
export FINANCIAL_DATA_API_KEY="your_api_key_here"
export FINANCIAL_DATA_SOURCE="alpha_vantage"  # or "yahoo_finance"

# Vault configuration
export VAULT_ENCRYPTION_KEY="your_vault_key"
export VAULT_STORAGE_PATH="/path/to/vault/storage"
```

### Agent Configuration

The agent can be configured via the manifest:

```python
# hushh_mcp/agents/chandufinance/manifest.py
manifest = {
    "id": "chandufinance",
    "name": "ChanduFinance Agent", 
    "description": "Financial valuation and DCF analysis agent",
    "version": "1.0.0",
    "capabilities": [
        "dcf_valuation",
        "sensitivity_analysis", 
        "financial_modeling",
        "investment_recommendations"
    ],
    "required_scopes": [
        "VAULT_READ_FINANCIALS",
        "VAULT_WRITE_VALUATION", 
        "VAULT_READ_MARKET_DATA",
        "VAULT_WRITE_REPORTS"
    ]
}
```

## Development

### Adding New Features

1. **New Commands**: Add command handlers to the `handle()` method
2. **New Calculations**: Extend the financial modeling operon
3. **New Data Sources**: Modify `_fetch_financial_data()` method

### Example: Adding P/E Analysis

```python
def _calculate_pe_metrics(self, financial_data, market_price):
    """Calculate P/E ratios and comparisons."""
    latest_eps = financial_data['income_statements'][-1]['earnings_per_share']
    current_pe = market_price / latest_eps
    
    return {
        'current_pe': current_pe,
        'eps': latest_eps,
        'pe_assessment': 'undervalued' if current_pe < 15 else 'overvalued'
    }
```

## Support and Documentation

### Troubleshooting

1. **Token Validation Errors**: Ensure consent tokens have proper scopes
2. **Data Access Issues**: Verify vault permissions and encryption keys
3. **Calculation Errors**: Check input data format and required parameters

### Performance Optimization

- Use caching for repeated financial data requests
- Implement asynchronous data fetching for multiple tickers
- Optimize vault operations for large datasets

## Contributing

When contributing to the ChanduFinance Agent:

1. Follow HushhMCP protocol guidelines
2. Maintain comprehensive test coverage
3. Update documentation for new features
4. Ensure proper consent validation for all operations

## License

This agent is part of the HushhMCP framework and follows the same licensing terms.

---

For more information about the HushhMCP protocol and framework, see the main project documentation.
