from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Domain
from domain_utils import extract_domains, validate_domain, categorize_domain, add_custom_rule, remove_custom_rule, load_custom_rules

def register_routes(app, mail, cache, limiter):

    # @app.route('/api/list_domains', methods=['GET'])
    # @login_required
    # def list_domains():
    #     domains = Domain.query.filter_by(user_id=current_user.id).all()
    #     return jsonify([domain.to_dict() for domain in domains])


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




    @app.route('/api/add_domain', methods=['POST'])
    @login_required
    def add_domain():
        data = request.get_json()
        domain_name = data['domain']
        if not validate_domain(domain_name):
            return jsonify({'error': 'Invalid domain name'}), 400

        domain_category = categorize_domain(domain_name)[0]
        new_domain = Domain(name=domain_name, category=domain_category, user_id=current_user.id)
        db.session.add(new_domain)
        db.session.commit()
        return jsonify(new_domain.to_dict()), 201



    @app.route('/api/remove_selected', methods=['POST'])
    @login_required
    def remove_selected():
        domains = request.json.get('domains', [])
        print(domains)
        removed_domains = []
        removed_count = 0
        for domain in domains:
            domain_obj = Domain.query.filter_by(name=domain, user_id=current_user.id).first()
            if domain_obj:
                removed_domains.append(domain)
                db.session.delete(domain_obj)
                db.session.commit()
                removed_count += 1
        return jsonify({'message': f'Removed {removed_count} selected domains', 'removed_count': removed_count, 'removed_domains': removed_domains})

    @app.route('/api/remove_selected2', methods=['POST'])
    @login_required
    def remove_selected2(domains):
        removed_count = 0
        print(domains)
        for domain in domains:
            domain_obj = Domain.query.filter_by(name=domain, user_id=current_user.id).first()
            if domain_obj:
                db.session.delete(domain_obj)
                db.session.commit()
                removed_count += 1
        return removed_count

    @app.route('/api/add_hashtags', methods=['POST'])
    @login_required
    def add_hashtags():
        domain_names = request.form.getlist('domain_names[]')
        hashtags = request.form['hashtags']
        updated_count = 0
        for domain_name in domain_names:
            domain = Domain.query.filter_by(name=domain_name, user_id=current_user.id).first()
            if domain:
                domain.hashtags = hashtags
                db.session.commit()
                updated_count += 1
        return jsonify({'updated_count': updated_count})


