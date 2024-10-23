#!/bin/bash

# remove old environment
deactivate
rm -rf venv
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

# Initialize the database
python -c "from app import init_db; init_db()"

echo "Environment setup complete. Activate the virtual environment with 'source venv/bin/activate'"
python app.py

xdg-open http://127.0.0.1:5000/