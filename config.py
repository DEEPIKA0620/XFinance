import os
from pathlib import Path

class Config:
    """Application configuration"""
    
    # Base paths
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / 'data'
    UPLOAD_DIR = BASE_DIR / 'uploads'
    OUTPUT_DIR = BASE_DIR / 'outputs'
    
    # Create directories
    DATA_DIR.mkdir(exist_ok=True)
    UPLOAD_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Data files
    TRANSACTIONS_FILE = DATA_DIR / 'transactions.csv'
    GOALS_FILE = DATA_DIR / 'goals.csv'
    SETTINGS_FILE = DATA_DIR / 'settings.json'
    
    # OCR settings
    TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
    # TESSERACT_CMD = '/usr/bin/tesseract'  # Linux/Mac
    
    # Report settings
    REPORT_TEMPLATES = BASE_DIR / 'templates' / 'reports'
    
    # Alert thresholds
    ALERT_THRESHOLDS = {
        'high_expense_percentage': 30,  # Alert if category > 30% of total
        'savings_alert': 10000,  # Alert if savings below this
        'bill_due_days': 3  # Days before bill due to alert
    }
    
    # Business mode settings
    BUSINESS_SETTINGS = {
        'gst_rate': 18,  # GST percentage
        'profit_margin_target': 20,  # Target profit margin %
        'expense_ratio_warning': 70  # Warning if expenses > 70% of income
    }
    
    # AI Coach settings
    AI_SETTINGS = {
        'max_insights': 5,
        'confidence_threshold': 0.7,
        'update_frequency_hours': 24
    }