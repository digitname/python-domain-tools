from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import csv
import io
from domain_extractor import extract_domains, validate_domain, categorize_domain
from auth import User, init_auth_db, add_user, login_manager
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure random key
login_manager.init_app(app)

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

@app.route('/api/domains', methods=['GET'])
@login_required
@limiter.limit("100 per day")
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
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
