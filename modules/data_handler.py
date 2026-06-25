import pandas as pd
import os
from datetime import datetime
from config import Config

class DataHandler:
    """Handle all data operations with CSV files"""
    
    def __init__(self):
        self.transactions_file = Config.TRANSACTIONS_FILE
        self.goals_file = Config.GOALS_FILE
        self._initialize_files()
    
    def _initialize_files(self):
        """Create CSV files if they don't exist"""
        if not self.transactions_file.exists():
            self.create_sample_data()
        
        if not self.goals_file.exists():
            self._create_empty_goals_file()
    
    def create_sample_data(self):
        """Create sample transaction data for initial setup"""
        sample_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5, 6, 7, 8],
            'date': [
                '2024-04-05', '2024-04-10', '2024-04-12', '2024-04-15',
                '2024-04-18', '2024-04-20', '2024-04-22', '2024-04-25'
            ],
            'merchant': [
                'Pizza Hut', 'Amazon', 'Uber', 'Reliance Fresh',
                'Tata Power', 'Zara', 'Metro', 'Local Mart'
            ],
            'category': [
                'Food & Dining', 'Shopping', 'Transportation', 'Food & Dining',
                'Bills & Utilities', 'Shopping', 'Transportation', 'Others'
            ],
            'amount': [1850, 3500, 450, 1250, 3420, 3625, 5250, 2280],
            'description': ['', '', '', '', '', '', '', '']
        })
        sample_data.to_csv(self.transactions_file, index=False)
        return sample_data
    
    def _create_empty_goals_file(self):
        """Create empty goals CSV"""
        goals_df = pd.DataFrame(columns=['id', 'name', 'target_amount', 'current_amount', 
                                          'deadline', 'priority', 'status'])
        goals_df.to_csv(self.goals_file, index=False)
    
    def get_transactions(self):
        """Get all transactions as DataFrame"""
        try:
            return pd.read_csv(self.transactions_file)
        except:
            return self.create_sample_data()
    
    def add_transaction(self, transaction):
        """Add a new transaction"""
        try:
            df = self.get_transactions()
            new_id = df['id'].max() + 1 if not df.empty else 1
            transaction['id'] = new_id
            df = pd.concat([df, pd.DataFrame([transaction])], ignore_index=True)
            df.to_csv(self.transactions_file, index=False)
            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def delete_transaction(self, trans_id):
        """Delete a transaction by ID"""
        try:
            df = self.get_transactions()
            df = df[df['id'] != trans_id]
            df.to_csv(self.transactions_file, index=False)
            return True
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False
    
    def update_transaction(self, trans_id, updates):
        """Update a transaction"""
        try:
            df = self.get_transactions()
            df.loc[df['id'] == trans_id, updates.keys()] = updates.values()
            df.to_csv(self.transactions_file, index=False)
            return True
        except Exception as e:
            print(f"Error updating transaction: {e}")
            return False
    
    def get_goals(self):
        """Get all goals"""
        try:
            return pd.read_csv(self.goals_file)
        except:
            self._create_empty_goals_file()
            return pd.DataFrame()
    
    def save_goals(self, goals_df):
        """Save goals to CSV"""
        goals_df.to_csv(self.goals_file, index=False)