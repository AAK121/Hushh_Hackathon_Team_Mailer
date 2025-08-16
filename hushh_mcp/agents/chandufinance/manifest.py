# hushh_mcp/agents/chandufinance/manifest.py

manifest = {
    "id": "chandufinance",
    "name": "Chandu Finance - Financial Valuation Agent",
    "description": "Performs DCF valuation on companies and provides Buy/Hold/Sell recommendations with comprehensive financial analysis.",
    "version": "1.0.0",
    "required_scopes": [
        "vault.read.finance", 
        "vault.write.file",
        "agent.finance.analyze",
        "custom.session.write"
    ],
    "capabilities": [
        "DCF Analysis",
        "Financial Statement Modeling",
        "Market Data Integration",
        "Investment Recommendations",
        "Sensitivity Analysis"
    ],
    "supported_commands": [
        "run_valuation",
        "get_financials", 
        "run_sensitivity",
        "market_analysis"
    ]
}
