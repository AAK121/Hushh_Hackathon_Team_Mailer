# tests/test_operons.py

"""
Test suite for HushhMCP Financial Modeling Operons
==================================================

This module tests the financial modeling operons independently
of any agent logic to ensure accurate calculations.
"""

import pytest
import json
from datetime import datetime
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hushh_mcp.operons.financial_modeling import (
    build_three_statement_model,
    perform_dcf_analysis,
    generate_recommendation,
    calculate_sensitivity_analysis,
    validate_financial_data,
    format_valuation_report,
    FinancialModelingError
)


class TestFinancialModeling:
    """Test cases for financial modeling operons."""
    
    @pytest.fixture
    def sample_financial_data(self):
        """Sample financial data for testing."""
        return {
            'ticker': 'TEST',
            'company_name': 'Test Corporation',
            'income_statements': [
                {
                    'year': 2021,
                    'revenue': 1000000000,
                    'operating_income': 200000000,
                    'ebitda': 250000000,
                    'net_income': 150000000
                },
                {
                    'year': 2022,
                    'revenue': 1100000000,
                    'operating_income': 220000000,
                    'ebitda': 275000000,
                    'net_income': 165000000
                },
                {
                    'year': 2023,
                    'revenue': 1200000000,
                    'operating_income': 240000000,
                    'ebitda': 300000000,
                    'net_income': 180000000
                }
            ],
            'balance_sheets': [
                {
                    'year': 2023,
                    'total_assets': 2000000000,
                    'total_debt': 500000000,
                    'shareholders_equity': 1200000000
                }
            ],
            'cash_flows': [
                {
                    'year': 2023,
                    'operating_cash_flow': 220000000,
                    'capex': -50000000,
                    'free_cash_flow': 170000000
                }
            ]
        }
    
    def test_validate_financial_data_valid(self, sample_financial_data):
        """Test validation of valid financial data."""
        assert validate_financial_data(sample_financial_data) == True
    
    def test_validate_financial_data_invalid(self):
        """Test validation of invalid financial data."""
        invalid_data = {'income_statements': []}  # Missing required fields
        assert validate_financial_data(invalid_data) == False
        
        invalid_data2 = {}  # Empty data
        assert validate_financial_data(invalid_data2) == False
    
    def test_build_three_statement_model(self, sample_financial_data):
        """Test three-statement model building."""
        forecasts = build_three_statement_model(sample_financial_data)
        
        # Check structure
        assert 'income_statements' in forecasts
        assert 'balance_sheets' in forecasts
        assert 'cash_flows' in forecasts
        assert 'assumptions' in forecasts
        
        # Check forecast length (should be 5 years)
        assert len(forecasts['income_statements']) == 5
        assert len(forecasts['balance_sheets']) == 5
        assert len(forecasts['cash_flows']) == 5
        
        # Check that revenues are growing
        revenues = [stmt['revenue'] for stmt in forecasts['income_statements']]
        for i in range(1, len(revenues)):
            assert revenues[i] > revenues[i-1], "Revenue should be growing"
        
        # Check that free cash flows are calculated
        for cf in forecasts['cash_flows']:
            assert 'free_cash_flow' in cf
            assert isinstance(cf['free_cash_flow'], (int, float))
    
    def test_build_three_statement_model_insufficient_data(self):
        """Test three-statement model with insufficient data."""
        insufficient_data = {
            'income_statements': [{'revenue': 1000000}],  # Only 1 year
            'balance_sheets': [],
            'cash_flows': []
        }
        
        with pytest.raises(FinancialModelingError):
            build_three_statement_model(insufficient_data)
    
    def test_perform_dcf_analysis(self, sample_financial_data):
        """Test DCF analysis calculation."""
        forecasts = build_three_statement_model(sample_financial_data)
        wacc = 0.10
        terminal_growth = 0.025
        
        dcf_results = perform_dcf_analysis(forecasts, wacc, terminal_growth)
        
        # Check structure
        required_fields = [
            'free_cash_flows', 'present_value_fcf', 'terminal_value',
            'pv_terminal_value', 'enterprise_value', 'equity_value',
            'intrinsic_value_per_share', 'wacc', 'terminal_growth_rate'
        ]
        
        for field in required_fields:
            assert field in dcf_results, f"Missing field: {field}"
        
        # Check that intrinsic value is positive
        assert dcf_results['intrinsic_value_per_share'] > 0
        
        # Check that enterprise value equals sum of PV components
        pv_fcf_sum = sum(dcf_results['present_value_fcf'])
        expected_ev = pv_fcf_sum + dcf_results['pv_terminal_value']
        assert abs(dcf_results['enterprise_value'] - expected_ev) < 0.01
        
        # Check WACC and terminal growth are stored correctly
        assert dcf_results['wacc'] == wacc
        assert dcf_results['terminal_growth_rate'] == terminal_growth
    
    def test_perform_dcf_analysis_no_cashflows(self):
        """Test DCF analysis with no cash flows."""
        empty_forecasts = {'cash_flows': []}
        
        with pytest.raises(FinancialModelingError):
            perform_dcf_analysis(empty_forecasts, 0.10, 0.025)
    
    def test_generate_recommendation_buy(self):
        """Test buy recommendation generation."""
        market_price = 80.0
        intrinsic_value = 100.0
        
        recommendation = generate_recommendation(market_price, intrinsic_value)
        
        assert recommendation['recommendation'] == 'BUY'
        assert recommendation['market_price'] == market_price
        assert recommendation['intrinsic_value'] == intrinsic_value
        assert recommendation['upside_potential'] > 0.15  # Should be > 15%
        assert 'rationale' in recommendation
        assert 'confidence_score' in recommendation
    
    def test_generate_recommendation_sell(self):
        """Test sell recommendation generation."""
        market_price = 120.0
        intrinsic_value = 100.0
        
        recommendation = generate_recommendation(market_price, intrinsic_value)
        
        assert recommendation['recommendation'] == 'SELL'
        assert recommendation['upside_potential'] < -0.15  # Should be < -15%
    
    def test_generate_recommendation_hold(self):
        """Test hold recommendation generation."""
        market_price = 102.0
        intrinsic_value = 100.0
        
        recommendation = generate_recommendation(market_price, intrinsic_value)
        
        assert recommendation['recommendation'] == 'HOLD'
        assert abs(recommendation['upside_potential']) <= 0.15  # Should be within ±15%
    
    def test_generate_recommendation_invalid_prices(self):
        """Test recommendation with invalid prices."""
        with pytest.raises(FinancialModelingError):
            generate_recommendation(0, 100)  # Zero market price
        
        with pytest.raises(FinancialModelingError):
            generate_recommendation(100, -50)  # Negative intrinsic value
    
    def test_calculate_sensitivity_analysis(self, sample_financial_data):
        """Test sensitivity analysis calculation."""
        forecasts = build_three_statement_model(sample_financial_data)
        base_dcf = perform_dcf_analysis(forecasts, 0.10, 0.025)
        
        wacc_range = (0.08, 0.12)
        growth_range = (0.02, 0.03)
        
        sensitivity = calculate_sensitivity_analysis(
            base_dcf, wacc_range, growth_range, forecasts
        )
        
        # Check structure
        assert 'sensitivity_matrix' in sensitivity
        assert 'wacc_values' in sensitivity
        assert 'growth_values' in sensitivity
        assert 'min_value' in sensitivity
        assert 'max_value' in sensitivity
        
        # Check matrix dimensions (should be 5x5)
        assert len(sensitivity['sensitivity_matrix']) == 5
        assert all(len(row) == 5 for row in sensitivity['sensitivity_matrix'])
        
        # Check that min and max values are correctly calculated
        all_values = [val for row in sensitivity['sensitivity_matrix'] for val in row]
        assert sensitivity['min_value'] == min(all_values)
        assert sensitivity['max_value'] == max(all_values)
    
    def test_format_valuation_report(self, sample_financial_data):
        """Test valuation report formatting."""
        forecasts = build_three_statement_model(sample_financial_data)
        dcf_results = perform_dcf_analysis(forecasts, 0.10, 0.025)
        recommendation = generate_recommendation(100.0, dcf_results['intrinsic_value_per_share'])
        
        report = format_valuation_report(dcf_results, recommendation)
        
        # Check main sections
        assert 'executive_summary' in report
        assert 'dcf_analysis' in report
        assert 'investment_recommendation' in report
        assert 'report_metadata' in report
        
        # Check executive summary
        summary = report['executive_summary']
        assert 'intrinsic_value' in summary
        assert 'recommendation' in summary
        assert 'upside_potential' in summary
        
        # Check metadata
        metadata = report['report_metadata']
        assert metadata['analyst'] == 'Chandu Finance Agent'
        assert metadata['methodology'] == 'Discounted Cash Flow (DCF) Analysis'
    
    def test_format_valuation_report_with_sensitivity(self, sample_financial_data):
        """Test valuation report with sensitivity analysis."""
        forecasts = build_three_statement_model(sample_financial_data)
        dcf_results = perform_dcf_analysis(forecasts, 0.10, 0.025)
        recommendation = generate_recommendation(100.0, dcf_results['intrinsic_value_per_share'])
        sensitivity = calculate_sensitivity_analysis(
            dcf_results, (0.08, 0.12), (0.02, 0.03), forecasts
        )
        
        report = format_valuation_report(dcf_results, recommendation, sensitivity)
        
        assert 'sensitivity_analysis' in report
        assert report['sensitivity_analysis'] == sensitivity


