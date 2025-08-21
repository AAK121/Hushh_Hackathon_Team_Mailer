# ChanduFinance - AI-Powered Personal Financial Advisor

## 🌟 Overview

ChanduFinance is a revolutionary AI-powered personal financial advisor that learns your income, budget, goals, and risk tolerance to provide **personalized investment advice**. Unlike traditional financial apps that show generic data, this agent uses LLM capabilities to understand YOUR unique financial situation and provide tailored recommendations.

## 🔗 Frontend-Backend Integration

### 📡 **API Endpoint**
```
POST http://localhost:8002/agents/chandufinance/execute
Content-Type: application/json
```

### 🔑 **Dynamic API Key Support**
ChanduFinance now supports **dynamic API keys** passed through the frontend, eliminating hardcoded credentials:

```javascript
// Frontend API Call Example
const response = await fetch('http://localhost:8002/agents/chandufinance/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_id: "user_123",
    token: "HCT:user_token_here",
    command: "setup_profile",
    
    // Dynamic API keys passed from frontend
    gemini_api_key: userProvidedGeminiKey,  // User's own Gemini API key
    api_keys: {
      custom_service_key: "additional_api_key"
    },
    
    // Command-specific parameters
    full_name: "John Doe",
    age: 30,
    monthly_income: 5000.0,
    monthly_expenses: 3000.0,
    risk_tolerance: "moderate"
  })
});
```

### 🎯 **Request Model**
```typescript
interface ChanduFinanceRequest {
  // Required fields
  user_id: string;
  token: string;  // HushhMCP consent token
  command: string;
  
  // Dynamic API keys (NEW!)
  gemini_api_key?: string;  // Pass user's Gemini API key
  api_keys?: Record<string, string>;  // Additional service keys
  
  // Command-specific parameters
  [key: string]: any;
}
```

### 📋 **Response Model**
```typescript
interface ChanduFinanceResponse {
  status: "success" | "error";
  agent_id: "chandufinance";
  user_id: string;
  message?: string;
  results?: any;
  errors?: string[];
  processing_time: number;
}
```

## 💎 What Makes ChanduFinance Unique

### 🧠 **LLM-Powered Personalization**
- **Learns your financial profile**: Income, expenses, goals, risk tolerance
- **Adapts advice to your situation**: Different recommendations for different people
- **Explains "why" behind every recommendation**: Educational and transparent
- **Personality-driven analysis**: Advice styled to your experience level

### 🏦 **Complete Personal Finance Management**
- **Comprehensive financial profiling**: Set up your income, budget, goals
- **Goal-based investing**: Align investments with your specific objectives  
- **Risk-appropriate recommendations**: Suggestions match your comfort level
- **Position sizing**: Calculate how much YOU should invest based on YOUR budget

### 🎓 **Financial Education & Coaching**
- **Beginner-friendly explanations**: Complex concepts made simple
- **Behavioral finance coaching**: Overcome common investment biases
- **Personalized learning**: Education adapted to your knowledge level
- **Real-time guidance**: Get advice when you need to make decisions

## 🚀 Features & Capabilities

### 📊 **Personal Finance Management Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `setup_profile` | Create your financial profile | Set income, expenses, age, risk tolerance |
| `update_income` | Update your monthly income | New job? Promotion? Update your profile |
| `set_budget` | Set detailed budget categories | Track where your money goes |
| `add_goal` | Add investment goals | House down payment, retirement, vacation |
| `view_profile` | View your complete financial profile | See your current financial snapshot |

### 🔍 **Personalized Investment Analysis**

| Command | Description | What Makes It Personal |
|---------|-------------|----------------------|
| `personal_stock_analysis` | Analyze stocks with YOUR context | Considers your budget, goals, risk tolerance |
| `portfolio_review` | Review your portfolio | Aligned with your financial goals |
| `goal_progress_check` | Check progress toward goals | Track if you're on target |

### 🎓 **AI-Powered Education & Coaching**

