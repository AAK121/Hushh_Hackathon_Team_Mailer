import React, { useState, useEffect } from 'react';
import { financeApi } from '../services/financeApi';

interface Transaction {
  id: string;
  amount: number;
  description: string;
  category: string;
  date: string;
  type: 'income' | 'expense';
}

interface Budget {
  id: string;
  category: string;
  allocated: number;
  spent: number;
  period: 'monthly' | 'yearly';
}

interface FinancialGoal {
  id: string;
  title: string;
  targetAmount: number;
  currentAmount: number;
  deadline: string;
  priority: 'high' | 'medium' | 'low';
}

interface FinanceAgentProps {
  onBack: () => void;
  onSendToHITL?: (message: string, context: any) => void;
}

const FinanceAgent: React.FC<FinanceAgentProps> = ({ onBack, onSendToHITL }) => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'portfolio' | 'analytics' | 'market' | 'planning' | 'insights'>('dashboard');
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [goals, setGoals] = useState<FinancialGoal[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Enhanced state for new API features
  const [financialProfile, setFinancialProfile] = useState<any>(null);
  const [portfolios, setPortfolios] = useState<any[]>([]);
  const [stockPrices, setStockPrices] = useState<any>({});
  const [cashflowAnalysis, setCashflowAnalysis] = useState<any>(null);
  const [spendingAnalysis, setSpendingAnalysis] = useState<any>(null);
  const [retirementPlan, setRetirementPlan] = useState<any>(null);
  const [emergencyFund, setEmergencyFund] = useState<any>(null);
  const [taxOptimization, setTaxOptimization] = useState<any>(null);
  const [aiInsights, setAiInsights] = useState<string>('');
  const [recommendations, setRecommendations] = useState<string[]>([]);
  
  // Current user state
  const [currentUserId] = useState('demo_user');
  const [userToken, setUserToken] = useState<string>('');
  
  // Form states
  const [showAddTransaction, setShowAddTransaction] = useState(false);
  const [showAddBudget, setShowAddBudget] = useState(false);
  const [showCreatePortfolio, setShowCreatePortfolio] = useState(false);
  
  const [newTransaction, setNewTransaction] = useState({
    amount: '',
    description: '',
    category: '',
    type: 'expense' as 'income' | 'expense'
  });

  const [newBudget, setNewBudget] = useState({
    category: '',
    allocated: '',
    period: 'monthly' as 'monthly' | 'yearly'
  });

  const [newPortfolio, setNewPortfolio] = useState({
    portfolio_name: '',
    investment_amount: '',
    risk_tolerance: 'moderate' as 'conservative' | 'moderate' | 'aggressive',
    investment_goals: [] as string[],
    time_horizon: ''
  });

  useEffect(() => {
    initializeFinanceSystem();
  }, []);

  const initializeFinanceSystem = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Check API health
      const isHealthy = await financeApi.healthCheck();
      if (!isHealthy) {
        throw new Error('Finance API is not available');
      }
      
      // Create token for finance operations
      const token = await financeApi.createChanduFinanceToken(currentUserId);
      setUserToken(token);
      
      // Setup user profile
      await setupUserProfile(token);
      
      // Load mock data for demo
      loadFinancialData();
      
    } catch (error) {
      console.error('Failed to initialize finance system:', error);
      setError(error instanceof Error ? error.message : 'Failed to initialize finance system');
      
      // Load mock data as fallback
      loadFinancialData();
      
    } finally {
      setLoading(false);
    }
  };

  const setupUserProfile = async (token: string) => {
    try {
      const profileResponse = await financeApi.executeChanduFinance({
        user_id: currentUserId,
        token: token,
        command: 'setup_profile',
        full_name: 'Demo User',
        age: 30,
        occupation: 'Software Developer',
        monthly_income: 5000,
        monthly_expenses: 3200,
        current_savings: 15000,
        current_debt: 5000,
        investment_budget: 1500,
        risk_tolerance: 'moderate',
        investment_experience: 'beginner'
      });
      
      if (profileResponse.status === 'success') {
        setFinancialProfile(profileResponse.profile_summary);
        if (profileResponse.ai_insights) {
          setAiInsights(profileResponse.ai_insights);
        }
        if (profileResponse.recommendations) {
          setRecommendations(profileResponse.recommendations);
        }
      }
    } catch (error) {
      console.error('Failed to setup user profile:', error);
    }
  };

  const loadFinancialData = () => {
    // Mock data - in production, this would come from an API
    const mockTransactions: Transaction[] = [
      {
        id: '1',
        amount: 3200,
        description: 'Salary',
        category: 'Income',
        date: '2025-01-15',
        type: 'income'
      },
      {
        id: '2',
        amount: 1200,
        description: 'Rent Payment',
        category: 'Housing',
        date: '2025-01-10',
        type: 'expense'
      },
      {
        id: '3',
        amount: 250,
        description: 'Groceries',
        category: 'Food',
        date: '2025-01-12',
        type: 'expense'
      },
      {
        id: '4',
        amount: 100,
        description: 'Electricity Bill',
        category: 'Utilities',
        date: '2025-01-08',
        type: 'expense'
      }
    ];

    const mockBudgets: Budget[] = [
      {
        id: '1',
        category: 'Food',
        allocated: 500,
        spent: 250,
        period: 'monthly'
      },
      {
        id: '2',
        category: 'Entertainment',
        allocated: 200,
        spent: 75,
        period: 'monthly'
      },
      {
        id: '3',
        category: 'Transportation',
        allocated: 300,
        spent: 120,
        period: 'monthly'
      }
    ];

    const mockGoals: FinancialGoal[] = [
      {
        id: '1',
        title: 'Emergency Fund',
        targetAmount: 15000,
        currentAmount: 8500,
        deadline: '2025-12-31',
        priority: 'high'
      },
      {
        id: '2',
        title: 'New Car',
        targetAmount: 25000,
        currentAmount: 5000,
        deadline: '2026-06-30',
        priority: 'medium'
      },
      {
        id: '3',
        title: 'Vacation Fund',
        targetAmount: 3000,
        currentAmount: 1200,
        deadline: '2025-08-01',
        priority: 'low'
      }
    ];

    setTransactions(mockTransactions);
    setBudgets(mockBudgets);
    setGoals(mockGoals);
  };

  // Portfolio Management Functions
  const createPortfolio = async () => {
    if (!userToken || !newPortfolio.portfolio_name || !newPortfolio.investment_amount) {
      setError('Please fill in all required portfolio fields');
      return;
    }

    try {
      setLoading(true);
      const response = await financeApi.createPortfolio({
        user_id: currentUserId,
        token: userToken,
        portfolio_name: newPortfolio.portfolio_name,
        investment_amount: parseFloat(newPortfolio.investment_amount),
        risk_tolerance: newPortfolio.risk_tolerance,
        investment_goals: newPortfolio.investment_goals,
        time_horizon: parseInt(newPortfolio.time_horizon)
      });
      
      if (response.status === 'success') {
        setPortfolios(prev => [...prev, response.data]);
        setAiInsights(response.ai_insights || '');
        setRecommendations(response.recommendations || []);
        setShowCreatePortfolio(false);
        setNewPortfolio({
          portfolio_name: '',
          investment_amount: '',
          risk_tolerance: 'moderate',
          investment_goals: [],
          time_horizon: ''
        });
      }
    } catch (error) {
      setError('Failed to create portfolio');
      console.error('Portfolio creation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzePortfolio = async (portfolioId: string) => {
    if (!userToken) return;

    try {
      setLoading(true);
      const response = await financeApi.analyzePortfolio({
        user_id: currentUserId,
        token: userToken,
        portfolio_id: portfolioId
      });
      
      if (response.status === 'success') {
        setAiInsights(response.ai_insights || '');
        setRecommendations(response.recommendations || []);
      }
    } catch (error) {
      setError('Failed to analyze portfolio');
      console.error('Portfolio analysis error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Analytics Functions
  const analyzeCashflow = async () => {
    if (!userToken) return;

    try {
      setLoading(true);
      const response = await financeApi.analyzeCashflow({
        user_id: currentUserId,
        token: userToken,
        period_months: 12,
        include_projections: true
      });
      
      if (response.status === 'success') {
        setCashflowAnalysis(response.data);
        setAiInsights(response.ai_insights || '');
        setRecommendations(response.recommendations || []);
      }
    } catch (error) {
      setError('Failed to analyze cashflow');
      console.error('Cashflow analysis error:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeSpending = async () => {
    if (!userToken) return;

    try {
      setLoading(true);
      const response = await financeApi.analyzeSpending({
        user_id: currentUserId,
        token: userToken,
        transactions: transactions.map(t => ({
          amount: t.amount,
          description: t.description,
          category: t.category,
          date: t.date,
          type: t.type
        })),
        analysis_type: 'detailed'
      });
      
      if (response.status === 'success') {
        setSpendingAnalysis(response.data);
        setAiInsights(response.ai_insights || '');
        setRecommendations(response.recommendations || []);
      }
    } catch (error) {
      setError('Failed to analyze spending');
      console.error('Spending analysis error:', error);
    } finally {
      setLoading(false);
    }
  };

  const optimizeTax = async () => {
    if (!userToken) return;

    try {
      setLoading(true);
      const response = await financeApi.optimizeTax({
        user_id: currentUserId,
        token: userToken,
        annual_income: 60000,
        investment_income: 5000,
        tax_year: 2024
      });
      
      if (response.status === 'success') {
        setTaxOptimization(response.data);
        setAiInsights(response.ai_insights || '');
        setRecommendations(response.recommendations || []);
      }
    } catch (error) {
      setError('Failed to optimize tax');
      console.error('Tax optimization error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Market Data Functions
  const getStockPrices = async () => {
    if (!userToken) return;

    try {
      setLoading(true);
      const response = await financeApi.getStockPrices({
        user_id: currentUserId,
        token: userToken,
        symbols: ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA'],
        include_analysis: true
      });
      
      if (response.status === 'success') {
        setStockPrices(response.data.prices || {});
        setAiInsights(response.ai_insights || '');
        setRecommendations(response.recommendations || []);
      }
    } catch (error) {
      setError('Failed to get stock prices');
      console.error('Stock prices error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Planning Functions
  const planRetirement = async () => {
    if (!userToken) return;

    try {
      setLoading(true);
      const response = await financeApi.planRetirement({
        user_id: currentUserId,
        token: userToken,
        current_age: 30,
        retirement_age: 65,
        desired_retirement_income: 6000,
        current_savings: 15000
      });
      
      if (response.status === 'success') {
        setRetirementPlan(response.data);
        setAiInsights(response.ai_insights || '');
        setRecommendations(response.recommendations || []);
      }
    } catch (error) {
      setError('Failed to plan retirement');
      console.error('Retirement planning error:', error);
    } finally {
      setLoading(false);
    }
  };

  const planEmergencyFund = async () => {
    if (!userToken) return;

    try {
      setLoading(true);
      const response = await financeApi.planEmergencyFund({
        user_id: currentUserId,
        token: userToken,
        monthly_expenses: 3200,
        current_emergency_savings: 5000,
        income_stability: 'stable'
      });
      
      if (response.status === 'success') {
        setEmergencyFund(response.data);
        setAiInsights(response.ai_insights || '');
        setRecommendations(response.recommendations || []);
      }
    } catch (error) {
      setError('Failed to plan emergency fund');
      console.error('Emergency fund planning error:', error);
    } finally {
      setLoading(false);
    }
  };

  const addTransaction = () => {
    if (!newTransaction.amount || !newTransaction.description || !newTransaction.category) {
      setError('Please fill in all transaction fields');
      return;
    }

    const transaction: Transaction = {
      id: Date.now().toString(),
      amount: parseFloat(newTransaction.amount),
      description: newTransaction.description,
      category: newTransaction.category,
      date: new Date().toISOString().split('T')[0],
      type: newTransaction.type
    };

    setTransactions(prev => [transaction, ...prev]);
    setNewTransaction({
      amount: '',
      description: '',
      category: '',
      type: 'expense'
    });
    setShowAddTransaction(false);
    setError(null);
  };

  const addBudget = () => {
    if (!newBudget.category || !newBudget.allocated) {
      setError('Please fill in all budget fields');
      return;
    }

    const budget: Budget = {
      id: Date.now().toString(),
      category: newBudget.category,
      allocated: parseFloat(newBudget.allocated),
      spent: 0,
      period: newBudget.period
    };

    setBudgets(prev => [...prev, budget]);
    setNewBudget({
      category: '',
      allocated: '',
      period: 'monthly'
    });
    setShowAddBudget(false);
    setError(null);
  };

  const getTotalIncome = () => {
    return transactions
      .filter(t => t.type === 'income')
      .reduce((sum, t) => sum + t.amount, 0);
  };

  const getTotalExpenses = () => {
    return transactions
      .filter(t => t.type === 'expense')
      .reduce((sum, t) => sum + t.amount, 0);
  };

  const getNetWorth = () => {
    return getTotalIncome() - getTotalExpenses();
  };

  const sendToHITL = (message: string, context: any) => {
    if (onSendToHITL) {
      onSendToHITL(message, {
        ...context,
        financialData: {
          transactions,
          budgets,
          goals,
          portfolios,
          netWorth: getNetWorth()
        }
      });
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingContainer}>
          <div style={styles.spinner}></div>
          <p>Loading finance agent...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <button onClick={onBack} style={styles.backButton}>
          ← Back
        </button>
        <h1 style={styles.title}>Finance Agent - ChanduFinance</h1>
        <button 
          onClick={() => sendToHITL('Need help with financial analysis', { activeTab })}
          style={styles.hitlButton}
        >
          Get Human Help
        </button>
      </div>

      {error && (
        <div style={styles.errorMessage}>
          {error}
          <button onClick={() => setError(null)} style={styles.closeError}>×</button>
        </div>
      )}

      {/* Enhanced Navigation Tabs */}
      <div style={styles.tabContainer}>
        {[
          { key: 'dashboard', label: 'Dashboard' },
          { key: 'portfolio', label: 'Portfolio' },
          { key: 'analytics', label: 'Analytics' },
          { key: 'market', label: 'Market Data' },
          { key: 'planning', label: 'Planning' },
          { key: 'insights', label: 'AI Insights' }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            style={{
              ...styles.tabButton,
              ...(activeTab === tab.key ? styles.activeTab : {})
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div style={styles.tabContent}>
          <div style={styles.metricsGrid}>
            <div style={styles.metricCard}>
              <h3>Total Income</h3>
              <p style={styles.income}>${getTotalIncome().toLocaleString()}</p>
            </div>
            <div style={styles.metricCard}>
              <h3>Total Expenses</h3>
              <p style={styles.expense}>${getTotalExpenses().toLocaleString()}</p>
            </div>
            <div style={styles.metricCard}>
              <h3>Net Worth</h3>
              <p style={getNetWorth() >= 0 ? styles.income : styles.expense}>
                ${getNetWorth().toLocaleString()}
              </p>
            </div>
            <div style={styles.metricCard}>
              <h3>Active Portfolios</h3>
              <p style={styles.neutral}>{portfolios.length}</p>
            </div>
          </div>

          {financialProfile && (
            <div style={styles.profileCard}>
              <h3>Financial Profile</h3>
              <p><strong>Age:</strong> {financialProfile.age}</p>
              <p><strong>Risk Tolerance:</strong> {financialProfile.risk_tolerance}</p>
              <p><strong>Monthly Income:</strong> ${financialProfile.monthly_income}</p>
              <p><strong>Investment Budget:</strong> ${financialProfile.investment_budget}</p>
            </div>
          )}

          <div style={styles.quickActions}>
            <h3>Quick Actions</h3>
            <div style={styles.actionGrid}>
              <button onClick={() => setShowCreatePortfolio(true)} style={styles.actionButton}>
                Create Portfolio
              </button>
              <button onClick={getStockPrices} style={styles.actionButton}>
                Get Market Data
              </button>
              <button onClick={analyzeCashflow} style={styles.actionButton}>
                Analyze Cashflow
              </button>
              <button onClick={planRetirement} style={styles.actionButton}>
                Plan Retirement
              </button>
            </div>
          </div>

          {/* Recent Transactions */}
          <div style={styles.section}>
            <div style={styles.sectionHeader}>
              <h3>Recent Transactions</h3>
              <button 
                onClick={() => setShowAddTransaction(true)}
                style={styles.addButton}
              >
                Add Transaction
              </button>
            </div>
            <div style={styles.transactionList}>
              {transactions.slice(0, 5).map(transaction => (
                <div key={transaction.id} style={styles.transactionItem}>
                  <div>
                    <strong>{transaction.description}</strong>
                    <p style={styles.category}>{transaction.category}</p>
                  </div>
                  <div style={styles.transactionAmount}>
                    <span style={transaction.type === 'income' ? styles.income : styles.expense}>
                      {transaction.type === 'income' ? '+' : '-'}${Math.abs(transaction.amount)}
                    </span>
                    <p style={styles.date}>{transaction.date}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Portfolio Tab */}
      {activeTab === 'portfolio' && (
        <div style={styles.tabContent}>
          <div style={styles.sectionHeader}>
            <h3>Investment Portfolios</h3>
            <button 
              onClick={() => setShowCreatePortfolio(true)}
              style={styles.addButton}
            >
              Create Portfolio
            </button>
          </div>

          {portfolios.length === 0 ? (
            <div style={styles.emptyState}>
              <p>No portfolios created yet. Start by creating your first investment portfolio.</p>
            </div>
          ) : (
            <div style={styles.portfolioGrid}>
              {portfolios.map((portfolio, index) => (
                <div key={index} style={styles.portfolioCard}>
                  <h4>{portfolio.name}</h4>
                  <p><strong>Value:</strong> ${portfolio.value?.toLocaleString() || 'N/A'}</p>
                  <p><strong>Risk:</strong> {portfolio.risk_tolerance}</p>
                  <p><strong>Return:</strong> {portfolio.return_rate || 'N/A'}%</p>
                  <button 
                    onClick={() => analyzePortfolio(portfolio.id)}
                    style={styles.analyzeButton}
                  >
                    Analyze
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div style={styles.tabContent}>
          <div style={styles.analyticsGrid}>
            <div style={styles.analyticsCard}>
              <h4>Cashflow Analysis</h4>
              <button onClick={analyzeCashflow} style={styles.analyzeButton}>
                Analyze Cashflow
              </button>
              {cashflowAnalysis && (
                <div style={styles.analysisResult}>
                  <p><strong>Monthly Income:</strong> ${cashflowAnalysis.monthly_income}</p>
                  <p><strong>Monthly Expenses:</strong> ${cashflowAnalysis.monthly_expenses}</p>
                  <p><strong>Net Flow:</strong> ${cashflowAnalysis.net_flow}</p>
                </div>
              )}
            </div>

            <div style={styles.analyticsCard}>
              <h4>Spending Analysis</h4>
              <button onClick={analyzeSpending} style={styles.analyzeButton}>
                Analyze Spending
              </button>
              {spendingAnalysis && (
                <div style={styles.analysisResult}>
                  <p><strong>Top Category:</strong> {spendingAnalysis.top_category}</p>
                  <p><strong>Monthly Average:</strong> ${spendingAnalysis.monthly_average}</p>
                </div>
              )}
            </div>

            <div style={styles.analyticsCard}>
              <h4>Tax Optimization</h4>
              <button onClick={optimizeTax} style={styles.analyzeButton}>
                Optimize Taxes
              </button>
              {taxOptimization && (
                <div style={styles.analysisResult}>
                  <p><strong>Potential Savings:</strong> ${taxOptimization.potential_savings}</p>
                  <p><strong>Recommendations:</strong> {taxOptimization.recommendations}</p>
                </div>
              )}
            </div>
          </div>

          {/* Budget Overview */}
          <div style={styles.section}>
            <div style={styles.sectionHeader}>
              <h3>Budget Overview</h3>
              <button 
                onClick={() => setShowAddBudget(true)}
                style={styles.addButton}
              >
                Add Budget
              </button>
            </div>
            <div style={styles.budgetList}>
              {budgets.map(budget => (
                <div key={budget.id} style={styles.budgetItem}>
                  <div style={styles.budgetInfo}>
                    <strong>{budget.category}</strong>
                    <p>${budget.spent} / ${budget.allocated} ({budget.period})</p>
                  </div>
                  <div style={styles.progressBar}>
                    <div 
                      style={{
                        ...styles.progressFill,
                        width: `${Math.min((budget.spent / budget.allocated) * 100, 100)}%`,
                        backgroundColor: budget.spent > budget.allocated ? '#e74c3c' : '#27ae60'
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Market Data Tab */}
      {activeTab === 'market' && (
        <div style={styles.tabContent}>
          <div style={styles.sectionHeader}>
            <h3>Market Data</h3>
            <button onClick={getStockPrices} style={styles.analyzeButton}>
              Refresh Data
            </button>
          </div>

          {Object.keys(stockPrices).length > 0 ? (
            <div style={styles.stockGrid}>
              {Object.entries(stockPrices).map(([symbol, data]: [string, any]) => (
                <div key={symbol} style={styles.stockCard}>
                  <h4>{symbol}</h4>
                  <p style={styles.stockPrice}>${data.price}</p>
                  <p style={data.change >= 0 ? styles.income : styles.expense}>
                    {data.change >= 0 ? '+' : ''}{data.change} ({data.change_percent}%)
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div style={styles.emptyState}>
              <p>Click "Refresh Data" to load current market prices</p>
            </div>
          )}
        </div>
      )}

      {/* Planning Tab */}
      {activeTab === 'planning' && (
        <div style={styles.tabContent}>
          <div style={styles.planningGrid}>
            <div style={styles.planningCard}>
              <h4>Retirement Planning</h4>
              <button onClick={planRetirement} style={styles.analyzeButton}>
                Plan Retirement
              </button>
              {retirementPlan && (
                <div style={styles.planResult}>
                  <p><strong>Monthly Savings Needed:</strong> ${retirementPlan.monthly_savings_needed}</p>
                  <p><strong>Projected Value:</strong> ${retirementPlan.projected_value}</p>
                  <p><strong>Years to Goal:</strong> {retirementPlan.years_to_goal}</p>
                </div>
              )}
            </div>

            <div style={styles.planningCard}>
              <h4>Emergency Fund</h4>
              <button onClick={planEmergencyFund} style={styles.analyzeButton}>
                Plan Emergency Fund
              </button>
              {emergencyFund && (
                <div style={styles.planResult}>
                  <p><strong>Recommended Amount:</strong> ${emergencyFund.recommended_amount}</p>
                  <p><strong>Current Progress:</strong> {emergencyFund.progress_percentage}%</p>
                  <p><strong>Months to Goal:</strong> {emergencyFund.months_to_goal}</p>
                </div>
              )}
            </div>
          </div>

          {/* Financial Goals */}
          <div style={styles.section}>
            <h3>Financial Goals</h3>
            <div style={styles.goalsList}>
              {goals.map(goal => (
                <div key={goal.id} style={styles.goalItem}>
                  <div style={styles.goalInfo}>
                    <h4>{goal.title}</h4>
                    <p>${goal.currentAmount.toLocaleString()} / ${goal.targetAmount.toLocaleString()}</p>
                    <p style={styles.deadline}>Target: {goal.deadline}</p>
                  </div>
                  <div style={styles.goalProgress}>
                    <div 
                      style={{
                        ...styles.progressFill,
                        width: `${(goal.currentAmount / goal.targetAmount) * 100}%`
                      }}
                    />
                  </div>
                  <span style={{
                    ...styles.priorityBadge,
                    backgroundColor: goal.priority === 'high' ? '#e74c3c' : 
                                   goal.priority === 'medium' ? '#f39c12' : '#95a5a6'
                  }}>
                    {goal.priority}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* AI Insights Tab */}
      {activeTab === 'insights' && (
        <div style={styles.tabContent}>
          <div style={styles.insightsContainer}>
            <h3>AI Financial Insights</h3>
            {aiInsights ? (
              <div style={styles.insightsCard}>
                <h4>Current Analysis</h4>
                <p style={styles.insightsText}>{aiInsights}</p>
              </div>
            ) : (
              <div style={styles.emptyState}>
                <p>Perform an analysis to get AI-powered insights</p>
              </div>
            )}

            {recommendations.length > 0 && (
              <div style={styles.recommendationsCard}>
                <h4>Recommendations</h4>
                <ul style={styles.recommendationsList}>
                  {recommendations.map((rec, index) => (
                    <li key={index} style={styles.recommendationItem}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Add Transaction Modal */}
      {showAddTransaction && (
        <div style={styles.modal}>
          <div style={styles.modalContent}>
            <h3>Add Transaction</h3>
            <div style={styles.formGroup}>
              <label>Amount</label>
              <input
                type="number"
                value={newTransaction.amount}
                onChange={(e) => setNewTransaction(prev => ({ ...prev, amount: e.target.value }))}
                style={styles.input}
                placeholder="0.00"
              />
            </div>
            <div style={styles.formGroup}>
              <label>Description</label>
              <input
                type="text"
                value={newTransaction.description}
                onChange={(e) => setNewTransaction(prev => ({ ...prev, description: e.target.value }))}
                style={styles.input}
                placeholder="Transaction description"
              />
            </div>
            <div style={styles.formGroup}>
              <label>Category</label>
              <input
                type="text"
                value={newTransaction.category}
                onChange={(e) => setNewTransaction(prev => ({ ...prev, category: e.target.value }))}
                style={styles.input}
                placeholder="Food, Transportation, etc."
              />
            </div>
            <div style={styles.formGroup}>
              <label>Type</label>
              <select
                value={newTransaction.type}
                onChange={(e) => setNewTransaction(prev => ({ ...prev, type: e.target.value as 'income' | 'expense' }))}
                style={styles.select}
              >
                <option value="expense">Expense</option>
                <option value="income">Income</option>
              </select>
            </div>
            <div style={styles.modalActions}>
              <button onClick={addTransaction} style={styles.saveButton}>
                Add Transaction
              </button>
              <button onClick={() => setShowAddTransaction(false)} style={styles.cancelButton}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Budget Modal */}
      {showAddBudget && (
        <div style={styles.modal}>
          <div style={styles.modalContent}>
            <h3>Add Budget</h3>
            <div style={styles.formGroup}>
              <label>Category</label>
              <input
                type="text"
                value={newBudget.category}
                onChange={(e) => setNewBudget(prev => ({ ...prev, category: e.target.value }))}
                style={styles.input}
                placeholder="Food, Entertainment, etc."
              />
            </div>
            <div style={styles.formGroup}>
              <label>Allocated Amount</label>
              <input
                type="number"
                value={newBudget.allocated}
                onChange={(e) => setNewBudget(prev => ({ ...prev, allocated: e.target.value }))}
                style={styles.input}
                placeholder="0.00"
              />
            </div>
            <div style={styles.formGroup}>
              <label>Period</label>
              <select
                value={newBudget.period}
                onChange={(e) => setNewBudget(prev => ({ ...prev, period: e.target.value as 'monthly' | 'yearly' }))}
                style={styles.select}
              >
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
            <div style={styles.modalActions}>
              <button onClick={addBudget} style={styles.saveButton}>
                Add Budget
              </button>
              <button onClick={() => setShowAddBudget(false)} style={styles.cancelButton}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Portfolio Modal */}
      {showCreatePortfolio && (
        <div style={styles.modal}>
          <div style={styles.modalContent}>
            <h3>Create Portfolio</h3>
            <div style={styles.formGroup}>
              <label>Portfolio Name</label>
              <input
                type="text"
                value={newPortfolio.portfolio_name}
                onChange={(e) => setNewPortfolio(prev => ({ ...prev, portfolio_name: e.target.value }))}
                style={styles.input}
                placeholder="My Investment Portfolio"
              />
            </div>
            <div style={styles.formGroup}>
              <label>Investment Amount</label>
              <input
                type="number"
                value={newPortfolio.investment_amount}
                onChange={(e) => setNewPortfolio(prev => ({ ...prev, investment_amount: e.target.value }))}
                style={styles.input}
                placeholder="10000"
              />
            </div>
            <div style={styles.formGroup}>
              <label>Risk Tolerance</label>
              <select
                value={newPortfolio.risk_tolerance}
                onChange={(e) => setNewPortfolio(prev => ({ ...prev, risk_tolerance: e.target.value as any }))}
                style={styles.select}
              >
                <option value="conservative">Conservative</option>
                <option value="moderate">Moderate</option>
                <option value="aggressive">Aggressive</option>
              </select>
            </div>
            <div style={styles.formGroup}>
              <label>Time Horizon (years)</label>
              <input
                type="number"
                value={newPortfolio.time_horizon}
                onChange={(e) => setNewPortfolio(prev => ({ ...prev, time_horizon: e.target.value }))}
                style={styles.input}
                placeholder="10"
              />
            </div>
            <div style={styles.modalActions}>
              <button onClick={createPortfolio} style={styles.saveButton}>
                Create Portfolio
              </button>
              <button onClick={() => setShowCreatePortfolio(false)} style={styles.cancelButton}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto',
    fontFamily: 'Arial, sans-serif'
  },
  loadingContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    height: '400px'
  },
  spinner: {
    width: '40px',
    height: '40px',
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #3498db',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px'
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#2c3e50',
    margin: 0
  },
  backButton: {
    padding: '10px 20px',
    backgroundColor: '#95a5a6',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '14px'
  },
  hitlButton: {
    padding: '10px 20px',
    backgroundColor: '#e74c3c',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '14px'
  },
  errorMessage: {
    backgroundColor: '#f8d7da',
    color: '#721c24',
    padding: '15px',
    borderRadius: '5px',
    marginBottom: '20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  closeError: {
    background: 'none',
    border: 'none',
    fontSize: '18px',
    cursor: 'pointer',
    color: '#721c24'
  },
  tabContainer: {
    display: 'flex',
    borderBottom: '2px solid #ecf0f1',
    marginBottom: '20px'
  },
  tabButton: {
    padding: '12px 24px',
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: '2px solid transparent',
    cursor: 'pointer',
    fontSize: '16px',
    color: '#7f8c8d',
    transition: 'all 0.3s ease'
  },
  activeTab: {
    color: '#3498db',
    borderBottomColor: '#3498db'
  },
  tabContent: {
    minHeight: '400px'
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '30px'
  },
  metricCard: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    textAlign: 'center' as const
  },
  income: {
    color: '#27ae60',
    fontSize: '24px',
    fontWeight: 'bold',
    margin: '10px 0'
  },
  expense: {
    color: '#e74c3c',
    fontSize: '24px',
    fontWeight: 'bold',
    margin: '10px 0'
  },
  neutral: {
    color: '#3498db',
    fontSize: '24px',
    fontWeight: 'bold',
    margin: '10px 0'
  },
  profileCard: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    marginBottom: '30px'
  },
  quickActions: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    marginBottom: '30px'
  },
  actionGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '15px',
    marginTop: '15px'
  },
  actionButton: {
    padding: '12px 20px',
    backgroundColor: '#3498db',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '14px',
    transition: 'background-color 0.3s ease'
  },
  section: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    marginBottom: '20px'
  },
  sectionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px'
  },
  addButton: {
    padding: '8px 16px',
    backgroundColor: '#27ae60',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '14px'
  },
  transactionList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '10px'
  },
  transactionItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '15px',
    backgroundColor: '#f8f9fa',
    borderRadius: '5px'
  },
  transactionAmount: {
    textAlign: 'right' as const
  },
  category: {
    color: '#7f8c8d',
    fontSize: '14px',
    margin: '5px 0'
  },
  date: {
    color: '#7f8c8d',
    fontSize: '12px',
    margin: '5px 0'
  },
  portfolioGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '20px'
  },
  portfolioCard: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
  },
  analyzeButton: {
    padding: '8px 16px',
    backgroundColor: '#3498db',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '14px',
    marginTop: '10px'
  },
  emptyState: {
    textAlign: 'center' as const,
    padding: '40px',
    color: '#7f8c8d'
  },
  analyticsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '20px',
    marginBottom: '30px'
  },
  analyticsCard: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
  },
  analysisResult: {
    marginTop: '15px',
    padding: '15px',
    backgroundColor: '#f8f9fa',
    borderRadius: '5px'
  },
  budgetList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '15px'
  },
  budgetItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    padding: '15px',
    backgroundColor: '#f8f9fa',
    borderRadius: '5px'
  },
  budgetInfo: {
    flex: '0 0 200px'
  },
  progressBar: {
    flex: 1,
    height: '10px',
    backgroundColor: '#ecf0f1',
    borderRadius: '5px',
    overflow: 'hidden'
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#27ae60',
    transition: 'width 0.3s ease'
  },
  stockGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '20px'
  },
  stockCard: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    textAlign: 'center' as const
  },
  stockPrice: {
    fontSize: '24px',
    fontWeight: 'bold',
    margin: '10px 0'
  },
  planningGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: '20px',
    marginBottom: '30px'
  },
  planningCard: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
  },
  planResult: {
    marginTop: '15px',
    padding: '15px',
    backgroundColor: '#f8f9fa',
    borderRadius: '5px'
  },
  goalsList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '15px'
  },
  goalItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    padding: '20px',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px'
  },
  goalInfo: {
    flex: '0 0 200px'
  },
  goalProgress: {
    flex: 1,
    height: '10px',
    backgroundColor: '#ecf0f1',
    borderRadius: '5px',
    overflow: 'hidden'
  },
  deadline: {
    color: '#7f8c8d',
    fontSize: '14px',
    margin: '5px 0'
  },
  priorityBadge: {
    padding: '4px 8px',
    borderRadius: '12px',
    color: 'white',
    fontSize: '12px',
    fontWeight: 'bold'
  },
  insightsContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '20px'
  },
  insightsCard: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
  },
  insightsText: {
    lineHeight: 1.6,
    color: '#2c3e50'
  },
  recommendationsCard: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
  },
  recommendationsList: {
    margin: 0,
    paddingLeft: '20px'
  },
  recommendationItem: {
    marginBottom: '10px',
    lineHeight: 1.6
  },
  modal: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000
  },
  modalContent: {
    backgroundColor: 'white',
    padding: '30px',
    borderRadius: '8px',
    width: '90%',
    maxWidth: '500px',
    maxHeight: '80%',
    overflow: 'auto'
  },
  formGroup: {
    marginBottom: '20px'
  },
  input: {
    width: '100%',
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '5px',
    fontSize: '16px',
    boxSizing: 'border-box' as const
  },
  select: {
    width: '100%',
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '5px',
    fontSize: '16px',
    boxSizing: 'border-box' as const
  },
  modalActions: {
    display: 'flex',
    gap: '10px',
    justifyContent: 'flex-end',
    marginTop: '20px'
  },
  saveButton: {
    padding: '10px 20px',
    backgroundColor: '#27ae60',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '16px'
  },
  cancelButton: {
    padding: '10px 20px',
    backgroundColor: '#95a5a6',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '16px'
  }
};

export default FinanceAgent;