class TestFinancialModelingIntegration:
    """Integration tests for the complete financial modeling workflow."""
    
    @pytest.fixture
    def complete_workflow_data(self):
        """Complete data for workflow testing."""
        return {
            'ticker': 'AAPL',
            'company_name': 'Apple Inc.',
            'income_statements': [
                {
                    'year': 2021,
                    'revenue': 365817000000,
                    'operating_income': 108949000000,
                    'ebitda': 123136000000,
                    'net_income': 94680000000
                },
                {
                    'year': 2022,
                    'revenue': 394328000000,
                    'operating_income': 119437000000,
                    'ebitda': 130541000000,
                    'net_income': 99803000000
                },
                {
                    'year': 2023,
                    'revenue': 383285000000,
                    'operating_income': 114301000000,
                    'ebitda': 125820000000,
                    'net_income': 96995000000
                }
            ],
            'balance_sheets': [
                {
                    'year': 2023,
                    'total_assets': 352755000000,
                    'total_debt': 123930000000,
                    'shareholders_equity': 62146000000
                }
            ],
            'cash_flows': [
                {
                    'year': 2023,
                    'operating_cash_flow': 110543000000,
                    'capex': -10959000000,
                    'free_cash_flow': 99584000000
                }
            ]
        }
    
    def test_complete_valuation_workflow(self, complete_workflow_data):
        """Test the complete valuation workflow."""
        # Step 1: Validate data
        assert validate_financial_data(complete_workflow_data)
        
        # Step 2: Build forecasts
        forecasts = build_three_statement_model(complete_workflow_data)
        assert forecasts is not None
        
        # Step 3: Perform DCF
        dcf_results = perform_dcf_analysis(forecasts, 0.09, 0.025)
        assert dcf_results['intrinsic_value_per_share'] > 0
        
        # Step 4: Generate recommendation
        market_price = 150.0  # Example market price
        recommendation = generate_recommendation(market_price, dcf_results['intrinsic_value_per_share'])
        assert recommendation['recommendation'] in ['BUY', 'HOLD', 'SELL']
        
        # Step 5: Format report
        report = format_valuation_report(dcf_results, recommendation)
        assert 'executive_summary' in report
        
        # Step 6: Sensitivity analysis
        sensitivity = calculate_sensitivity_analysis(
            dcf_results, (0.07, 0.11), (0.02, 0.03), forecasts
        )
        assert 'sensitivity_matrix' in sensitivity
        
        print(f"✅ Complete workflow test passed!")
        print(f"   Intrinsic Value: ${dcf_results['intrinsic_value_per_share']:.2f}")
        print(f"   Market Price: ${market_price:.2f}")
        print(f"   Recommendation: {recommendation['recommendation']}")


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