| Command | Description | How LLM Helps |
|---------|-------------|---------------|
| `explain_like_im_new` | Beginner-friendly explanations | Adapts complexity to your level |
| `investment_education` | Learn investment concepts | Personalized learning path |
| `behavioral_coaching` | Overcome investment biases | Recognize and avoid common mistakes |

## 📖 Quick Start Guide

### 🏁 **Step 1: Set Up Your Financial Profile**

```python
from hushh_mcp.agents.chandufinance.index import run_agent

result = run_agent(
    user_id="user123",
    token="HCT:your_consent_token",
    parameters={
        'command': 'setup_profile',
        'full_name': 'John Smith',
        'age': 28,
        'occupation': 'Software Engineer',
        'monthly_income': 6000,
        'monthly_expenses': 4000,
        'current_savings': 15000,
        'risk_tolerance': 'moderate',
        'investment_experience': 'beginner',
        'investment_budget': 1500,
        # API keys provided dynamically (not hardcoded)
        'gemini_api_key': 'your_gemini_api_key_here'  # Optional for LLM features
    }
)
```

**Sample Output:**
```
🎉 FINANCIAL PROFILE CREATED!
==================================================
📊 YOUR FINANCIAL SNAPSHOT:
------------------------------
💰 Monthly Income: $6,000.00
💸 Monthly Expenses: $4,000.00
📈 Savings Rate: 33.3%
💼 Investment Budget: $1,500.00
⚖️ Risk Tolerance: moderate
🎓 Experience Level: beginner

💬 PERSONALIZED MESSAGE:
------------------------------
Congratulations on taking control of your finances! With a 33% savings rate, 
you're doing better than most people your age. Your moderate risk tolerance 
and $1,500 monthly investment budget puts you on track to build substantial 
wealth over time. I recommend starting with broad market ETFs like VTI or 
VOO to build your foundation.
```

### 📊 **Step 2: Add Investment Goals**

```python
result = run_agent(
    user_id="user123",
    token="HCT:your_consent_token",
    parameters={
        'command': 'add_goal',
        'goal_name': 'Emergency Fund',
        'target_amount': 20000,
        'target_date': '2026-12-31',
        'priority': 'high'
    }
)
```

### 🔍 **Step 3: Get Personalized Stock Analysis**

```python
result = run_agent(
    user_id="user123",
    token="HCT:your_consent_token",
    parameters={
        'command': 'personal_stock_analysis',
        'ticker': 'AAPL'
    }
)
```

**Sample Output:**
```
📈 PERSONALIZED APPLE (AAPL) ANALYSIS FOR JOHN
=================================================
💰 Current Price: $175.50
📊 Your Personal Context: 28 years old, moderate risk, $1,500/month budget

🎯 POSITION SIZING RECOMMENDATION:
• Suggested allocation: $450 (30% of monthly budget)
• Rationale: Conservative position for large-cap stability
• This represents 0.26% of your total portfolio

🤔 WHY APPLE FITS YOUR PROFILE:
• Strong dividend growth aligns with your moderate risk tolerance
• Large-cap stability suitable for beginners
• Technology exposure good for your age demographic
• Price momentum supports long-term growth goals

⚠️ PERSONALIZED RISKS FOR YOU:
• At $450 investment, represents 1.8 weeks of savings
• Consider dollar-cost averaging over 3 months
• Monitor earnings reports (next one: Jan 31, 2024)

💡 NEXT STEPS TAILORED FOR YOU:
1. Start with $150/month DCA for 3 months
2. Learn about Apple's business model first
3. Consider VTI for broader diversification
4. Review again when you have 6 months experience
```

### 🎓 **Step 4: Get Beginner-Friendly Education**

```python
result = run_agent(
    user_id="user123",
    token="HCT:your_consent_token",
    parameters={
        'command': 'explain_like_im_new',
        'topic': 'compound_interest',
        'complexity': 'beginner'
    }
)
```

## 🔧 API Integration

### 🌐 **FastAPI Endpoints**

The ChanduFinance agent is fully integrated with FastAPI for frontend communication:

