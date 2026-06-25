import pandas as pd
import numpy as np
from datetime import datetime
from config import Config

class AIFinancialCoach:
    """Generate intelligent financial insights and recommendations"""
    
    def __init__(self):
        self.thresholds = Config.ALERT_THRESHOLDS
    
    def generate_insights(self, transactions, metrics):
        """Generate main insights for dashboard"""
        insights = []
        
        if transactions.empty:
            return [{'type': 'info', 'message': 'Add some transactions to get personalized insights!'}]
        
        # Check high food expenses
        category_totals = transactions.groupby('category')['amount'].sum()
        total_expenses = metrics['total_expenses']
        
        if total_expenses > 0:
            food_percent = (category_totals.get('Food & Dining', 0) / total_expenses * 100)
            if food_percent > 35:
                insights.append({
                    'type': 'warning',
                    'icon': 'fas fa-utensils',
                    'title': 'High Food Expenses',
                    'message': f'You spent {food_percent:.0f}% on Food, which is more than usual (35% recommended).',
                    'action': 'Try reducing dining out by 20% next month.'
                })
        
        # Check shopping expenses
        shopping_amount = category_totals.get('Shopping', 0)
        if shopping_amount > 7000:
            insights.append({
                'type': 'warning',
                'icon': 'fas fa-shopping-bag',
                'title': 'High Shopping Alert',
                'message': f'Your shopping expenses are ₹{shopping_amount:,} this month.',
                'action': 'Consider postponing non-essential purchases.'
            })
        
        # Savings improvement
        savings_rate = metrics['savings_rate']
        if savings_rate < 20:
            insights.append({
                'type': 'info',
                'icon': 'fas fa-piggy-bank',
                'title': 'Improve Savings',
                'message': f'Your current savings rate is {savings_rate:.0f}%.',
                'action': 'Try to save at least 20% of your income.'
            })
        elif savings_rate > 30:
            insights.append({
                'type': 'success',
                'icon': 'fas fa-chart-line',
                'title': 'Excellent Savings!',
                'message': f'Great job! You\'re saving {savings_rate:.0f}% of your income.',
                'action': 'Consider investing your surplus for better returns.'
            })
        
        # Transportation check
        transport = category_totals.get('Transportation', 0)
        if transport < 5000:
            insights.append({
                'type': 'success',
                'icon': 'fas fa-car',
                'title': 'Controlled Transportation',
                'message': 'Your transportation costs are under control.',
                'action': 'Keep up the good work!'
            })
        
        # Check for bill payments
        upcoming_bills = self._check_upcoming_bills(transactions)
        if upcoming_bills:
            insights.append({
                'type': 'reminder',
                'icon': 'fas fa-bell',
                'title': 'Upcoming Bills',
                'message': f'You have {len(upcoming_bills)} bills due soon.',
                'action': 'Set up auto-pay to avoid late fees.'
            })
        
        return insights[:5]  # Return top 5 insights
    
    def generate_detailed_insights(self, transactions, metrics):
        """Generate detailed financial analysis"""
        detailed = {
            'summary': {},
            'patterns': [],
            'trends': [],
            'risks': []
        }
        
        if transactions.empty:
            return detailed
        
        # Summary
        detailed['summary'] = {
            'total_spent': metrics['total_expenses'],
            'avg_transaction': metrics['total_expenses'] / max(len(transactions), 1),
            'top_category': self._get_top_category(transactions),
            'best_day_to_save': self._find_best_saving_day(transactions)
        }
        
        # Spending patterns
        transactions['date'] = pd.to_datetime(transactions['date'])
        transactions['day_of_week'] = transactions['date'].dt.day_name()
        
        weekday_spending = transactions.groupby('day_of_week')['amount'].mean()
        detailed['patterns'] = weekday_spending.to_dict()
        
        # Trends
        if len(transactions) > 5:
            recent_avg = transactions.tail(5)['amount'].mean()
            overall_avg = transactions['amount'].mean()
            trend = 'increasing' if recent_avg > overall_avg * 1.1 else 'decreasing' if recent_avg < overall_avg * 0.9 else 'stable'
            detailed['trends'].append(f"Spending trend is {trend} compared to average.")
        
        return detailed
    
    def get_recommendations(self, transactions, metrics):
        """Get actionable recommendations"""
        recommendations = []
        
        if transactions.empty:
            return recommendations
        
        category_totals = transactions.groupby('category')['amount'].sum()
        total_expenses = metrics['total_expenses']
        
        # Category-specific recommendations
        for category, amount in category_totals.items():
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
            
            if category == 'Food & Dining' and percentage > 30:
                recommendations.append({
                    'category': category,
                    'recommendation': 'Reduce dining out by 2-3 times per week',
                    'potential_savings': amount * 0.2,
                    'priority': 'high'
                })
            elif category == 'Shopping' and amount > 5000:
                recommendations.append({
                    'category': category,
                    'recommendation': 'Wait 48 hours before making non-essential purchases',
                    'potential_savings': amount * 0.15,
                    'priority': 'medium'
                })
            elif category == 'Transportation' and amount > 3000:
                recommendations.append({
                    'category': category,
                    'recommendation': 'Consider using public transport 2 days a week',
                    'potential_savings': amount * 0.25,
                    'priority': 'medium'
                })
        
        # General recommendations
        if metrics['savings_rate'] < 15:
            recommendations.append({
                'category': 'General',
                'recommendation': 'Set up automatic transfer to savings account',
                'potential_savings': metrics['total_income'] * 0.1,
                'priority': 'high'
            })
        
        return recommendations
    
    def _get_top_category(self, transactions):
        """Get category with highest spending"""
        category_totals = transactions.groupby('category')['amount'].sum()
        return category_totals.idxmax() if not category_totals.empty else None
    
    def _find_best_saving_day(self, transactions):
        """Find which day has lowest average spending"""
        if len(transactions) < 5:
            return "Insufficient data"
        
        avg_by_day = transactions.groupby(transactions['date'].dt.day_name())['amount'].mean()
        best_day = avg_by_day.idxmin()
        return best_day
    
    def _check_upcoming_bills(self, transactions):
        """Check for upcoming recurring bills"""
        # Simplified - would need bill tracking in real implementation
        bills = transactions[transactions['category'] == 'Bills & Utilities']
        if not bills.empty:
            last_bill_date = pd.to_datetime(bills['date'].max())
            days_since = (datetime.now() - last_bill_date).days
            
            if days_since > 25:  # Assuming monthly bills
                return [{'type': 'Electricity', 'due_date': last_bill_date + pd.Timedelta(days=30)}]
        
        return []