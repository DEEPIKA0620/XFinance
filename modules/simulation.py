import pandas as pd
import numpy as np

class WhatIfSimulator:
    """Run what-if scenarios for financial planning"""
    
    def simulate_spending_change(self, transactions, category, percentage_change):
        """Simulate changing spending in a category"""
        if transactions.empty:
            return {'error': 'No transaction data available'}
        
        # Calculate current metrics
        current_total = transactions['amount'].sum()
        current_category_total = transactions[transactions['category'] == category]['amount'].sum() if category else 0
        
        # Apply change
        if category:
            # Change specific category
            change_factor = 1 + (percentage_change / 100)
            new_category_total = current_category_total * change_factor
            
            # Adjust total expenses
            new_total = current_total - current_category_total + new_category_total
        else:
            # Change all expenses
            change_factor = 1 + (percentage_change / 100)
            new_total = current_total * change_factor
        
        # Calculate impact
        income = 45000  # Default monthly income
        current_savings = income - current_total
        new_savings = income - new_total
        
        result = {
            'current': {
                'total_expenses': current_total,
                'category_expense': current_category_total if category else None,
                'savings': current_savings,
                'savings_rate': (current_savings / income * 100) if income > 0 else 0
            },
            'simulated': {
                'total_expenses': new_total,
                'category_expense': new_category_total if category else None,
                'savings': new_savings,
                'savings_rate': (new_savings / income * 100) if income > 0 else 0
            },
            'impact': {
                'savings_change': new_savings - current_savings,
                'savings_change_percent': ((new_savings - current_savings) / current_savings * 100) if current_savings != 0 else 0,
                'monthly_impact': (new_savings - current_savings) / 1  # Per month
            }
        }
        
        # Add recommendations based on simulation
        if result['impact']['savings_change'] > 0:
            result['recommendation'] = f"Great! This change would increase your savings by ₹{result['impact']['savings_change']:,.0f} per month."
        else:
            result['recommendation'] = f"This would decrease your savings by ₹{abs(result['impact']['savings_change']):,.0f} per month. Consider a smaller adjustment."
        
        return result
    
    def simulate_income_change(self, transactions, new_income):
        """Simulate change in income"""
        if transactions.empty:
            return {'error': 'No transaction data available'}
        
        current_expenses = transactions['amount'].sum()
        current_income = 45000  # Default
        
        current_savings = current_income - current_expenses
        new_savings = new_income - current_expenses
        
        return {
            'current_income': current_income,
            'new_income': new_income,
            'current_savings': current_savings,
            'new_savings': new_savings,
            'improvement': new_savings - current_savings,
            'recommendation': f"Increasing income to ₹{new_income:,} would add ₹{new_savings - current_savings:,} to your savings."
        }
    
    def simulate_investment_scenario(self, transactions, investment_amount, rate_of_return, years):
        """Simulate investment growth"""
        current_savings = 45000 - transactions['amount'].sum()
        
        # Calculate future value
        future_value = investment_amount * (1 + rate_of_return/100) ** years
        
        return {
            'investment_amount': investment_amount,
            'rate_of_return': rate_of_return,
            'years': years,
            'future_value': future_value,
            'total_gain': future_value - investment_amount,
            'recommendation': f"Investing ₹{investment_amount:,} at {rate_of_return}% for {years} years could grow to ₹{future_value:,.0f}."
        }
    
    def simulate_budget_optimization(self, transactions):
        """Optimize budget across categories"""
        if transactions.empty:
            return {'error': 'No transaction data'}
        
        category_totals = transactions.groupby('category')['amount'].sum()
        total_expenses = category_totals.sum()
        
        # Recommended budget percentages
        ideal_budget = {
            'Food & Dining': 25,
            'Shopping': 15,
            'Transportation': 10,
            'Bills & Utilities': 20,
            'Others': 30
        }
        
        optimization = []
        for category, current_amount in category_totals.items():
            current_percent = (current_amount / total_expenses * 100) if total_expenses > 0 else 0
            ideal_percent = ideal_budget.get(category, 15)
            
            if current_percent > ideal_percent * 1.2:
                reduction_needed = current_amount * (current_percent - ideal_percent) / 100
                optimization.append({
                    'category': category,
                    'current_percent': current_percent,
                    'ideal_percent': ideal_percent,
                    'reduction_needed': reduction_needed,
                    'action': f"Reduce {category} by {reduction_needed:,.0f} per month"
                })
        
        total_potential_savings = sum(item['reduction_needed'] for item in optimization)
        
        return {
            'optimizations': optimization,
            'total_potential_savings': total_potential_savings,
            'new_savings_rate': ((45000 - total_expenses + total_potential_savings) / 45000 * 100)
        }