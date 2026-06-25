from flask import Flask, jsonify, request, send_file, session, render_template
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import json
import os
import io
import re
from PIL import Image
import pytesseract
import pdf2image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import hashlib
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'
CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)

# User database (in-memory, replace with actual database in production)
users = {}
sessions = {}

# Data storage for each user
user_data = {}

# Initialize with demo user
demo_user_id = str(uuid.uuid4())
users['demo@xfinance.com'] = {
    'id': demo_user_id,
    'email': 'demo@xfinance.com',
    'password': bcrypt.generate_password_hash('demo123').decode('utf-8'),
    'name': 'Demo User',
    'created_at': datetime.now().isoformat()
}

# Initialize demo user data
user_data[demo_user_id] = {
    'personal_transactions': [
        {"id": 1, "desc": "Salary", "amount": 75000, "type": "income", "category": "Income", "date": datetime.now().strftime("%Y-%m-%d")},
        {"id": 2, "desc": "Rent", "amount": 18000, "type": "expense", "category": "Bills & Utilities", "date": datetime.now().strftime("%Y-%m-%d")},
        {"id": 3, "desc": "Groceries", "amount": 5500, "type": "expense", "category": "Food & Dining", "date": datetime.now().strftime("%Y-%m-%d")},
        {"id": 4, "desc": "Shopping", "amount": 3500, "type": "expense", "category": "Shopping", "date": datetime.now().strftime("%Y-%m-%d")}
    ],
    'financial_goals': [],
    'recent_actions': [],
    'business_revenue': [
        {"id": 1, "source": "Product Sales", "amount": 50000, "period": "daily", "date": datetime.now().strftime("%Y-%m-%d")},
        {"id": 2, "source": "Consulting Services", "amount": 25000, "period": "weekly", "date": datetime.now().strftime("%Y-%m-%d")}
    ],
    'business_expenses': [
        {"id": 1, "category": "Rent", "desc": "Office Rent", "amount": 25000, "date": datetime.now().strftime("%Y-%m-%d")},
        {"id": 2, "category": "Salaries", "desc": "Staff Salary", "amount": 45000, "date": datetime.now().strftime("%Y-%m-%d")},
        {"id": 3, "category": "Utilities", "desc": "Electricity Bill", "amount": 5000, "date": datetime.now().strftime("%Y-%m-%d")},
        {"id": 4, "category": "Inventory", "desc": "Raw Materials", "amount": 15000, "date": datetime.now().strftime("%Y-%m-%d")}
    ]
}

# Helper functions
def get_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'personal_transactions': [],
            'financial_goals': [],
            'recent_actions': [],
            'business_revenue': [],
            'business_expenses': []
        }
    return user_data[user_id]

# OCR Functions
def extract_text_from_image(image_file):
    """Extract text from image using Tesseract OCR"""
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

