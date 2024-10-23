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

from .models import db, User, Domain
from .domain_utils import extract_domains, validate_domain, categorize_domain, add_custom_rule, remove_custom_rule, load_custom_rules

def register_api_routes(app, mail, cache, limiter):


    @app.route('/api/domains', methods=['GET'])
    @login_required
    @limiter.limit("100 per day")
    @cache.cached(timeout=300)
    def api_domains():
        domains = Domain.query.all()
        return jsonify([{'domain': domain.name, 'category': domain.category} for domain in domains])

    @app.route('/api/list_domains', methods=['GET'])
    @login_required
    def api_list_domains():
        page = request.args.get('page', 1, type=int)
        per_page = 20
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
            'ns%',
            'dns%',
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

    @app.route('/api/list_domains', methods=['GET'])
    @login_required
    def api_list_domains():
        page = request.args.get('page', 1, type=int)
        per_page = 20
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
            'ns%',
            'dns%',
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

