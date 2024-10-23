from flask import render_template, request, send_file, jsonify, redirect, url_for, flash, session
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
import csv
import io
import openpyxl
import pyotp
import json
import logging
from collections import Counter
from flask_paginate import Pagination
from datetime import datetime

from models import db, User, Domain
from domain_utils import extract_domains, validate_domain, categorize_domain, add_custom_rule, remove_custom_rule, load_custom_rules


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

def register_routes(app, mail, cache, limiter):
    @app.route('/', methods=['GET', 'POST'])
    @login_required
    def index():
        if request.method == 'POST':
            text = request.form.get('text', None)
            if text:
                extracted_domains = extract_domains(text)
                new_domains = save_domains(extracted_domains, current_user)
                flash(f'Successfully extracted and saved {new_domains} new domains.')
            else:
                flash('Please enter some text to extract domains.')
            return redirect(url_for('index'))

        domains = Domain.query.filter_by(user_id=current_user.id).all()
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
                    save_domains(domains, current_user)
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
        
        rules = load_custom_rules()
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
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists. Please choose a different one.')
                return redirect(url_for('register'))
            
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


    @app.context_processor
    def inject_total_domains():
        if current_user.is_authenticated:
            total_domains = Domain.query.filter_by(user_id=current_user.id).count()
            return dict(total_domains=total_domains)
        return dict()
