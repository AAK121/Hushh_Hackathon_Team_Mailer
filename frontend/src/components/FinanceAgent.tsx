import React, { useState, useEffect } from 'react';

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
  const [activeTab, setActiveTab] = useState<'dashboard' | 'transactions' | 'budget' | 'goals' | 'insights'>('dashboard');
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [goals, setGoals] = useState<FinancialGoal[]>([]);
  const [loading, setLoading] = useState(false);
  const [financialProfile, setFinancialProfile] = useState<any>(null);
  const [profileMessage, setProfileMessage] = useState<string>('');
  
  // Form states
  const [showAddTransaction, setShowAddTransaction] = useState(false);
  const [showAddBudget, setShowAddBudget] = useState(false);
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

  useEffect(() => {
    loadFinancialData();
    initializeFinanceProfile();
  }, []);

  const initializeFinanceProfile = async () => {
    try {
      setLoading(true);
      // Import the API service
      const { hushMcpApi } = await import('../services/hushMcpApi');
      
      // Create finance token
      const token = await hushMcpApi.createChanduFinanceToken('demo_user');
      
      // Setup profile
      const profileResponse = await hushMcpApi.executeChanduFinance({
        user_id: 'demo_user',
        token: token,
        command: 'setup_profile',
        full_name: 'Demo User',
        age: 30,
        occupation: 'Software Developer',
        monthly_income: 3700,
        monthly_expenses: 1630,
        current_savings: 5000,
        investment_budget: 1000,
        risk_tolerance: 'moderate',
        investment_experience: 'beginner',
        gemini_api_key: process.env.VITE_GEMINI_API_KEY || 'AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI'
      });
      
      if (profileResponse.status === 'success') {
        setFinancialProfile(profileResponse.profile_summary);
        setProfileMessage(profileResponse.welcome_message || 'Profile loaded successfully');
      }
    } catch (error) {
      console.error('Failed to initialize finance profile:', error);
      // Continue with mock data if backend fails
    } finally {
      setLoading(false);
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
        amount: 350,
        description: 'Groceries',
        category: 'Food',
        date: '2025-01-08',
        type: 'expense'
      },
      {
        id: '4',
        amount: 80,
        description: 'Gas Station',
        category: 'Transportation',
        date: '2025-01-07',
        type: 'expense'
      },
      {
        id: '5',
        amount: 500,
        description: 'Freelance Project',
        category: 'Income',
        date: '2025-01-05',
        type: 'income'
      }
    ];

    const mockBudgets: Budget[] = [
      {
        id: '1',
        category: 'Food',
        allocated: 600,
        spent: 350,
        period: 'monthly'
      },
      {
        id: '2',
        category: 'Transportation',
        allocated: 200,
        spent: 80,
        period: 'monthly'
      },
      {
        id: '3',
        category: 'Entertainment',
        allocated: 300,
        spent: 0,
        period: 'monthly'
      },
      {
        id: '4',
        category: 'Housing',
        allocated: 1200,
        spent: 1200,
        period: 'monthly'
      }
    ];

    const mockGoals: FinancialGoal[] = [
      {
        id: '1',
        title: 'Emergency Fund',
        targetAmount: 10000,
        currentAmount: 3500,
        deadline: '2025-12-31',
        priority: 'high'
      },
      {
        id: '2',
        title: 'Vacation to Europe',
        targetAmount: 5000,
        currentAmount: 1200,
        deadline: '2025-08-15',
        priority: 'medium'
      },
      {
        id: '3',
        title: 'New Laptop',
        targetAmount: 2000,
        currentAmount: 800,
        deadline: '2025-06-01',
        priority: 'low'
      }
    ];

    setTransactions(mockTransactions);
    setBudgets(mockBudgets);
    setGoals(mockGoals);
  };

  const addTransaction = () => {
    if (!newTransaction.amount || !newTransaction.description || !newTransaction.category) {
      alert('Please fill in all fields');
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

    // Send to HITL for financial insights
    if (onSendToHITL) {
      const message = `New ${transaction.type} of $${transaction.amount} for ${transaction.category}: ${transaction.description}. How does this impact my financial goals and budget?`;
      onSendToHITL(message, { transaction, totalTransactions: transactions.length + 1 });
    }
  };

  const addBudget = () => {
    if (!newBudget.category || !newBudget.allocated) {
      alert('Please fill in all fields');
      return;
    }

    const budget: Budget = {
      id: Date.now().toString(),
      category: newBudget.category,
      allocated: parseFloat(newBudget.allocated),
      spent: 0,
      period: newBudget.period
    };

    setBudgets(prev => [budget, ...prev]);
    setNewBudget({
      category: '',
      allocated: '',
      period: 'monthly'
    });
    setShowAddBudget(false);

    // Send to HITL for budget optimization
    if (onSendToHITL) {
      const message = `Created new ${budget.period} budget for ${budget.category}: $${budget.allocated}. Can you suggest ways to optimize this budget allocation?`;
      onSendToHITL(message, { budget, totalBudgets: budgets.length + 1 });
    }
  };

  const generateFinancialInsights = () => {
    setLoading(true);
    
    setTimeout(() => {
      if (onSendToHITL) {
        const totalIncome = transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0);
        const totalExpenses = transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0);
        const netIncome = totalIncome - totalExpenses;
        const goalProgress = goals.reduce((sum, g) => sum + (g.currentAmount / g.targetAmount), 0) / goals.length * 100;
        
        const message = `Analyze my finances: Income: $${totalIncome}, Expenses: $${totalExpenses}, Net: $${netIncome}. Average goal progress: ${goalProgress.toFixed(1)}%. What insights and recommendations do you have?`;
        onSendToHITL(message, { 
          summary: { totalIncome, totalExpenses, netIncome, goalProgress },
          transactions, 
          budgets, 
          goals 
        });
      }
      setLoading(false);
    }, 1000);
  };

  const sendGoalAnalysisToHITL = (goal: FinancialGoal) => {
    if (onSendToHITL) {
      const progress = (goal.currentAmount / goal.targetAmount) * 100;
      const daysLeft = Math.ceil((new Date(goal.deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
      const message = `Analyze my goal "${goal.title}": ${progress.toFixed(1)}% complete, $${goal.currentAmount}/$${goal.targetAmount}, ${daysLeft} days left. How can I reach this goal faster?`;
      onSendToHITL(message, { goal, progress, daysLeft });
    }
  };

  const styles = {
    container: {
      padding: '2rem',
      background: 'linear-gradient(135deg, #0f766e 0%, #065f46 100%)',
      minHeight: '100vh',
      color: 'white',
    },
    header: {
      textAlign: 'center' as const,
      marginBottom: '3rem',
    },
    title: {
      fontSize: '3rem',
      fontWeight: '700',
      marginBottom: '1rem',
      textShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
    },
    subtitle: {
      fontSize: '1.2rem',
      color: 'rgba(255, 255, 255, 0.9)',
      maxWidth: '600px',
      margin: '0 auto',
      lineHeight: '1.6',
    },
    backButton: {
      position: 'absolute' as const,
      top: '2rem',
      left: '2rem',
      padding: '0.75rem 1.5rem',
      background: 'rgba(255, 255, 255, 0.2)',
      border: 'none',
      borderRadius: '0.75rem',
      color: 'white',
      cursor: 'pointer',
      fontSize: '1rem',
      fontWeight: '500',
      transition: 'all 0.3s ease',
      backdropFilter: 'blur(10px)',
    },
    tabsContainer: {
      display: 'flex',
      justifyContent: 'center',
      gap: '1rem',
      marginBottom: '2rem',
      flexWrap: 'wrap' as const,
    },
    tab: {
      padding: '0.75rem 1.5rem',
      background: 'rgba(255, 255, 255, 0.1)',
      border: 'none',
      borderRadius: '0.75rem',
      color: 'white',
      cursor: 'pointer',
      fontSize: '1rem',
      fontWeight: '500',
      transition: 'all 0.3s ease',
      backdropFilter: 'blur(10px)',
    },
    activeTab: {
      background: 'rgba(255, 255, 255, 0.3)',
    },
    contentContainer: {
      background: 'rgba(255, 255, 255, 0.1)',
      borderRadius: '1rem',
      padding: '2rem',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
    },
    grid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '2rem',
    },
    card: {
      background: 'rgba(255, 255, 255, 0.1)',
      borderRadius: '0.75rem',
      padding: '1.5rem',
      border: '1px solid rgba(255, 255, 255, 0.2)',
    },
    cardTitle: {
      fontSize: '1.25rem',
      fontWeight: '600',
      marginBottom: '1rem',
    },
    summaryGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '1rem',
      marginBottom: '2rem',
    },
    summaryCard: {
      background: 'rgba(255, 255, 255, 0.1)',
      borderRadius: '0.75rem',
      padding: '1.5rem',
      textAlign: 'center' as const,
    },
    summaryValue: {
      fontSize: '2rem',
      fontWeight: '700',
      marginBottom: '0.5rem',
    },
    summaryLabel: {
      fontSize: '0.9rem',
      color: 'rgba(255, 255, 255, 0.8)',
    },
    button: {
      padding: '0.75rem 1.5rem',
      background: 'rgba(255, 255, 255, 0.2)',
      border: 'none',
      borderRadius: '0.5rem',
      color: 'white',
      cursor: 'pointer',
      fontSize: '0.9rem',
      fontWeight: '500',
      transition: 'all 0.3s ease',
      marginRight: '0.5rem',
      marginBottom: '0.5rem',
    },
    primaryButton: {
      background: 'linear-gradient(135deg, #10b981, #047857)',
    },
    hitlButton: {
      background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
    },
    transactionCard: {
      background: 'rgba(255, 255, 255, 0.1)',
      borderRadius: '0.75rem',
      padding: '1rem',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      marginBottom: '0.75rem',
    },
    budgetCard: {
      background: 'rgba(255, 255, 255, 0.1)',
      borderRadius: '0.75rem',
      padding: '1.5rem',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      marginBottom: '1rem',
    },
    progressBar: {
      width: '100%',
      height: '0.5rem',
      background: 'rgba(255, 255, 255, 0.2)',
      borderRadius: '0.25rem',
      overflow: 'hidden',
      marginTop: '0.5rem',
    },
    progressFill: {
      height: '100%',
      borderRadius: '0.25rem',
      transition: 'width 0.3s ease',
    },
    modal: {
      position: 'fixed' as const,
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    },
    modalContent: {
      background: 'rgba(255, 255, 255, 0.95)',
      borderRadius: '1rem',
      padding: '2rem',
      maxWidth: '500px',
      width: '90%',
      color: '#333',
    },
    formGroup: {
      marginBottom: '1rem',
    },
    label: {
      display: 'block',
      marginBottom: '0.5rem',
      fontWeight: '600',
      color: '#333',
    },
    input: {
      width: '100%',
      padding: '0.75rem',
      borderRadius: '0.5rem',
      border: '1px solid #ddd',
      fontSize: '1rem',
    },
    select: {
      width: '100%',
      padding: '0.75rem',
      borderRadius: '0.5rem',
      border: '1px solid #ddd',
      fontSize: '1rem',
    }
  };

  const totalIncome = transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0);
  const totalExpenses = transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0);
  const netIncome = totalIncome - totalExpenses;

  const getBudgetStatus = (budget: Budget) => {
    const percentage = (budget.spent / budget.allocated) * 100;
    if (percentage > 100) return { color: '#ef4444', status: 'Over Budget' };
    if (percentage > 80) return { color: '#f59e0b', status: 'Near Limit' };
    return { color: '#10b981', status: 'On Track' };
  };

  const renderDashboard = () => (
    <div>
      <div style={styles.summaryGrid}>
        <div style={styles.summaryCard}>
          <div style={{...styles.summaryValue, color: '#10b981'}}>${totalIncome.toLocaleString()}</div>
          <div style={styles.summaryLabel}>Total Income</div>
        </div>
        <div style={styles.summaryCard}>
          <div style={{...styles.summaryValue, color: '#ef4444'}}>${totalExpenses.toLocaleString()}</div>
          <div style={styles.summaryLabel}>Total Expenses</div>
        </div>
        <div style={styles.summaryCard}>
          <div style={{...styles.summaryValue, color: netIncome >= 0 ? '#10b981' : '#ef4444'}}>
            ${netIncome.toLocaleString()}
          </div>
          <div style={styles.summaryLabel}>Net Income</div>
        </div>
        <div style={styles.summaryCard}>
          <div style={{...styles.summaryValue, color: '#3b82f6'}}>{goals.length}</div>
          <div style={styles.summaryLabel}>Active Goals</div>
        </div>
      </div>

      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <button 
          style={{...styles.button, ...styles.hitlButton}}
          onClick={generateFinancialInsights}
          disabled={loading}
        >
          {loading ? '🤖 Analyzing...' : '🤖 Get Financial Insights'}
        </button>
      </div>

      <div style={styles.grid}>
        <div style={styles.card}>
          <h3 style={styles.cardTitle}>Recent Transactions</h3>
          {transactions.slice(0, 5).map((transaction) => (
            <div key={transaction.id} style={styles.transactionCard}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontWeight: '500' }}>{transaction.description}</span>
                <span style={{ 
                  fontWeight: '600',
                  color: transaction.type === 'income' ? '#10b981' : '#ef4444'
                }}>
                  {transaction.type === 'income' ? '+' : '-'}${transaction.amount}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.8)' }}>
                <span>{transaction.category}</span>
                <span>{new Date(transaction.date).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>

        <div style={styles.card}>
          <h3 style={styles.cardTitle}>Budget Overview</h3>
          {budgets.slice(0, 3).map((budget) => {
            const status = getBudgetStatus(budget);
            const percentage = Math.min((budget.spent / budget.allocated) * 100, 100);
            
            return (
              <div key={budget.id} style={styles.budgetCard}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ fontWeight: '500' }}>{budget.category}</span>
                  <span style={{ color: status.color, fontSize: '0.8rem', fontWeight: '600' }}>
                    {status.status}
                  </span>
                </div>
                <div style={{ fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                  ${budget.spent} / ${budget.allocated}
                </div>
                <div style={styles.progressBar}>
                  <div 
                    style={{
                      ...styles.progressFill,
                      width: `${percentage}%`,
                      background: status.color
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        <div style={styles.card}>
          <h3 style={styles.cardTitle}>Financial Goals</h3>
          {goals.slice(0, 3).map((goal) => {
            const progress = (goal.currentAmount / goal.targetAmount) * 100;
            const daysLeft = Math.ceil((new Date(goal.deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
            
            return (
              <div key={goal.id} style={{ marginBottom: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <div>
                    <div style={{ fontWeight: '500' }}>{goal.title}</div>
                    <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.8)' }}>
                      ${goal.currentAmount} / ${goal.targetAmount} • {daysLeft} days left
                    </div>
                  </div>
                  <button 
                    style={{...styles.button, ...styles.hitlButton, padding: '0.5rem 1rem'}}
                    onClick={() => sendGoalAnalysisToHITL(goal)}
                  >
                    🤖 Analyze
                  </button>
                </div>
                <div style={styles.progressBar}>
                  <div 
                    style={{
                      ...styles.progressFill,
                      width: `${Math.min(progress, 100)}%`,
                      background: progress >= 100 ? '#10b981' : progress >= 50 ? '#3b82f6' : '#f59e0b'
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );

  const renderTransactions = () => (
    <div>
      <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <button 
          style={{...styles.button, ...styles.primaryButton}}
          onClick={() => setShowAddTransaction(true)}
        >
          + Add Transaction
        </button>
      </div>

      <div style={styles.grid}>
        {transactions.map((transaction) => (
          <div key={transaction.id} style={styles.transactionCard}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: '500' }}>{transaction.description}</span>
              <span style={{ 
                fontWeight: '600',
                color: transaction.type === 'income' ? '#10b981' : '#ef4444'
              }}>
                {transaction.type === 'income' ? '+' : '-'}${transaction.amount}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.8)' }}>
              <span>{transaction.category}</span>
              <span>{new Date(transaction.date).toLocaleDateString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div style={styles.container}>
      <button 
        onClick={onBack} 
        style={styles.backButton}
        onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)'}
        onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)'}
      >
        ← Back to Agent Store
      </button>

      <div style={styles.header}>
        <h1 style={styles.title}>💰 Personal Finance Manager</h1>
        <p style={styles.subtitle}>
          Intelligent financial management with AI-powered insights. Track your expenses, 
          manage budgets, set goals, and get personalized recommendations to improve your financial health.
        </p>
      </div>

      <div style={styles.tabsContainer}>
        {['dashboard', 'transactions', 'budget', 'goals'].map((tab) => (
          <button
            key={tab}
            style={{
              ...styles.tab,
              ...(activeTab === tab ? styles.activeTab : {})
            }}
            onClick={() => setActiveTab(tab as any)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div style={styles.contentContainer}>
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'transactions' && renderTransactions()}
        {activeTab === 'budget' && (
          <div>
            <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
              <button 
                style={{...styles.button, ...styles.primaryButton}}
                onClick={() => setShowAddBudget(true)}
              >
                + Add Budget
              </button>
            </div>
            {/* Budget management content would go here */}
          </div>
        )}
        {activeTab === 'goals' && (
          <div>
            <h3>Financial Goals</h3>
            {goals.map((goal) => {
              const progress = (goal.currentAmount / goal.targetAmount) * 100;
              return (
                <div key={goal.id} style={styles.card}>
                  <h4>{goal.title}</h4>
                  <p>${goal.currentAmount} / ${goal.targetAmount}</p>
                  <div style={styles.progressBar}>
                    <div 
                      style={{
                        ...styles.progressFill,
                        width: `${Math.min(progress, 100)}%`,
                        background: '#10b981'
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Add Transaction Modal */}
      {showAddTransaction && (
        <div style={styles.modal} onClick={() => setShowAddTransaction(false)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h2>Add New Transaction</h2>
            
            <div style={styles.formGroup}>
              <label style={styles.label}>Type</label>
              <select
                style={styles.select}
                value={newTransaction.type}
                onChange={(e) => setNewTransaction({...newTransaction, type: e.target.value as 'income' | 'expense'})}
              >
                <option value="expense">Expense</option>
                <option value="income">Income</option>
              </select>
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Amount</label>
              <input
                style={styles.input}
                type="number"
                value={newTransaction.amount}
                onChange={(e) => setNewTransaction({...newTransaction, amount: e.target.value})}
                placeholder="0.00"
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Description</label>
              <input
                style={styles.input}
                value={newTransaction.description}
                onChange={(e) => setNewTransaction({...newTransaction, description: e.target.value})}
                placeholder="What was this for?"
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Category</label>
              <select
                style={styles.select}
                value={newTransaction.category}
                onChange={(e) => setNewTransaction({...newTransaction, category: e.target.value})}
              >
                <option value="">Select category</option>
                <option value="Food">Food</option>
                <option value="Transportation">Transportation</option>
                <option value="Housing">Housing</option>
                <option value="Entertainment">Entertainment</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Income">Income</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '2rem' }}>
              <button 
                onClick={() => setShowAddTransaction(false)}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: '#6b7280',
                  border: 'none',
                  borderRadius: '0.5rem',
                  color: 'white',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
              <button 
                onClick={addTransaction}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: '#10b981',
                  border: 'none',
                  borderRadius: '0.5rem',
                  color: 'white',
                  cursor: 'pointer'
                }}
              >
                Add Transaction
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Budget Modal */}
      {showAddBudget && (
        <div style={styles.modal} onClick={() => setShowAddBudget(false)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h2>Add New Budget</h2>
            
            <div style={styles.formGroup}>
              <label style={styles.label}>Category</label>
              <select
                style={styles.select}
                value={newBudget.category}
                onChange={(e) => setNewBudget({...newBudget, category: e.target.value})}
              >
                <option value="">Select category</option>
                <option value="Food">Food</option>
                <option value="Transportation">Transportation</option>
                <option value="Entertainment">Entertainment</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Utilities">Utilities</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Allocated Amount</label>
              <input
                style={styles.input}
                type="number"
                value={newBudget.allocated}
                onChange={(e) => setNewBudget({...newBudget, allocated: e.target.value})}
                placeholder="0.00"
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Period</label>
              <select
                style={styles.select}
                value={newBudget.period}
                onChange={(e) => setNewBudget({...newBudget, period: e.target.value as 'monthly' | 'yearly'})}
              >
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '2rem' }}>
              <button 
                onClick={() => setShowAddBudget(false)}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: '#6b7280',
                  border: 'none',
                  borderRadius: '0.5rem',
                  color: 'white',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
              <button 
                onClick={addBudget}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: '#10b981',
                  border: 'none',
                  borderRadius: '0.5rem',
                  color: 'white',
                  cursor: 'pointer'
                }}
              >
                Add Budget
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FinanceAgent;
