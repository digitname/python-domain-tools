from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
from flask_caching import Cache
import sqlite3
import csv
import io
import openpyxl
import pyotp
from domain_extractor import extract_domains, validate_domain, categorize_domain, add_custom_rule, remove_custom_rule, custom_rules, load_custom_rules
from auth import User, init_auth_db, add_user, login_manager
import logging
from collections import Counter
from flask_paginate import Pagination

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure random key
login_manager.init_app(app)

# Cache configuration
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'

mail = Mail(app)

limiter = Limiter(app, key_func=get_remote_address)

logging.basicConfig(filename='app.log', level=logging.INFO)

def init_db():
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS domains
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, domain TEXT UNIQUE, category TEXT)''')
    conn.commit()
    conn.close()
    init_auth_db()

def save_domains(domains):
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    for domain in domains:
        if validate_domain(domain):
            category = categorize_domain(domain)
            c.execute("INSERT OR IGNORE INTO domains (domain, category) VALUES (?, ?)", (domain, category))
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    domains = []
    if request.method == 'POST':
        text = request.form['text']
        file_type = request.form['file_type']
        domains = extract_domains(text, file_type)
        save_domains(domains)
    return render_template('index.html', domains=domains)

@app.route('/search', methods=['GET'])
@login_required
@cache.cached(timeout=300, query_string=True)
def search():
    query = request.args.get('query', '')
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    c.execute("SELECT domain, category FROM domains WHERE domain LIKE ?", (f'%{query}%',))
    domains = [{'domain': row[0], 'category': row[1]} for row in c.fetchall()]
    conn.close()
    return render_template('index.html', domains=domains, search_query=query)

@app.route('/export', methods=['GET'])
@login_required
@cache.cached(timeout=300, query_string=True)
def export():
    format = request.args.get('format', 'csv')
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    c.execute("SELECT domain, category FROM domains")
    domains = [{'domain': row[0], 'category': row[1]} for row in c.fetchall()]
    conn.close()

    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Domain', 'Category'])
        writer.writerows([[d['domain'], d['category']] for d in domains])
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            attachment_filename='domains.csv'
        )
    elif format == 'json':
        return jsonify(domains)
    elif format == 'excel':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['Domain', 'Category'])
        for domain in domains:
            ws.append([domain['domain'], domain['category']])
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            attachment_filename='domains.xlsx'
        )

@app.route('/api/domains', methods=['GET'])
@login_required
@limiter.limit("100 per day")
@cache.cached(timeout=300)
def api_domains():
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    c.execute("SELECT domain, category FROM domains")
    domains = [{'domain': row[0], 'category': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(domains)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_by_username(username)
        if user and user.check_password(password):
            if user.two_factor_secret:
                session['user_id'] = user.id
                return redirect(url_for('two_factor_auth'))
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/two_factor_auth', methods=['GET', 'POST'])
def two_factor_auth():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.get(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        token = request.form['token']
        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(token):
            login_user(user)
            session.pop('user_id', None)
            return redirect(url_for('index'))
        flash('Invalid token')
    
    return render_template('two_factor_auth.html')

@app.route('/enable_2fa', methods=['GET', 'POST'])
@login_required
def enable_2fa():
    if request.method == 'POST':
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        token = request.form['token']
        if totp.verify(token):
            current_user.set_two_factor_secret(secret)
            flash('Two-factor authentication enabled successfully')
            return redirect(url_for('index'))
        flash('Invalid token')
    
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    qr_code = totp.provisioning_uri(current_user.username, issuer_name="Domain Extractor")
    return render_template('enable_2fa.html', qr_code=qr_code, secret=secret)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/bulk_import', methods=['GET', 'POST'])
@login_required
def bulk_import():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            try:
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_reader = csv.reader(stream)
                domains = [row[0] for row in csv_reader if row]
                save_domains(domains)
                flash(f'Successfully imported {len(domains)} domains')
                
                # Send email notification
                msg = Message("Bulk Import Results",
                              recipients=[current_user.email])
                msg.body = f"Your bulk import has been completed. {len(domains)} domains were successfully imported."
                mail.send(msg)
                
            except Exception as e:
                logging.error(f'Error during bulk import: {str(e)}')
                flash('Error during import. Please check the file format.')
        else:
            flash('Please upload a CSV file')
    return render_template('bulk_import.html')

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))
    
    # Add admin functionality here
    return render_template('admin.html')

@app.route('/statistics')
@login_required
@cache.cached(timeout=300)
def statistics():
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    c.execute("SELECT category, COUNT(*) FROM domains GROUP BY category")
    category_stats = dict(c.fetchall())
    c.execute("SELECT COUNT(DISTINCT domain) FROM domains")
    total_domains = c.fetchone()[0]
    conn.close()
    
    return render_template('statistics.html', category_stats=category_stats, total_domains=total_domains)

@app.route('/custom_rules', methods=['GET', 'POST'])
@login_required
def custom_rules():
    if request.method == 'POST':
        rule = request.form['rule']
        category = request.form['category']
        add_custom_rule(rule, category)
        flash('Custom rule added successfully')
    
    rules = load_custom_rules()  # Load the custom rules from the JSON file
    return render_template('custom_rules.html', rules=rules)

@app.route('/remove_rule/<rule>')
@login_required
def remove_rule(rule):
    if remove_custom_rule(rule):
        flash('Custom rule removed successfully')
    else:
        flash('Rule not found')
    return redirect(url_for('custom_rules'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Check if username already exists
        if User.get_by_username(username):
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User.create(username, password, email)
        if new_user:
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Please try again.')
    
    return render_template('register.html')

@app.route('/domains', methods=['GET'])
@login_required
def list_domains():
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Number of domains per page
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')

    conn = sqlite3.connect('domains.db')
    c = conn.cursor()

    # Base query
    query = "SELECT domain, category FROM domains"
    params = []

    # Apply filters
    if search_query:
        query += " WHERE domain LIKE ?"
        params.append(f'%{search_query}%')
    
    if category_filter:
        if 'WHERE' in query:
            query += " AND category = ?"
        else:
            query += " WHERE category = ?"
        params.append(category_filter)

    # Get total count
    c.execute(f"SELECT COUNT(*) FROM ({query})", params)
    total = c.fetchone()[0]

    # Apply pagination
    query += f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"
    
    c.execute(query, params)
    domains = [{'domain': row[0], 'category': row[1]} for row in c.fetchall()]

    # Get unique categories for the filter dropdown
    c.execute("SELECT DISTINCT category FROM domains")
    categories = [row[0] for row in c.fetchall()]

    conn.close()

    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap4')

    return render_template('list_domains.html', domains=domains, pagination=pagination, 
                           search_query=search_query, category_filter=category_filter, 
                           categories=categories)

@app.route('/api/list_domains', methods=['GET'])
@login_required
def api_list_domains():
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Number of domains per page
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')

    conn = sqlite3.connect('domains.db')
    c = conn.cursor()

    # Base query
    query = "SELECT domain, category FROM domains"
    params = []

    # Apply filters
    if search_query:
        query += " WHERE domain LIKE ?"
        params.append(f'%{search_query}%')
    
    if category_filter:
        if 'WHERE' in query:
            query += " AND category = ?"
        else:
            query += " WHERE category = ?"
        params.append(category_filter)

    # Get total count
    c.execute(f"SELECT COUNT(*) FROM ({query})", params)
    total = c.fetchone()[0]

    # Apply pagination
    query += f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"
    
    c.execute(query, params)
    domains = [{'domain': row[0], 'category': row[1]} for row in c.fetchall()]

    conn.close()

    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap4')
    
    return jsonify({
        'domains': domains,
        'pagination': pagination.links
    })

@app.route('/api/remove_ns', methods=['POST'])
@login_required
def remove_ns():
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    c.execute("DELETE FROM domains WHERE domain LIKE 'ns%'")
    removed_count = c.rowcount
    conn.commit()
    conn.close()
    return jsonify({'message': f'Removed {removed_count} NS server domains'})

@app.route('/api/remove_subdomains', methods=['POST'])
@login_required
def remove_subdomains():
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    c.execute("SELECT domain FROM domains")
    domains = [row[0] for row in c.fetchall()]
    
    removed_count = 0
    for domain in domains:
        parts = domain.split('.')
        if len(parts) > 2:
            c.execute("DELETE FROM domains WHERE domain = ?", (domain,))
            removed_count += 1
    
    conn.commit()
    conn.close()
    return jsonify({'message': f'Removed {removed_count} subdomains'})

@app.route('/api/remove_selected', methods=['POST'])
@login_required
def remove_selected():
    domains = request.json.get('domains', [])
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    c.executemany("DELETE FROM domains WHERE domain = ?", [(domain,) for domain in domains])
    removed_count = c.rowcount
    conn.commit()
    conn.close()
    return jsonify({'message': f'Removed {removed_count} selected domains'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
