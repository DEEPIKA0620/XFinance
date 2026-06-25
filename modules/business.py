import pandas as pd
import numpy as np
from config import Config

class BusinessMode:
    """Business mode features for MSMEs"""
    
    def __init__(self):
        self.settings = Config.BUSINESS_SETTINGS
    
    def calculate_metrics(self, transactions):
        """Calculate business-specific metrics"""
        if transactions.empty:
            return {
                'total_revenue': 0,
                'total_expenses': 0,
                'profit': 0,
                'profit_margin': 0,
                'expense_ratio': 0,
                'operating_cashflow': 0
            }
        
        # For business, income is revenue, expenses are operational costs
        revenue = 45000 * 2  # Simulating business revenue
        expenses = transactions['amount'].sum()
        profit = revenue - expenses
        
        return {
            'total_revenue': revenue,
            'total_expenses': expenses,
            'profit': profit,
            'profit_margin': (profit / revenue * 100) if revenue > 0 else 0,
            'expense_ratio': (expenses / revenue * 100) if revenue > 0 else 0,
            'operating_cashflow': profit,
            'transaction_volume': len(transactions)
        }
    
    def calculate_gst(self, transactions):
        """Calculate GST summary"""
        total_expenses = transactions['amount'].sum() if not transactions.empty else 0
        
        # Simulate GST calculation
        gst_rate = self.settings['gst_rate']
        gst_input = total_expenses * (gst_rate / (100 + gst_rate))  # Input GST
        gst_output = 45000 * 2 * (gst_rate / 100)  # Output GST (assuming revenue)
        
        net_gst = gst_output - gst_input
        
        return {
            'gst_rate': gst_rate,
            'gst_input': gst_input,
            'gst_output': gst_output,
            'net_gst_payable': net_gst if net_gst > 0 else 0,
            'gst_refund': -net_gst if net_gst < 0 else 0,
            'gst_status': 'Payable' if net_gst > 0 else 'Refundable' if net_gst < 0 else 'No GST Due'
        }
    
    def get_insights(self, transactions, metrics):
        """Generate business insights"""
        insights = []
        
        # Profit margin check
        if metrics['profit_margin'] < self.settings['profit_margin_target']:
            insights.append({
                'type': 'warning',
                'message': f"Profit margin ({metrics['profit_margin']:.1f}%) is below target ({self.settings['profit_margin_target']}%)",
                'recommendation': 'Review operational costs or increase pricing'
            })
        else:
            insights.append({
                'type': 'success',
                'message': f"Healthy profit margin of {metrics['profit_margin']:.1f}%",
                'recommendation': 'Consider reinvesting profits for growth'
            })
        
        # Expense ratio check
        if metrics['expense_ratio'] > self.settings['expense_ratio_warning']:
            insights.append({
                'type': 'warning',
                'message': f"High expense ratio: {metrics['expense_ratio']:.1f}% of revenue",
                'recommendation': 'Look for cost reduction opportunities'
            })
        
        # Transaction analysis
        if not transactions.empty:
            avg_transaction = metrics['total_expenses'] / metrics['transaction_volume']
            insights.append({
                'type': 'info',
                'message': f"Average transaction value: ₹{avg_transaction:,.2f}",
                'recommendation': 'Consider volume discounts for frequent purchases'
            })
        
        return insights
    
    def cashflow_projection(self, transactions, months=3):
        """Project cashflow for next months"""
        if transactions.empty:
            return []
        
        avg_monthly_expenses = transactions['amount'].sum()
        avg_monthly_revenue = 45000 * 2  # Simulated
        
        projections = []
        current_cash = avg_monthly_revenue - avg_monthly_expenses
        
        for i in range(1, months + 1):
            projection = {
                'month': i,
                'projected_revenue': avg_monthly_revenue * (1 + 0.05 * i),  # 5% growth per month
                'projected_expenses': avg_monthly_expenses * (1 + 0.03 * i),  # 3% expense growth
                'projected_cashflow': current_cash * i
            }
            projections.append(projection)
        
        return projections
    
    def expense_categorization_business(self, transactions):
        """Categorize expenses for business accounting"""
        if transactions.empty:
            return {}
        
        business_categories = {
            'Office Supplies': 0,
            'Travel': 0,
            'Marketing': 0,
            'Utilities': 0,
            'Software & Tools': 0,
            'Other': 0
        }
        
        # Simple mapping (could be enhanced)
        for idx, row in transactions.iterrows():
            merchant = row['merchant'].lower()
            amount = row['amount']
            
            if any(keyword in merchant for keyword in ['amazon', 'stationery', 'office']):
                business_categories['Office Supplies'] += amount
            elif any(keyword in merchant for keyword in ['uber', 'ola', 'flight', 'hotel']):
                business_categories['Travel'] += amount
            elif any(keyword in merchant for keyword in ['google', 'facebook', 'ads']):
                business_categories['Marketing'] += amount
            elif any(keyword in merchant for keyword in ['electricity', 'water', 'internet']):
                business_categories['Utilities'] += amount
            elif any(keyword in merchant for keyword in ['software', 'subscription', 'cloud']):
                business_categories['Software & Tools'] += amount
            else:
                business_categories['Other'] += amount
        
        return business_categories