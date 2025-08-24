/**
 * Enhanced Finance API Service for ChanduFinance Agent
 * Integrates with the new comprehensive finance endpoints
 */

const BASE_URL = 'http://localhost:8001';

// Types for requests and responses
export interface FinanceApiResponse {
  status: string;
  data: { [key: string]: any };
  ai_insights?: string;
  recommendations?: string[];
  processing_time: number;
  errors?: string[];
}

export interface TokenRequest {
  user_id: string;
  agent_id: string;
  scope: string;
}

export interface TokenResponse {
  token: string;
  expires_at: string;
  scope: string;
}

// Portfolio Management Types
export interface PortfolioCreateRequest {
  user_id: string;
  token: string;
  portfolio_name: string;
  investment_amount: number;
  risk_tolerance: 'conservative' | 'moderate' | 'aggressive';
  investment_goals: string[];
  time_horizon: number;
  gemini_api_key?: string;
}

export interface PortfolioAnalyzeRequest {
  user_id: string;
  token: string;
  portfolio_id?: string;
  holdings?: Array<{ [key: string]: any }>;
  gemini_api_key?: string;
}

export interface PortfolioRebalanceRequest {
  user_id: string;
  token: string;
  portfolio_id: string;
  gemini_api_key?: string;
}

// Analytics Types
export interface CashflowAnalysisRequest {
  user_id: string;
  token: string;
  period_months?: number;
  include_projections?: boolean;
  gemini_api_key?: string;
}

export interface SpendingAnalysisRequest {
  user_id: string;
  token: string;
  transactions?: Array<{ [key: string]: any }>;
  analysis_type?: 'summary' | 'detailed' | 'predictive';
  gemini_api_key?: string;
}

export interface TaxOptimizationRequest {
  user_id: string;
  token: string;
  annual_income: number;
  investment_income?: number;
  tax_year?: number;
  gemini_api_key?: string;
}

// Market Data Types
export interface StockPriceRequest {
  user_id: string;
  token: string;
  symbols: string[];
  include_analysis?: boolean;
  gemini_api_key?: string;
}

export interface PortfolioValueRequest {
  user_id: string;
  token: string;
  portfolio_id: string;
  gemini_api_key?: string;
}

// Planning Types
export interface RetirementPlanningRequest {
  user_id: string;
  token: string;
  current_age: number;
  retirement_age: number;
  desired_retirement_income: number;
  current_savings: number;
  gemini_api_key?: string;
}

export interface EmergencyFundRequest {
  user_id: string;
  token: string;
  monthly_expenses: number;
  current_emergency_savings: number;
  income_stability?: 'stable' | 'variable' | 'uncertain';
  gemini_api_key?: string;
}

class FinanceApiService {
  private readonly baseUrl: string;
  private readonly defaultGeminiKey: string;

  constructor() {
    this.baseUrl = BASE_URL;
    this.defaultGeminiKey = import.meta.env.VITE_GEMINI_API_KEY || 'AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI';
  }

