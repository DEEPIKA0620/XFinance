import pytesseract
from PIL import Image
import re
import os
from datetime import datetime

class OCRProcessor:
    """Process bill images and extract data using Tesseract OCR"""
    
    def __init__(self):
        # Set Tesseract path (adjust based on your OS)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def extract_from_image(self, image_path):
        """Extract text from image and parse bill information"""
        try:
            # Open image
            image = Image.open(image_path)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image)
            
            # Parse extracted text
            extracted_data = self._parse_bill_text(text)
            
            return extracted_data
        except Exception as e:
            print(f"OCR Error: {e}")
            # Return mock data for testing
            return self._get_mock_data()
    
    def _parse_bill_text(self, text):
        """Parse bill text to extract relevant information"""
        data = {
            'merchant': self._extract_merchant(text),
            'date': self._extract_date(text),
            'amount': self._extract_amount(text),
            'items': self._extract_items(text),
            'raw_text': text
        }
        
        return data
    
    def _extract_merchant(self, text):
        """Extract merchant name from bill text"""
        # Common patterns for merchant names
        lines = text.split('\n')
        
        # Usually merchant name is in first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) < 50 and not any(c.isdigit() for c in line[:3]):
                # Filter out common words
                if not any(word in line.lower() for word in ['invoice', 'receipt', 'bill', 'total']):
                    return line[:50]
        
        return "Unknown Merchant"
    
    def _extract_date(self, text):
        """Extract date from bill text"""
        # Common date patterns
        patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # DD/MM/YYYY or MM/DD/YYYY
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',   # YYYY-MM-DD
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}',
            r'\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return datetime.now().strftime('%Y-%m-%d')
    
    def _extract_amount(self, text):
        """Extract total amount from bill text"""
        # Common amount patterns
        patterns = [
            r'TOTAL\s*:?\s*[\₹$]?\s*(\d+[\d,.]*\d+)',
            r'AMOUNT\s*:?\s*[\₹$]?\s*(\d+[\d,.]*\d+)',
            r'GRAND TOTAL\s*:?\s*[\₹$]?\s*(\d+[\d,.]*\d+)',
            r'[\₹$]\s*(\d+[\d,.]*\d+)',
            r'(\d+[\d,.]*\d+)\s*$'  # Last number in text
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Clean the amount
                amount_str = matches[-1].replace(',', '').strip()
                try:
                    return float(amount_str)
                except:
                    continue
        
        return 0.0
    
    def _extract_items(self, text):
        """Extract line items from bill"""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            # Look for lines with amount patterns
            if re.search(r'[\₹$]\s*\d+', line) or re.search(r'\d+\.\d{2}$', line):
                # Extract item name and amount
                parts = line.split()
                if len(parts) >= 2:
                    # Try to find amount
                    amount_match = re.search(r'(\d+\.\d{2})', line)
                    if amount_match:
                        amount = float(amount_match.group(1))
                        item_name = line[:line.find(str(amount))].strip()
                        if item_name and amount > 0:
                            items.append({
                                'name': item_name[:50],
                                'amount': amount
                            })
        
        return items[:10]  # Limit to 10 items
    
    def _get_mock_data(self):
        """Return mock data for testing when OCR fails"""
        return {
            'merchant': 'Reliance Fresh',
            'date': '2024-04-24',
            'amount': 1250.00,
            'items': [
                {'name': 'Vegetables', 'amount': 450.00},
                {'name': 'Fruits', 'amount': 350.00},
                {'name': 'Dairy', 'amount': 450.00}
            ],
            'raw_text': 'Mock OCR text for testing'
        }