```javascript
// Profile Setup
const setupProfile = async (profileData) => {
  const response = await fetch('/agents/chandufinance/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userConsentToken}`
    },
    body: JSON.stringify({
      user_id: userId,
      token: consentToken,
      command: 'setup_profile',
      // API keys provided dynamically (not hardcoded)
      gemini_api_key: userProvidedGeminiKey, // Optional for LLM features
      ...profileData
    })
  });
  
  return await response.json();
};

// Personalized Stock Analysis
const analyzeStock = async (ticker, geminiApiKey = null) => {
  const response = await fetch('/agents/chandufinance/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userConsentToken}`
    },
    body: JSON.stringify({
      user_id: userId,
      token: consentToken,
      command: 'personal_stock_analysis',
      ticker: ticker,
      // API key provided dynamically if user wants LLM features
      ...(geminiApiKey && { gemini_api_key: geminiApiKey })
    })
  });
  
  return await response.json();
};
```

### 📋 **Available API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents/chandufinance/status` | GET | Get agent status and capabilities |
| `/agents/chandufinance/execute` | POST | Execute any ChanduFinance command |

### 📝 **Supported Commands**

- `setup_profile` - Create comprehensive financial profile
- `update_income` - Update monthly income
- `set_budget` - Set detailed budget categories
- `add_goal` - Add financial goals
- `view_profile` - View complete profile
- `personal_stock_analysis` - Get personalized stock analysis
- `portfolio_review` - Review investment portfolio
- `goal_progress_check` - Check goal progress
- `explain_like_im_new` - Beginner explanations
- `investment_education` - Educational content
- `behavioral_coaching` - Behavioral finance guidance

## 🧠 LLM-Powered Features

### 🎭 **Personality-Driven Analysis**

The agent can provide investment advice in the style of famous investors:

```python
result = run_agent(
    user_id="user123",
    token="HCT:your_consent_token",
    parameters={
        'command': 'personal_stock_analysis',
        'ticker': 'BRK.B',
        'style': 'warren_buffett'
    }
)
```

### 🎓 **Adaptive Education**

The agent adjusts explanations based on your experience level:

- **Beginner**: Simple analogies, basic concepts
- **Intermediate**: More detailed analysis, introducing advanced concepts  
- **Advanced**: Complex strategies, nuanced analysis

### 🧠 **Behavioral Coaching**

```python
result = run_agent(
    user_id="user123",
    token="HCT:your_consent_token",
    parameters={
        'command': 'behavioral_coaching',
        'topic': 'fear_of_missing_out'
    }
)
```

## 📊 Sample Workflows

### 🏠 **Home Buyer Workflow**

```python
# 1. Set up profile with home buying goal
run_agent(user_id="user123", token=token, parameters={
    'command': 'setup_profile',
    'monthly_income': 7000,
    'monthly_expenses': 4500,
    'age': 32
})

# 2. Add home down payment goal  
run_agent(user_id="user123", token=token, parameters={
    'command': 'add_goal',
    'goal_name': 'Home Down Payment',
    'target_amount': 80000,
    'target_date': '2027-06-01'
})

# 3. Analyze conservative investments
run_agent(user_id="user123", token=token, parameters={
    'command': 'personal_stock_analysis',
    'ticker': 'VTI'
})

# 4. Get education on real estate investing
run_agent(user_id="user123", token=token, parameters={
    'command': 'investment_education',
    'topic': 'real estate vs stocks'
})
```

### 📈 **Growth Investor Workflow**

```python
# 1. Set up aggressive growth profile
run_agent(user_id="user123", token=token, parameters={
    'command': 'setup_profile',
    'monthly_income': 5000,
    'monthly_expenses': 3000,
    'risk_tolerance': 'aggressive',
    'investment_experience': 'intermediate'
})

# 2. Analyze growth stocks with personal context
run_agent(user_id="user123", token=token, parameters={
    'command': 'personal_stock_analysis',
    'ticker': 'NVDA'
})

# 3. Learn about growth investing strategies
run_agent(user_id="user123", token=token, parameters={
    'command': 'explain_like_im_new',
    'topic': 'growth vs value investing'
})
```

