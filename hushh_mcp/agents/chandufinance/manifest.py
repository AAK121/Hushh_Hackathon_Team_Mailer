# hushh_mcp/agents/chandufinance/manifest.py

manifest = {
    "id": "chandufinance",
    "name": "Personal Financial Advisor - AI-Powered Wealth Management",
    "description": "Advanced personal financial agent that learns your income, budget, goals, and provides personalized investment advice using LLM-powered analysis. Combines traditional DCF valuation with personal financial planning.",
    "version": "2.0.0",
    "required_scopes": [
        "vault.read.finance", 
        "vault.write.file",
        "vault.read.personal",
        "vault.write.personal", 
        "agent.finance.analyze",
        "agent.llm.analyze",
        "custom.session.write",
        "custom.personality",
        "custom.financial.profile"
    ],
    "capabilities": [
        "Personal Financial Profiling",
        "Income & Budget Analysis", 
        "Goal-Based Investment Planning",
        "Personalized Stock Analysis",
        "LLM-Powered Investment Insights",
        "Personality-Driven Advice",
        "Risk Tolerance Assessment",
        "Portfolio Optimization",
        "Behavioral Finance Coaching",
        "Financial Education & Explanations"
    ],
    "supported_commands": [
        # Personal Finance Management
        "setup_profile",
        "update_income", 
        "set_budget",
        "add_goal",
        "risk_assessment",
        
        # Personalized Analysis  
        "personal_stock_analysis",
        "portfolio_review",
        "goal_progress_check",
        "spending_analysis",
        
        # LLM-Enhanced Features
        "personality_analysis",
        "explain_like_im_new",
        "behavioral_coaching", 
        "investment_education",
        
        # Traditional Analysis (Enhanced)
        "run_valuation",
        "get_financials",
        "run_sensitivity", 
        "market_analysis"
    ],
    "personality_modes": [
        "conservative_saver",
        "growth_investor", 
        "balanced_planner",
        "aggressive_trader",
        "beginner_friendly",
        "expert_level"
    ]
}
