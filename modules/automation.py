import pandas as pd
from datetime import datetime, timedelta
from config import Config

class AutoActionSystem:
    """Automated alerts and actions based on financial rules"""
    
    def __init__(self):
        self.thresholds = Config.ALERT_THRESHOLDS
        self.active_alerts = []
    
    def check_alerts(self, transactions, metrics):
        """Check for alerts based on current state"""
        alerts = []
        
        if transactions.empty:
            return alerts
        
        # Check high expense alert
        category_totals = transactions.groupby('category')['amount'].sum()
        total_expenses = metrics['total_expenses']
        
        for category, amount in category_totals.items():
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
            if percentage > self.thresholds['high_expense_percentage']:
                alerts.append({
                    'type': 'high_expense',
                    'category': category,
                    'message': f"High {category} expenses: ₹{amount:,} ({percentage:.0f}% of total)",
                    'severity': 'warning'
                })
        
        # Check savings alert
        if metrics['net_savings'] < self.thresholds['savings_alert']:
            alerts.append({
                'type': 'low_savings',
                'message': f"Low savings alert: ₹{metrics['net_savings']:,} remaining",
                'severity': 'critical'
            })
        
        # Check transaction frequency
        if len(transactions) > 50:
            alerts.append({
                'type': 'high_transaction_frequency',
                'message': f"High number of transactions: {len(transactions)} this month",
                'severity': 'info'
            })
        
        # Check for unusual spending
        unusual = self._detect_unusual_spending(transactions)
        if unusual:
            alerts.append({
                'type': 'unusual_spending',
                'message': f"Unusual spending detected: {unusual['merchant']} - ₹{unusual['amount']:,}",
                'severity': 'warning'
            })
        
        self.active_alerts = alerts
        return alerts
    
    def get_active_alerts(self, transactions, metrics):
        """Get current active alerts"""
        return self.check_alerts(transactions, metrics)
    
    def process_new_transaction(self, transaction):
        """Process new transaction and trigger auto actions"""
        actions = []
        
        # Check if transaction exceeds threshold
        if transaction['amount'] > 10000:
            actions.append({
                'type': 'large_transaction_alert',
                'action': 'Send notification',
                'message': f"Large transaction detected: ₹{transaction['amount']:,} at {transaction['merchant']}"
            })
        
        # Check if in high-spending category
        if transaction['category'] in ['Shopping', 'Food & Dining'] and transaction['amount'] > 3000:
            actions.append({
                'type': 'category_alert',
                'action': 'Categorize for review',
                'message': f"High {transaction['category']} expense: ₹{transaction['amount']:,}"
            })
        
        return actions
    
    def execute_action(self, action_type, params):
        """Execute automated actions"""
        if action_type == 'send_alert':
            return self._send_alert(params.get('message', ''))
        elif action_type == 'categorize_transaction':
            return self._auto_categorize(params.get('transaction', {}))
        elif action_type == 'budget_adjustment':
            return self._adjust_budget(params.get('category', ''), params.get('amount', 0))
        else:
            return {'success': False, 'message': 'Unknown action type'}
    
    def _send_alert(self, message):
        """Send alert (simulated)"""
        print(f"ALERT: {message}")
        return {'success': True, 'message': 'Alert sent'}
    
    def _auto_categorize(self, transaction):
        """Auto-categorize transaction based on merchant"""
        # Simple rule-based categorization
        merchant = transaction.get('merchant', '').lower()
        
        rules = {
            'Food & Dining': ['restaurant', 'cafe', 'pizza', 'starbucks', 'kfc', 'mcdonald'],
            'Shopping': ['amazon', 'flipkart', 'zara', 'myntra', 'mall'],
            'Transportation': ['uber', 'ola', 'metro', 'bus', 'petrol', 'fuel'],
            'Bills & Utilities': ['electricity', 'water', 'gas', 'broadband', 'mobile']
        }
        
        for category, keywords in rules.items():
            if any(keyword in merchant for keyword in keywords):
                return {'success': True, 'category': category}
        
        return {'success': False, 'message': 'Could not auto-categorize'}
    
    def _adjust_budget(self, category, amount):
        """Adjust budget for category (simulated)"""
        return {
            'success': True,
            'category': category,
            'new_budget': amount,
            'message': f"Budget for {category} adjusted to ₹{amount:,}"
        }
    
    def _detect_unusual_spending(self, transactions):
        """Detect unusually large transactions"""
        if len(transactions) < 3:
            return None
        
        avg_spending = transactions['amount'].mean()
        std_spending = transactions['amount'].std()
        
        # Find transactions > 2 standard deviations above mean
        for idx, row in transactions.iterrows():
            if row['amount'] > avg_spending + (2 * std_spending):
                return {
                    'merchant': row['merchant'],
                    'amount': row['amount'],
                    'date': row['date']
                }
        
        return None