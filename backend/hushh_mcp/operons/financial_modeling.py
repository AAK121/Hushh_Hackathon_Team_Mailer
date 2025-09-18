# hushh_mcp/operons/financial_modeling.py

"""
Financial Modeling Operon for HushhMCP
=====================================

This operon provides reusable financial modeling functions for DCF analysis,
three-statement modeling, and investment recommendations. Designed to be used
by financial agents within the HushhMCP ecosystem.
"""

import json
import math
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta


class FinancialModelingError(Exception):
    """Custom exception for financial modeling errors"""
    pass


def build_three_statement_model(historical_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a three-statement financial model with forecasts.
    
    Args:
        historical_data: Dictionary containing historical financial statements
        
    Returns:
        Dictionary containing forecasted income statement, balance sheet, and cash flow
    """
    try:
        # Extract historical data
        income_statements = historical_data.get('income_statements', [])
        balance_sheets = historical_data.get('balance_sheets', [])
        cash_flows = historical_data.get('cash_flows', [])
        
        if not income_statements or len(income_statements) < 3:
            raise FinancialModelingError("Insufficient historical income statement data")
            
        # Calculate growth rates from historical data
        revenues = [stmt.get('revenue', 0) for stmt in income_statements[-3:]]
        revenue_growth_rates = []
        for i in range(1, len(revenues)):
            if revenues[i-1] != 0:
                growth = (revenues[i] - revenues[i-1]) / revenues[i-1]
                revenue_growth_rates.append(growth)
        
        avg_revenue_growth = sum(revenue_growth_rates) / len(revenue_growth_rates) if revenue_growth_rates else 0.05
        
        # Get latest financial metrics
        latest_income = income_statements[-1]
        latest_balance = balance_sheets[-1] if balance_sheets else {}
        latest_cashflow = cash_flows[-1] if cash_flows else {}
        
        # Calculate key ratios
        latest_revenue = latest_income.get('revenue', 0)
        latest_ebitda = latest_income.get('ebitda', latest_income.get('operating_income', 0))
        ebitda_margin = latest_ebitda / latest_revenue if latest_revenue > 0 else 0.15
        
        # Forecast 5 years
        forecast_years = 5
        forecasts = {
            'income_statements': [],
            'balance_sheets': [],
            'cash_flows': [],
            'assumptions': {
                'revenue_growth_rate': avg_revenue_growth,
                'ebitda_margin': ebitda_margin,
                'tax_rate': 0.25,
                'capex_as_percent_revenue': 0.03,
                'working_capital_change': 0.02
            }
        }
        
        # Generate forecasts
        for year in range(1, forecast_years + 1):
            # Income Statement Forecast
            forecasted_revenue = latest_revenue * ((1 + avg_revenue_growth) ** year)
            forecasted_ebitda = forecasted_revenue * ebitda_margin
            depreciation = forecasted_revenue * 0.02  # 2% of revenue
            forecasted_ebit = forecasted_ebitda - depreciation
            interest_expense = forecasted_revenue * 0.01  # 1% of revenue
            ebt = forecasted_ebit - interest_expense
            taxes = ebt * 0.25  # 25% tax rate
            net_income = ebt - taxes
            
            income_forecast = {
                'year': datetime.now().year + year,
                'revenue': round(forecasted_revenue, 2),
                'ebitda': round(forecasted_ebitda, 2),
                'depreciation': round(depreciation, 2),
                'ebit': round(forecasted_ebit, 2),
                'interest_expense': round(interest_expense, 2),
                'ebt': round(ebt, 2),
                'taxes': round(taxes, 2),
                'net_income': round(net_income, 2)
            }
            
            # Cash Flow Forecast
            capex = forecasted_revenue * 0.03  # 3% of revenue
            working_capital_change = forecasted_revenue * 0.02  # 2% of revenue
            free_cash_flow = net_income + depreciation - capex - working_capital_change
            
            cashflow_forecast = {
                'year': datetime.now().year + year,
                'net_income': round(net_income, 2),
                'depreciation': round(depreciation, 2),
                'capex': round(-capex, 2),
                'working_capital_change': round(-working_capital_change, 2),
                'free_cash_flow': round(free_cash_flow, 2)
            }
            
            # Simple Balance Sheet (focus on key items)
            balance_forecast = {
                'year': datetime.now().year + year,
                'total_assets': round(forecasted_revenue * 0.8, 2),  # Asset turnover of 1.25
                'total_debt': round(forecasted_revenue * 0.3, 2),    # 30% debt-to-revenue
                'shareholders_equity': round(forecasted_revenue * 0.4, 2)  # 40% equity-to-revenue
            }
            
            forecasts['income_statements'].append(income_forecast)
            forecasts['cash_flows'].append(cashflow_forecast)
            forecasts['balance_sheets'].append(balance_forecast)
        
        return forecasts
        
    except Exception as e:
        raise FinancialModelingError(f"Error building three-statement model: {str(e)}")


def perform_dcf_analysis(forecasts: Dict[str, Any], wacc: float, terminal_growth_rate: float) -> Dict[str, Any]:
    """
    Perform Discounted Cash Flow (DCF) analysis.
    
    Args:
        forecasts: Dictionary containing forecasted financial statements
        wacc: Weighted Average Cost of Capital (as decimal, e.g., 0.10 for 10%)
        terminal_growth_rate: Terminal growth rate (as decimal, e.g., 0.03 for 3%)
        
    Returns:
        Dictionary containing DCF analysis results including intrinsic value per share
    """
    try:
        cash_flows = forecasts.get('cash_flows', [])
        if not cash_flows:
            raise FinancialModelingError("No cash flow forecasts available for DCF analysis")
        
        # Extract free cash flows
        fcf_projections = [cf['free_cash_flow'] for cf in cash_flows]
        
        # Calculate present value of forecasted cash flows
        pv_fcf = []
        for i, fcf in enumerate(fcf_projections):
            pv = fcf / ((1 + wacc) ** (i + 1))
            pv_fcf.append(pv)
        
        # Calculate terminal value
        terminal_fcf = fcf_projections[-1] * (1 + terminal_growth_rate)
        terminal_value = terminal_fcf / (wacc - terminal_growth_rate)
        pv_terminal_value = terminal_value / ((1 + wacc) ** len(fcf_projections))
        
        # Calculate enterprise value
        enterprise_value = sum(pv_fcf) + pv_terminal_value
        
        # Assume some debt and cash (simplified)
        net_debt = enterprise_value * 0.2  # Assume 20% net debt
        equity_value = enterprise_value - net_debt
        
        # Assume shares outstanding (this would come from market data in real implementation)
        shares_outstanding = 1000000  # 1 million shares (placeholder)
        intrinsic_value_per_share = equity_value / shares_outstanding
        
        dcf_results = {
            'free_cash_flows': fcf_projections,
            'present_value_fcf': [round(pv, 2) for pv in pv_fcf],
            'terminal_value': round(terminal_value, 2),
            'pv_terminal_value': round(pv_terminal_value, 2),
            'enterprise_value': round(enterprise_value, 2),
            'net_debt': round(net_debt, 2),
            'equity_value': round(equity_value, 2),
            'shares_outstanding': shares_outstanding,
            'intrinsic_value_per_share': round(intrinsic_value_per_share, 2),
            'wacc': wacc,
            'terminal_growth_rate': terminal_growth_rate,
            'calculation_date': datetime.now().isoformat()
        }
        
        return dcf_results
        
    except Exception as e:
        raise FinancialModelingError(f"Error performing DCF analysis: {str(e)}")


def generate_recommendation(market_price: float, intrinsic_value: float, confidence_threshold: float = 0.15) -> Dict[str, Any]:
    """
    Generate investment recommendation based on market price vs intrinsic value.
    
    Args:
        market_price: Current market price per share
        intrinsic_value: Calculated intrinsic value per share
        confidence_threshold: Threshold for recommendation confidence (default 15%)
        
    Returns:
        Dictionary containing recommendation, rationale, and confidence metrics
    """
    try:
        if market_price <= 0 or intrinsic_value <= 0:
            raise FinancialModelingError("Market price and intrinsic value must be positive")
        
        # Calculate upside/downside
        upside_potential = (intrinsic_value - market_price) / market_price
        
        # Generate recommendation
        if upside_potential > confidence_threshold:
            recommendation = "BUY"
            rationale = f"Stock appears undervalued with {upside_potential:.1%} upside potential"
        elif upside_potential < -confidence_threshold:
            recommendation = "SELL"
            rationale = f"Stock appears overvalued with {abs(upside_potential):.1%} downside risk"
        else:
            recommendation = "HOLD"
            rationale = f"Stock appears fairly valued with {upside_potential:.1%} potential return"
        
        # Calculate confidence score
        confidence_score = min(abs(upside_potential) / confidence_threshold, 1.0)
        
        recommendation_result = {
            'recommendation': recommendation,
            'rationale': rationale,
            'market_price': market_price,
            'intrinsic_value': intrinsic_value,
            'upside_potential': round(upside_potential, 4),
            'confidence_score': round(confidence_score, 2),
            'confidence_threshold': confidence_threshold,
            'analysis_date': datetime.now().isoformat()
        }
        
        return recommendation_result
        
    except Exception as e:
        raise FinancialModelingError(f"Error generating recommendation: {str(e)}")


def calculate_sensitivity_analysis(base_dcf_results: Dict[str, Any], wacc_range: Tuple[float, float], 
                                 growth_range: Tuple[float, float], forecasts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform sensitivity analysis on DCF valuation.
    
    Args:
        base_dcf_results: Base case DCF analysis results
        wacc_range: Tuple of (min_wacc, max_wacc) for sensitivity
        growth_range: Tuple of (min_growth, max_growth) for sensitivity
        forecasts: Forecasted financial statements
        
    Returns:
        Dictionary containing sensitivity analysis results
    """
    try:
        sensitivity_matrix = []
        wacc_values = [wacc_range[0] + i * (wacc_range[1] - wacc_range[0]) / 4 for i in range(5)]
        growth_values = [growth_range[0] + i * (growth_range[1] - growth_range[0]) / 4 for i in range(5)]
        
        for wacc in wacc_values:
            row = []
            for growth in growth_values:
                dcf_result = perform_dcf_analysis(forecasts, wacc, growth)
                row.append(round(dcf_result['intrinsic_value_per_share'], 2))
            sensitivity_matrix.append(row)
        
        sensitivity_results = {
            'base_case_value': base_dcf_results['intrinsic_value_per_share'],
            'wacc_range': wacc_range,
            'growth_range': growth_range,
            'wacc_values': [round(w, 3) for w in wacc_values],
            'growth_values': [round(g, 3) for g in growth_values],
            'sensitivity_matrix': sensitivity_matrix,
            'min_value': min([min(row) for row in sensitivity_matrix]),
            'max_value': max([max(row) for row in sensitivity_matrix]),
            'analysis_date': datetime.now().isoformat()
        }
        
        return sensitivity_results
        
    except Exception as e:
        raise FinancialModelingError(f"Error calculating sensitivity analysis: {str(e)}")


def validate_financial_data(data: Dict[str, Any]) -> bool:
    """
    Validate financial data structure and completeness.
    
    Args:
        data: Financial data dictionary to validate
        
    Returns:
        Boolean indicating if data is valid
    """
    required_fields = ['income_statements', 'balance_sheets', 'cash_flows']
    
    for field in required_fields:
        if field not in data:
            return False
        if not isinstance(data[field], list) or len(data[field]) == 0:
            return False
    
    # Check if income statements have required fields
    for stmt in data['income_statements']:
        if 'revenue' not in stmt:
            return False
    
    return True


def format_valuation_report(dcf_results: Dict[str, Any], recommendation: Dict[str, Any], 
                          sensitivity: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Format a comprehensive valuation report.
    
    Args:
        dcf_results: DCF analysis results
        recommendation: Investment recommendation
        sensitivity: Optional sensitivity analysis results
        
    Returns:
        Formatted valuation report
    """
    report = {
        'executive_summary': {
            'intrinsic_value': dcf_results['intrinsic_value_per_share'],
            'market_price': recommendation['market_price'],
            'recommendation': recommendation['recommendation'],
            'upside_potential': recommendation['upside_potential'],
            'confidence_score': recommendation['confidence_score']
        },
        'dcf_analysis': dcf_results,
        'investment_recommendation': recommendation,
        'report_metadata': {
            'report_date': datetime.now().isoformat(),
            'methodology': 'Discounted Cash Flow (DCF) Analysis',
            'analyst': 'Chandu Finance Agent',
            'version': '1.0.0'
        }
    }
    
    if sensitivity:
        report['sensitivity_analysis'] = sensitivity
    
    return report
