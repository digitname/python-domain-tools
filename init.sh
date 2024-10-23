#!/bin/bash

# remove old environment
#source venv/bin/deactivate
rm -rf venv
rm app.log
rm domains.db
rm src/domains.db
date +%Y-%m-%d > .date

chmod +x *.sh

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Uninstall existing packages
pip uninstall -y -r requirements.txt

# Install requirements
pip install -r requirements.txt

# Run database migration
#python src/migrate_db.py

# Initialize the database
python -c "from app import init_db; init_db()"

echo "Environment setup complete. Activate the virtual environment with 'source venv/bin/activate'"
python src/app.py

xdg-open http://127.0.0.1:5000/