## 🎯 Competitive Advantages

### ❌ **Traditional Financial Apps**
- Show generic data for everyone
- One-size-fits-all recommendations  
- No understanding of your situation
- Static, impersonal advice

### ✅ **ChanduFinance Agent**
- **Learns YOUR specific situation**: Income, goals, risk tolerance
- **Personalizes EVERY recommendation**: Different advice for different people
- **Explains the "why"**: Educational and transparent reasoning
- **Adapts over time**: Learns your preferences and improves advice
- **Conversational interface**: Ask questions in natural language
- **Goal-oriented**: Aligns investments with your life objectives

## 🚀 Advanced Features

### 💡 **Smart Position Sizing**
Automatically calculates how much YOU should invest based on:
- Your available investment budget
- Risk tolerance settings
- Existing portfolio allocation
- Goal timelines

### 🎯 **Goal-Based Recommendations**
- Retirement planning strategies
- House down payment investing
- Education funding approaches
- Emergency fund optimization

### 📚 **Continuous Learning**
- Tracks your investment decisions
- Learns your preferences over time
- Adapts advice style to your feedback
- Improves recommendations based on your goals

## 🎯 Frontend Integration Examples

### 🖥️ **Complete Frontend Implementation**

#### **React Component Example**
```jsx
import React, { useState } from 'react';

const ChanduFinanceWidget = ({ userApiKey, userToken }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);

  const createProfile = async (profileData) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8002/agents/chandufinance/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: "current_user",
          token: userToken,
          command: "setup_profile",
          gemini_api_key: userApiKey,  // User's own API key
          ...profileData
        })
      });
      
      const result = await response.json();
      if (result.status === 'success') {
        setProfile(result.results);
      }
    } catch (error) {
      console.error('Profile creation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPersonalizedAdvice = async (stockSymbol) => {
    const response = await fetch('http://localhost:8002/agents/chandufinance/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: "current_user",
        token: userToken,
        command: "personal_stock_analysis",
        gemini_api_key: userApiKey,
        stock_symbols: [stockSymbol],
        analysis_type: "comprehensive"
      })
    });
    return response.json();
  };

  return (
    <div className="chandufinance-widget">
      {/* Your financial advisor UI here */}
    </div>
  );
};
```

#### **Vue.js Integration**
```vue
<template>
  <div class="financial-dashboard">
    <button @click="setupProfile">Setup Profile</button>
    <button @click="getAdvice">Get Investment Advice</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      userToken: this.$store.state.userToken,
      geminiApiKey: this.$store.state.userApiKeys.gemini
    };
  },
  methods: {
    async setupProfile() {
      const response = await this.$http.post('/agents/chandufinance/execute', {
        user_id: this.userId,
        token: this.userToken,
        command: "setup_profile",
        gemini_api_key: this.geminiApiKey,
        full_name: this.userProfile.name,
        age: this.userProfile.age,
        monthly_income: this.userProfile.income,
        monthly_expenses: this.userProfile.expenses,
        risk_tolerance: this.userProfile.riskLevel
      });
      
      if (response.data.status === 'success') {
        this.$toast.success('Profile created successfully!');
      }
    }
  }
};
</script>
```

### 🔧 **Advanced Integration Patterns**

#### **Error Handling & Retry Logic**
```javascript
class ChanduFinanceAPI {
  constructor(baseURL, defaultApiKey) {
    this.baseURL = baseURL;
    this.defaultApiKey = defaultApiKey;
  }

  async execute(command, params, retries = 3) {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await fetch(`${this.baseURL}/agents/chandufinance/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            command,
            gemini_api_key: this.defaultApiKey,
            ...params
          })
        });

        const result = await response.json();
        
        if (result.status === 'success') {
          return result;
        } else {
          throw new Error(result.errors?.join(', ') || 'Unknown error');
        }
      } catch (error) {
        if (attempt === retries) throw error;
        await this.delay(1000 * attempt); // Exponential backoff
      }
    }
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

