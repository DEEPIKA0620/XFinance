import pandas as pd
from datetime import datetime, timedelta
from config import Config

class GoalPlanner:
    """Manage financial goals and track progress"""
    
    def __init__(self):
        self.data_handler = None
        self.goals_file = Config.GOALS_FILE
    
    def get_all_goals(self):
        """Get all financial goals"""
        try:
            if self.goals_file.exists():
                goals_df = pd.read_csv(self.goals_file)
                return goals_df.to_dict('records')
            return []
        except:
            return []
    
    def create_goal(self, goal_data):
        """Create a new financial goal"""
        try:
            goals = self.get_all_goals()
            
            new_goal = {
                'id': len(goals) + 1 if goals else 1,
                'name': goal_data.get('name'),
                'target_amount': float(goal_data.get('target_amount', 0)),
                'current_amount': float(goal_data.get('current_amount', 0)),
                'deadline': goal_data.get('deadline'),
                'priority': goal_data.get('priority', 'medium'),
                'status': 'active',
                'created_at': datetime.now().strftime('%Y-%m-%d')
            }
            
            goals.append(new_goal)
            goals_df = pd.DataFrame(goals)
            goals_df.to_csv(self.goals_file, index=False)
            
            return new_goal
        except Exception as e:
            print(f"Error creating goal: {e}")
            return None
    
    def update_goal(self, goal_id, updates):
        """Update an existing goal"""
        try:
            goals = self.get_all_goals()
            for goal in goals:
                if goal['id'] == goal_id:
                    goal.update(updates)
                    break
            
            goals_df = pd.DataFrame(goals)
            goals_df.to_csv(self.goals_file, index=False)
            return True
        except:
            return False
    
    def delete_goal(self, goal_id):
        """Delete a goal"""
        try:
            goals = self.get_all_goals()
            goals = [g for g in goals if g['id'] != goal_id]
            goals_df = pd.DataFrame(goals) if goals else pd.DataFrame()
            goals_df.to_csv(self.goals_file, index=False)
            return True
        except:
            return False
    
    def calculate_progress(self, goal_id, transactions):
        """Calculate progress towards a goal"""
        goals = self.get_all_goals()
        goal = next((g for g in goals if g['id'] == goal_id), None)
        
        if not goal:
            return None
        
        target = goal['target_amount']
        current = goal['current_amount']
        
        # Calculate monthly savings needed
        deadline = datetime.strptime(goal['deadline'], '%Y-%m-%d')
        months_left = max(1, (deadline - datetime.now()).days / 30)
        remaining = target - current
        
        monthly_needed = remaining / months_left if remaining > 0 else 0
        
        # Check if on track (simplified)
        if transactions.empty:
            on_track = False
        else:
            recent_savings = 45000 - transactions['amount'].sum()  # Assuming income 45000
            on_track = recent_savings >= monthly_needed
        
        progress_percent = (current / target * 100) if target > 0 else 0
        
        return {
            'goal': goal,
            'progress_percent': progress_percent,
            'remaining': remaining,
            'months_left': months_left,
            'monthly_needed': monthly_needed,
            'on_track': on_track,
            'recommendation': self._get_recommendation(monthly_needed, on_track)
        }
    
    def _get_recommendation(self, monthly_needed, on_track):
        """Generate recommendation for goal achievement"""
        if on_track:
            return "You're on track to achieve this goal! Keep up the good work."
        else:
            return f"You need to save ₹{monthly_needed:,.0f} per month to reach this goal. Try reducing non-essential expenses."
    
    def suggest_goal(self, transactions):
        """Suggest a new goal based on spending patterns"""
        if transactions.empty:
            return {
                'suggestion': 'Start by tracking your expenses to set meaningful goals',
                'target': None
            }
        
        total_expenses = transactions['amount'].sum()
        current_savings = 45000 - total_expenses
        
        if current_savings > 10000:
            return {
                'suggestion': 'Emergency Fund',
                'target': 50000,
                'reason': 'You have good savings potential. Build a 3-month emergency fund.'
            }
        else:
            return {
                'suggestion': 'Reduce Expenses',
                'target': 10000,
                'reason': 'Focus on saving ₹10,000 by reducing unnecessary spending.'
            }