def extract_bill_details(text):
    """Extract merchant, amount, and date from OCR text"""
    details = {
        'merchant': None,
        'amount': None,
        'date': None
    }
    
    # Extract amount (looking for currency patterns)
    amount_patterns = [
        r'Total[:\s]*₹?\s*([\d,]+\.?\d*)',
        r'Amount[:\s]*₹?\s*([\d,]+\.?\d*)',
        r'Grand Total[:\s]*₹?\s*([\d,]+\.?\d*)',
        r'₹\s*([\d,]+\.?\d*)',
        r'([\d,]+\.?\d*)\s*INR'
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                details['amount'] = float(amount_str)
                break
            except:
                pass
    
    # Extract merchant (look for business names at top)
    lines = text.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if len(line) > 3 and len(line) < 50 and not any(c.isdigit() for c in line):
            if any(word in line.lower() for word in ['store', 'shop', 'cafe', 'restaurant', 'mart', 'supermarket']):
                details['merchant'] = line
                break
            elif not details['merchant'] and len(line) > 5:
                details['merchant'] = line
    
    # Extract date
    date_patterns = [
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{4}-\d{1,2}-\d{1,2})',
        r'Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            details['date'] = match.group(1)
            break
    
    if not details['date']:
        details['date'] = datetime.now().strftime("%Y-%m-%d")
    
    if not details['merchant']:
        details['merchant'] = "Unknown Merchant"
    
    if not details['amount']:
        details['amount'] = 0
    
    return details

# Routes
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', '')
        
        if email in users:
            return jsonify({'success': False, 'error': 'Email already registered'}), 400
        
        user_id = str(uuid.uuid4())
        users[email] = {
            'id': user_id,
            'email': email,
            'password': bcrypt.generate_password_hash(password).decode('utf-8'),
            'name': name,
            'created_at': datetime.now().isoformat()
        }
        
        # Initialize user data
        user_data[user_id] = {
            'personal_transactions': [],
            'financial_goals': [],
            'recent_actions': [],
            'business_revenue': [],
            'business_expenses': []
        }
        
        return jsonify({'success': True, 'message': 'User created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if email not in users:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        user = users[email]
        if not bcrypt.check_password_hash(user['password'], password):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        session_token = str(uuid.uuid4())
        sessions[session_token] = user['id']
        
        return jsonify({
            'success': True,
            'token': session_token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/verify', methods=['POST'])
def verify():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token not in sessions:
            return jsonify({'success': False, 'error': 'Invalid session'}), 401
        
        user_id = sessions[token]
        return jsonify({'success': True, 'user_id': user_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token in sessions:
            del sessions[token]
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Personal Finance Routes
@app.route('/api/personal/transactions', methods=['GET'])
def get_personal_transactions():
    try:
        user_id = get_user_from_token()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = get_user_data(user_id)
        return jsonify({'success': True, 'transactions': data['personal_transactions']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/personal/transactions', methods=['POST'])
def add_personal_transaction():
    try:
        user_id = get_user_from_token()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        new_transaction = {
            'id': int(datetime.now().timestamp() * 1000),
            'desc': data.get('desc'),
            'amount': float(data.get('amount')),
            'type': data.get('type'),
            'category': data.get('category'),
            'date': data.get('date', datetime.now().strftime("%Y-%m-%d"))
        }
        
        user_data[user_id]['personal_transactions'].append(new_transaction)
        return jsonify({'success': True, 'transaction': new_transaction})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/personal/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_personal_transaction(transaction_id):
    try:
        user_id = get_user_from_token()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        user_data[user_id]['personal_transactions'] = [
            t for t in user_data[user_id]['personal_transactions'] if t['id'] != transaction_id
        ]
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/personal/goals', methods=['GET', 'POST', 'DELETE'])
def manage_personal_goals():
    try:
        user_id = get_user_from_token()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        if request.method == 'GET':
            return jsonify({'success': True, 'goals': user_data[user_id]['financial_goals']})
        elif request.method == 'POST':
            goal = request.json
            goal['id'] = int(datetime.now().timestamp() * 1000)
            user_data[user_id]['financial_goals'].append(goal)
            return jsonify({'success': True, 'goal': goal})
        elif request.method == 'DELETE':
            goal_id = request.json.get('id')
            user_data[user_id]['financial_goals'] = [
                g for g in user_data[user_id]['financial_goals'] if g['id'] != goal_id
            ]
            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/personal/stats', methods=['GET'])
def get_personal_stats():
    try:
        user_id = get_user_from_token()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        transactions = user_data[user_id]['personal_transactions']
        income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        
        categories = {}
        for t in transactions:
            if t['type'] == 'expense':
                categories[t['category']] = categories.get(t['category'], 0) + t['amount']
        
        return jsonify({
            'success': True,
            'income': income,
            'expense': expense,
            'savings': income - expense,
            'savings_rate': ((income - expense) / income * 100) if income > 0 else 0,
            'categories': categories
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Business Finance Routes
@app.route('/api/business/revenue', methods=['GET', 'POST'])
def manage_revenue():
    try:
        user_id = get_user_from_token()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        if request.method == 'GET':
            return jsonify({'success': True, 'revenue': user_data[user_id]['business_revenue']})
        else:
            revenue = request.json
            revenue['id'] = int(datetime.now().timestamp() * 1000)
            revenue['date'] = datetime.now().strftime("%Y-%m-%d")
            user_data[user_id]['business_revenue'].append(revenue)
            return jsonify({'success': True, 'revenue': revenue})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/business/expenses', methods=['GET', 'POST'])
def manage_business_expenses():
    try:
        user_id = get_user_from_token()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        if request.method == 'GET':
            return jsonify({'success': True, 'expenses': user_data[user_id]['business_expenses']})
        else:
            expense = request.json
            expense['id'] = int(datetime.now().timestamp() * 1000)
            expense['date'] = datetime.now().strftime("%Y-%m-%d")
            user_data[user_id]['business_expenses'].append(expense)
            return jsonify({'success': True, 'expense': expense})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/business/stats', methods=['GET'])
def get_business_stats():
    try:
        user_id = get_user_from_token()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        revenue_total = sum(r['amount'] for r in user_data[user_id]['business_revenue'])
        expense_total = sum(e['amount'] for e in user_data[user_id]['business_expenses'])
        profit = revenue_total - expense_total
        margin = (profit / revenue_total * 100) if revenue_total > 0 else 0
        
        categories = {}
        for e in user_data[user_id]['business_expenses']:
            categories[e['category']] = categories.get(e['category'], 0) + e['amount']
        
        return jsonify({
            'success': True,
            'revenue': revenue_total,
            'expenses': expense_total,
            'profit': profit,
            'margin': margin,
            'categories': categories
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# OCR Route
@app.route('/api/ocr/scan', methods=['POST'])
def scan_bill():
    try:
        user_id = get_user_from_token()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        
        # Save temporarily
        temp_path = f"/tmp/{uuid.uuid4()}.jpg"
        file.save(temp_path)
        
        # Extract text using OCR
        extracted_text = extract_text_from_image(open(temp_path, 'rb'))
        
        # Parse bill details
        bill_details = extract_bill_details(extracted_text)
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'merchant': bill_details['merchant'],
            'amount': bill_details['amount'],
            'date': bill_details['date'],
            'raw_text': extracted_text[:500]  # Send first 500 chars for debugging
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Report Generation
@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    try:
        user_id = get_user_from_token()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        report_type = data.get('type', 'personal')
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#3b82f6'), spaceAfter=30)
        story.append(Paragraph(f"XFinance {report_type.title()} Report", title_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        if report_type == 'personal':
            transactions = user_data[user_id]['personal_transactions']
            income = sum(t['amount'] for t in transactions if t['type'] == 'income')
            expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
            
            summary_data = [
                ['Metric', 'Amount (₹)'],
                ['Total Income', f'₹{income:,.2f}'],
                ['Total Expenses', f'₹{expense:,.2f}'],
                ['Net Savings', f'₹{income - expense:,.2f}']
            ]
            
            summary_table = Table(summary_data, colWidths=[200, 200])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
        
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'xfinance_{report_type}_report_{datetime.now().strftime("%Y%m%d")}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Action History
@app.route('/api/actions', methods=['GET', 'POST'])
def manage_actions():
    try:
        user_id = get_user_from_token()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        if request.method == 'GET':
            return jsonify({'success': True, 'actions': user_data[user_id]['recent_actions']})
        else:
            action = request.json
            action['id'] = int(datetime.now().timestamp() * 1000)
            action['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_data[user_id]['recent_actions'].insert(0, action)
            if len(user_data[user_id]['recent_actions']) > 10:
                user_data[user_id]['recent_actions'] = user_data[user_id]['recent_actions'][:10]
            return jsonify({'success': True, 'action': action})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return render_template('dashboard.html')


def get_user_from_token():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:]
    return sessions.get(token)

if __name__ == '__main__':
    print("🚀 XFinance Backend Server Starting...")
    print("📊 API available at: http://localhost:5000")
    print("🔐 Endpoints: /api/login, /api/signup, /api/ocr/scan")
    app.run(debug=True, port=5000)