#### **Real-time Updates with WebSocket**
```javascript
// WebSocket integration for real-time financial updates
const ws = new WebSocket('ws://localhost:8002/ws/chandufinance');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  if (update.type === 'portfolio_update') {
    updatePortfolioDisplay(update.data);
  }
};

// Request portfolio analysis with real-time updates
const requestPortfolioAnalysis = async () => {
  await fetch('http://localhost:8002/agents/chandufinance/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: currentUser.id,
      token: userToken,
      command: "portfolio_review",
      gemini_api_key: userApiKey,
      enable_realtime: true,
      websocket_id: ws.id
    })
  });
};
```

### 🔐 **Security Best Practices**

#### **Secure API Key Management**
```javascript
// ❌ DON'T: Store API keys in frontend code
const BAD_EXAMPLE = {
  gemini_api_key: "AIzaSyC..." // Never do this!
};

// ✅ DO: Get API keys from secure user session
const secureApiCall = async () => {
  // Get API key from authenticated user session
  const userApiKey = await getUserApiKey(); // From secure backend
  
  return fetch('/agents/chandufinance/execute', {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userJwtToken}`
    },
    body: JSON.stringify({
      user_id: currentUser.id,
      token: hushhToken,
      command: "view_profile",
      gemini_api_key: userApiKey  // Securely passed
    })
  });
};
```

#### **Token Validation**
```javascript
const validateAndExecute = async (command, params) => {
  // Validate token before making request
  const tokenValid = await validateHushhToken(userToken);
  if (!tokenValid) {
    throw new Error('Invalid or expired token');
  }

  return fetch('/agents/chandufinance/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: currentUser.id,
      token: userToken,
      command,
      gemini_api_key: await getSecureApiKey(),
      ...params
    })
  });
};
```

## 🔒 Security & Privacy

### 🛡️ **HushhMCP Compliance**
- All personal financial data encrypted in vault storage
- Consent token validation for every operation
- Scope-based permission system
- No data sharing without explicit consent

### 🔐 **Data Protection**
- End-to-end encryption for sensitive financial information
- Secure token-based authentication
- Personal data never leaves your control
- GDPR-compliant privacy practices

## 📞 Support & Documentation

### 🆘 **Getting Help**
- Check error messages for specific guidance
- Verify API token configuration
- Review command parameters and formats

### 🔍 **Troubleshooting**
```python
# Test agent loading
from hushh_mcp.agents.chandufinance.index import PersonalFinancialAgent
print('✅ Agent loaded successfully')

# Test API connection  
import requests
response = requests.get('http://localhost:8002/agents/chandufinance/status')
print('✅ API connection successful' if response.status_code == 200 else '❌ API connection failed')
```

## 🎯 Success Metrics

### 📊 **User Engagement**
- Time spent learning through the agent
- Number of personalized analyses requested
- Goal completion rates

### 💡 **Educational Impact**  
- User confidence in financial decisions
- Investment knowledge improvement
- Reduced emotional investing mistakes

### 🎯 **Personalization Effectiveness**
- Advice relevance scores
- User satisfaction with recommendations
- Adoption of suggested strategies

## 🚧 Future Enhancements

### 🔮 **Planned Features**
- Real-time portfolio tracking
- Automated rebalancing suggestions
- Tax optimization strategies
- Integration with banking/brokerage APIs
- Social investing features (learn from others with similar profiles)

### 🧠 **Advanced AI Features**
- Predictive financial modeling
- Market sentiment analysis
- Economic cycle awareness
- Multi-scenario planning

---

## 💎 **The Revolution: Personal Finance Meets AI**

ChanduFinance isn't just another financial calculator - it's your **personal financial advisor** that:

- **Knows your situation**: Income, goals, fears, dreams
- **Speaks your language**: Explanations that match your knowledge level  
- **Grows with you**: Learns and adapts as your situation changes
- **Educates while advising**: Makes you a better investor
- **Protects your privacy**: All data encrypted in your personal vault

**Experience the future of personal finance - where AI doesn't replace human judgment, but enhances it with personalized wisdom.**