  // Token Management
  async createToken(user_id: string, scope: string): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/consent/tokens`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id,
          agent_id: 'agent_chandufinance',
          scope
        })
      });

      if (!response.ok) {
        throw new Error(`Token creation failed: ${response.statusText}`);
      }

      const data: TokenResponse = await response.json();
      return data.token;
    } catch (error) {
      console.error('Failed to create token:', error);
      throw error;
    }
  }

  // Core ChanduFinance Agent
  async executeChanduFinance(params: {
    user_id: string;
    token: string;
    command: string;
    [key: string]: any;
  }): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/chandufinance/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...params,
          gemini_api_key: params.gemini_api_key || this.defaultGeminiKey
        })
      });

      if (!response.ok) {
        throw new Error(`ChanduFinance execution failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to execute ChanduFinance:', error);
      throw error;
    }
  }

  // Portfolio Management
  async createPortfolio(request: PortfolioCreateRequest): Promise<FinanceApiResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/chandufinance/portfolio/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          gemini_api_key: request.gemini_api_key || this.defaultGeminiKey
        })
      });

      if (!response.ok) {
        throw new Error(`Portfolio creation failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to create portfolio:', error);
      throw error;
    }
  }

  async analyzePortfolio(request: PortfolioAnalyzeRequest): Promise<FinanceApiResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/chandufinance/portfolio/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          gemini_api_key: request.gemini_api_key || this.defaultGeminiKey
        })
      });

      if (!response.ok) {
        throw new Error(`Portfolio analysis failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to analyze portfolio:', error);
      throw error;
    }
  }

  async rebalancePortfolio(request: PortfolioRebalanceRequest): Promise<FinanceApiResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/chandufinance/portfolio/rebalance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          gemini_api_key: request.gemini_api_key || this.defaultGeminiKey
        })
      });

      if (!response.ok) {
        throw new Error(`Portfolio rebalancing failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to rebalance portfolio:', error);
      throw error;
    }
  }

  // Financial Analytics
  async analyzeCashflow(request: CashflowAnalysisRequest): Promise<FinanceApiResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/chandufinance/analytics/cashflow`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          period_months: request.period_months || 12,
          include_projections: request.include_projections ?? true,
          gemini_api_key: request.gemini_api_key || this.defaultGeminiKey
        })
      });

      if (!response.ok) {
        throw new Error(`Cashflow analysis failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to analyze cashflow:', error);
      throw error;
    }
  }

  async analyzeSpending(request: SpendingAnalysisRequest): Promise<FinanceApiResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/chandufinance/analytics/spending`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          analysis_type: request.analysis_type || 'detailed',
          gemini_api_key: request.gemini_api_key || this.defaultGeminiKey
        })
      });

      if (!response.ok) {
        throw new Error(`Spending analysis failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to analyze spending:', error);
      throw error;
    }
  }

  async optimizeTax(request: TaxOptimizationRequest): Promise<FinanceApiResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/chandufinance/analytics/tax-optimization`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          investment_income: request.investment_income || 0,
          tax_year: request.tax_year || 2024,
          gemini_api_key: request.gemini_api_key || this.defaultGeminiKey
        })
      });

      if (!response.ok) {
        throw new Error(`Tax optimization failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to optimize tax:', error);
      throw error;
    }
  }

  // Market Data
  async getStockPrices(request: StockPriceRequest): Promise<FinanceApiResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/chandufinance/market/stock-price`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          include_analysis: request.include_analysis ?? true,
          gemini_api_key: request.gemini_api_key || this.defaultGeminiKey
        })
      });

      if (!response.ok) {
        throw new Error(`Stock price fetch failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get stock prices:', error);
      throw error;
    }
  }

  async getPortfolioValue(request: PortfolioValueRequest): Promise<FinanceApiResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/chandufinance/market/portfolio-value`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          gemini_api_key: request.gemini_api_key || this.defaultGeminiKey
        })
      });

      if (!response.ok) {
        throw new Error(`Portfolio value fetch failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get portfolio value:', error);
      throw error;
    }
  }

  // Advanced Planning
  async planRetirement(request: RetirementPlanningRequest): Promise<FinanceApiResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/chandufinance/planning/retirement`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          gemini_api_key: request.gemini_api_key || this.defaultGeminiKey
        })
      });

      if (!response.ok) {
        throw new Error(`Retirement planning failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to plan retirement:', error);
      throw error;
    }
  }

  async planEmergencyFund(request: EmergencyFundRequest): Promise<FinanceApiResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/chandufinance/planning/emergency-fund`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          income_stability: request.income_stability || 'stable',
          gemini_api_key: request.gemini_api_key || this.defaultGeminiKey
        })
      });

      if (!response.ok) {
        throw new Error(`Emergency fund planning failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to plan emergency fund:', error);
      throw error;
    }
  }

  // Helper method to create a token for finance operations
  async createChanduFinanceToken(user_id: string): Promise<string> {
    return this.createToken(user_id, 'vault.read.finance');
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const financeApi = new FinanceApiService();
export default financeApi;
