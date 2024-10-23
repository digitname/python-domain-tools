import click
import sqlite3
from domain_extractor import extract_domains, validate_domain, categorize_domain

@click.group()
def cli():
    pass

@cli.command()
@click.argument('text')
@click.option('--file-type', default='text', type=click.Choice(['text', 'html', 'markdown']))
def extract(text, file_type):
    """Extract domains from the given text."""
    domains = extract_domains(text, file_type)
    for domain in domains:
        category = categorize_domain(domain)
        click.echo(f"Domain: {domain}, Category: {category}")

@cli.command()
@click.argument('domain')
def validate(domain):
    """Validate a single domain."""
    is_valid = validate_domain(domain)
    click.echo(f"Domain '{domain}' is {'valid' if is_valid else 'invalid'}.")

@cli.command()
def list_domains():
    """List all domains in the database."""
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    c.execute("SELECT domain, category FROM domains")
    domains = c.fetchall()
    conn.close()

    if domains:
        for domain, category in domains:
            click.echo(f"Domain: {domain}, Category: {category}")
    else:
        click.echo("No domains found in the database.")

if __name__ == '__main__':
    cli()
