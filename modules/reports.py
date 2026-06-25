import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF
from config import Config

class ReportGenerator:
    """Generate financial reports in various formats"""
    
    def __init__(self):
        self.output_dir = Config.OUTPUT_DIR
    
    def generate_report(self, transactions, metrics, report_type, month):
        """Generate financial report"""
        if report_type == 'summary':
            return self._generate_summary_report(transactions, metrics, month)
        elif report_type == 'detailed':
            return self._generate_detailed_report(transactions, metrics, month)
        elif report_type == 'category':
            return self._generate_category_report(transactions, month)
        else:
            return self._generate_summary_report(transactions, metrics, month)
    
    def _generate_summary_report(self, transactions, metrics, month):
        """Generate summary report PDF"""
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"XFinance Summary Report - {month}", ln=True, align='C')
        pdf.ln(10)
        
        # Date
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
        pdf.ln(10)
        
        # Financial Summary
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Financial Summary", ln=True)
        pdf.set_font("Arial", size=10)
        
        pdf.cell(0, 8, f"Total Income: ₹{metrics['total_income']:,.2f}", ln=True)
        pdf.cell(0, 8, f"Total Expenses: ₹{metrics['total_expenses']:,.2f}", ln=True)
        pdf.cell(0, 8, f"Net Savings: ₹{metrics['net_savings']:,.2f}", ln=True)
        pdf.cell(0, 8, f"Savings Rate: {metrics['savings_rate']:.1f}%", ln=True)
        pdf.cell(0, 8, f"Number of Transactions: {metrics['transaction_count']}", ln=True)
        pdf.ln(10)
        
        # Category Breakdown
        if not transactions.empty:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Category Breakdown", ln=True)
            pdf.set_font("Arial", size=10)
            
            category_totals = transactions.groupby('category')['amount'].sum()
            for category, amount in category_totals.items():
                percentage = (amount / metrics['total_expenses'] * 100) if metrics['total_expenses'] > 0 else 0
                pdf.cell(0, 8, f"{category}: ₹{amount:,.2f} ({percentage:.1f}%)", ln=True)
        
        # Save PDF
        filename = f"xfinance_summary_{month}.pdf"
        filepath = self.output_dir / filename
        pdf.output(str(filepath))
        
        return str(filepath)
    
    def _generate_detailed_report(self, transactions, metrics, month):
        """Generate detailed transaction report"""
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"XFinance Detailed Report - {month}", ln=True, align='C')
        pdf.ln(10)
        
        # Summary
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Summary", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 8, f"Total Transactions: {len(transactions)}", ln=True)
        pdf.cell(0, 8, f"Total Amount: ₹{metrics['total_expenses']:,.2f}", ln=True)
        pdf.cell(0, 8, f"Average Transaction: ₹{metrics['total_expenses']/len(transactions) if len(transactions) > 0 else 0:,.2f}", ln=True)
        pdf.ln(10)
        
        # Transaction List
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Transaction Details", ln=True)
        pdf.set_font("Arial", size=8)
        
        # Table header
        pdf.cell(40, 8, "Date", 1)
        pdf.cell(60, 8, "Merchant", 1)
        pdf.cell(50, 8, "Category", 1)
        pdf.cell(40, 8, "Amount", 1)
        pdf.ln()
        
        # Table content
        for idx, row in transactions.iterrows():
            pdf.cell(40, 8, row['date'], 1)
            pdf.cell(60, 8, row['merchant'][:30], 1)
            pdf.cell(50, 8, row['category'], 1)
            pdf.cell(40, 8, f"₹{row['amount']:,.2f}", 1)
            pdf.ln()
        
        # Save PDF
        filename = f"xfinance_detailed_{month}.pdf"
        filepath = self.output_dir / filename
        pdf.output(str(filepath))
        
        return str(filepath)
    
    def _generate_category_report(self, transactions, month):
        """Generate category analysis report"""
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"XFinance Category Analysis - {month}", ln=True, align='C')
        pdf.ln(10)
        
        if not transactions.empty:
            category_totals = transactions.groupby('category')['amount'].sum()
            total_expenses = category_totals.sum()
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Spending by Category", ln=True)
            pdf.set_font("Arial", size=10)
            
            for category, amount in category_totals.items():
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                pdf.cell(0, 8, f"{category}:", ln=True)
                pdf.cell(20, 8, "")
                pdf.cell(0, 8, f"  Amount: ₹{amount:,.2f}", ln=True)
                pdf.cell(20, 8, "")
                pdf.cell(0, 8, f"  Percentage: {percentage:.1f}%", ln=True)
                pdf.ln(2)
            
            # Recommendations
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Recommendations", ln=True)
            pdf.set_font("Arial", size=10)
            
            for category, amount in category_totals.items():
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                if percentage > 30:
                    pdf.cell(0, 8, f"• High {category} expenses: Consider reducing by 20%", ln=True)
                elif category == 'Food & Dining' and percentage > 25:
                    pdf.cell(0, 8, f"• Try cooking at home more often to reduce {category} costs", ln=True)
        
        # Save PDF
        filename = f"xfinance_category_{month}.pdf"
        filepath = self.output_dir / filename
        pdf.output(str(filepath))
        
        return str(filepath)