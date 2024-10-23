from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
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
from datetime import datetime
import json
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///domains.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)

login_manager.init_app(app)

migrate = Migrate(app, db)

# Define the Domain model
class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hashtags = db.Column(db.String(255))  # New field for hashtags

    def __repr__(self):
        return f'<Domain {self.name}>'

# Update the User model to include the relationship with Domain
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))
    domains = db.relationship('Domain', backref='user', lazy=True)

    @staticmethod
    def get(user_id):
        return User.query.get(int(user_id))

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    # ... (other methods)

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
    db.create_all()
    init_auth_db()

def save_domains(domains):
    new_domains = 0
    for domain in domains:
        if validate_domain(domain):
            category = categorize_domain(domain)
            try:
                new_domain = Domain(name=domain, category=category, user_id=current_user.id)
                db.session.add(new_domain)
                db.session.commit()
                new_domains += 1
            except IntegrityError:
                db.session.rollback()  # Roll back the failed transaction
                # Optionally, you can update the existing domain's category here
                existing_domain = Domain.query.filter_by(name=domain).first()
                if existing_domain:
                    existing_domain.category = category
                    db.session.commit()
    return new_domains

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        text = request.form['text']
        extracted_domains = extract_domains(text)
        new_domains = save_domains(extracted_domains)
        flash(f'Successfully extracted and saved {new_domains} new domains.')
        return redirect(url_for('index'))

    domains = Domain.query.filter_by(user_id=current_user.id).all()
    
    # Calculate category statistics
    category_stats = Counter(domain.category for domain in domains)
    
    return render_template('index.html', domains=domains, category_stats=category_stats)

@app.route('/search', methods=['GET'])
@login_required
@cache.cached(timeout=300, query_string=True)
def search():
    query = request.args.get('query', '')
    domains = Domain.query.filter(Domain.name.ilike(f'%{query}%')).all()
    return render_template('index.html', domains=domains, search_query=query)

@app.route('/export', methods=['GET'])
@login_required
@cache.cached(timeout=300, query_string=True)
def export():
    format = request.args.get('format', 'csv')
    domains = Domain.query.filter_by(user_id=current_user.id).all()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Domain', 'Category', 'Hashtags'])
        writer.writerows([[domain.name, domain.category, domain.hashtags] for domain in domains])
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'domains_export_{timestamp}.csv'
        )
    elif format == 'json':
        data = [{'domain': domain.name, 'category': domain.category, 'hashtags': domain.hashtags} for domain in domains]
        return send_file(
            io.BytesIO(json.dumps(data, indent=2).encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'domains_export_{timestamp}.json'
        )
    elif format == 'excel':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['Domain', 'Category', 'Hashtags'])
        for domain in domains:
            ws.append([domain.name, domain.category, domain.hashtags])
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'domains_export_{timestamp}.xlsx'
        )

@app.route('/api/domains', methods=['GET'])
@login_required
@limiter.limit("100 per day")
@cache.cached(timeout=300)
def api_domains():
    domains = Domain.query.all()
    return jsonify([{'domain': domain.name, 'category': domain.category} for domain in domains])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
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
    
    user = User.query.get(session['user_id'])
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
    category_stats = Counter(domain.category for domain in Domain.query.all())
    total_domains = Domain.query.count()
    
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
        if User.query.filter_by(username=username).first():
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
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    sort_by = request.args.get('sort', 'name')
    sort_order = request.args.get('order', 'asc')

    query = Domain.query.filter_by(user_id=current_user.id)
    if search_query:
        query = query.filter(Domain.name.ilike(f'%{search_query}%'))
    if category_filter:
        query = query.filter(Domain.category == category_filter)

    if sort_by == 'name':
        query = query.order_by(Domain.name.asc() if sort_order == 'asc' else Domain.name.desc())
    elif sort_by == 'category':
        query = query.order_by(Domain.category.asc() if sort_order == 'asc' else Domain.category.desc())

    domains = query.all()
    total_domains = len(domains)

    categories = Domain.query.with_entities(Domain.category).distinct().all()
    categories = [category[0] for category in categories]

    return render_template('list_domains.html',
                           domains=domains,
                           search_query=search_query,
                           category_filter=category_filter,
                           categories=categories,
                           total_domains=total_domains,
                           sort_by=sort_by,
                           sort_order=sort_order)

@app.route('/api/list_domains', methods=['GET'])
@login_required
def api_list_domains():
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Number of domains per page
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')

    domains = Domain.query.filter(Domain.name.ilike(f'%{search_query}%'))
    if category_filter:
        domains = domains.filter(Domain.category == category_filter)

    total = domains.count()
    domains = domains.paginate(page, per_page, False)

    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap4')
    
    return jsonify({
        'domains': [{'domain': domain.name, 'category': domain.category} for domain in domains],
        'pagination': pagination.links
    })

@app.route('/api/remove_ns', methods=['POST'])
@login_required
def remove_ns():
    popular_ns = [
        'ns%',  # Catches ns1, ns2, etc.
        'dns%',  # Catches dns1, dns2, etc.
        '%.cloudflare.com',
        '%.NS.CLOUDFLARE.COM',
        '%.sedo.com',
        '%.registrar-servers.com',
        '%.domaincontrol.com',
        '%.googledomains.com',
        '%.awsdns-%',
        '%.azure-dns.%',
        '%.gandi.net',
        '%.ovh.net',
        '%.name-services.com',
    ]

    removed_count = 0
    for pattern in popular_ns:
        domains_to_remove = Domain.query.filter(Domain.name.ilike(pattern)).all()
        for domain in domains_to_remove:
            db.session.delete(domain)
            removed_count += 1

    db.session.commit()
    return jsonify({'message': f'Removed {removed_count} DNS server domains'})

@app.route('/api/remove_subdomains', methods=['POST'])
@login_required
def remove_subdomains():
    domains = Domain.query.all()
    
    removed_count = 0
    for domain in domains:
        parts = domain.name.split('.')
        if len(parts) > 2:
            db.session.delete(domain)
            removed_count += 1
    
    db.session.commit()
    return jsonify({'message': f'Removed {removed_count} subdomains'})

@app.route('/api/remove_selected', methods=['POST'])
@login_required
def remove_selected():
    domains = request.json.get('domains', [])
    removed_count = Domain.query.filter(Domain.name.in_(domains)).delete(synchronize_session='fetch')
    db.session.commit()
    return jsonify({'message': f'Removed {removed_count} selected domains'})

@app.route('/api/add_hashtags', methods=['POST'])
@login_required
def add_hashtags():
    data = request.json
    domains = data.get('domains', [])
    hashtags = data.get('hashtags', '')

    updated_count = Domain.query.filter(Domain.name.in_(domains)).update(
        {Domain.hashtags: Domain.hashtags + ' ' + hashtags if Domain.hashtags else hashtags},
        synchronize_session='fetch'
    )
    db.session.commit()

    return jsonify({'message': f'Added hashtags to {updated_count} domains'})

@app.context_processor
def inject_total_domains():
    if current_user.is_authenticated:
        total_domains = Domain.query.filter_by(user_id=current_user.id).count()
        return dict(total_domains=total_domains)
    return dict()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
