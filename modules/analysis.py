import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FinancialAnalyzer:
    """Perform financial calculations and analysis"""
    
    def calculate_metrics(self, transactions):
        """Calculate key financial metrics"""
        if transactions.empty:
            return {
                'total_income': 0,
                'total_expenses': 0,
                'net_savings': 0,
                'avg_daily_spend': 0,
                'savings_rate': 0
            }
        
        total_expenses = transactions['amount'].sum()
        total_income = 45000  # Default monthly income (can be made dynamic)
        net_savings = total_income - total_expenses
        
        # Calculate average daily spending
        if len(transactions) > 0:
            date_range = pd.to_datetime(transactions['date']).max() - pd.to_datetime(transactions['date']).min()
            days = max(date_range.days, 1)
            avg_daily_spend = total_expenses / days
        else:
            avg_daily_spend = 0
        
        # Savings rate
        savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_savings': net_savings,
            'avg_daily_spend': avg_daily_spend,
            'savings_rate': savings_rate,
            'transaction_count': len(transactions)
        }
    
    def get_category_breakdown(self, transactions):
        """Get spending breakdown by category"""
        if transactions.empty:
            return {}
        
        category_totals = transactions.groupby('category')['amount'].sum().to_dict()
        
        # Ensure all categories are present
        all_categories = ['Food & Dining', 'Shopping', 'Transportation', 
                         'Bills & Utilities', 'Others']
        
        for cat in all_categories:
            if cat not in category_totals:
                category_totals[cat] = 0
        
        return category_totals
    
    def get_spending_trends(self, transactions):
        """Calculate spending trends over time"""
        if transactions.empty:
            return []
        
        transactions['date'] = pd.to_datetime(transactions['date'])
        transactions['week'] = transactions['date'].dt.isocalendar().week
        transactions['month'] = transactions['date'].dt.strftime('%Y-%m')
        
        # Weekly trends
        weekly_trends = transactions.groupby('week')['amount'].sum().to_dict()
        
        # Monthly trends
        monthly_trends = transactions.groupby('month')['amount'].sum().to_dict()
        
        return {
            'weekly': weekly_trends,
            'monthly': monthly_trends
        }
    
    def calculate_month_over_month_change(self, transactions):
        """Calculate month-over-month change in expenses"""
        if transactions.empty:
            return {}
        
        transactions['date'] = pd.to_datetime(transactions['date'])
        transactions['month'] = transactions['date'].dt.strftime('%Y-%m')
        
        monthly_spending = transactions.groupby('month')['amount'].sum()
        
        changes = {}
        for i in range(1, len(monthly_spending)):
            prev_month = monthly_spending.index[i-1]
            curr_month = monthly_spending.index[i]
            change_pct = ((monthly_spending[curr_month] - monthly_spending[prev_month]) 
                         / monthly_spending[prev_month] * 100)
            changes[curr_month] = round(change_pct, 2)
        
        return changes
    
    def get_top_expenses(self, transactions, n=5):
        """Get top N expenses"""
        if transactions.empty:
            return []
        
        return transactions.nlargest(n, 'amount')[['date', 'merchant', 'amount']].to_dict('records')
    
    def get_spending_patterns(self, transactions):
        """Identify spending patterns and anomalies"""
        patterns = {
            'unusual_spending': [],
            'frequent_categories': [],
            'saving_opportunities': []
        }
        
        if transactions.empty:
            return patterns
        
        # Calculate average per category
        category_avg = transactions.groupby('category')['amount'].mean()
        
        # Find unusual spending (2x average)
        for idx, row in transactions.iterrows():
            cat_avg = category_avg.get(row['category'], 0)
            if cat_avg > 0 and row['amount'] > cat_avg * 2:
                patterns['unusual_spending'].append({
                    'date': row['date'],
                    'merchant': row['merchant'],
                    'amount': row['amount'],
                    'category': row['category']
                })
        
        # Frequent spending categories
        category_counts = transactions['category'].value_counts()
        patterns['frequent_categories'] = category_counts.head(3).to_dict()
        
        return patterns