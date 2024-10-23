# Domain Extractor

A web application and command-line tool for extracting, validating, and categorizing domain names from various input formats.

## Features

- Extract domains from plain text, HTML, and Markdown inputs
- Validate and categorize extracted domains
- User authentication and authorization with admin roles
- Bulk import of domains from CSV files
- Search functionality for stored domains
- Export domains in CSV and JSON formats
- RESTful API for programmatic access with rate limiting
- Responsive web interface
- Command-line interface (CLI) for quick domain operations

## Installation

1. Clone the repository:   ```
   git clone https://github.com/yourusername/domain-extractor.git
   cd domain-extractor   ```

2. Run the initialization script:   ```
   chmod +x init.sh
   ./init.sh   ```

   This script will:
   - Create and activate a virtual environment
   - Install required dependencies
   - Initialize the database
   - Create a git_update.sh script for easy version management

3. Activate the virtual environment:   ```
   source venv/bin/activate   ```

## Usage

### Web Application

1. Run the application:   ```
   python app.py   ```

2. Access the application in your web browser at `http://localhost:5000`

3. Log in using your credentials

4. Use the web interface to extract, search, and manage domains

### Command-Line Interface (CLI)

The CLI provides quick access to domain operations:

- Extract domains from text:  ```
  python cli.py extract "Visit example.com and test.org"  ```

- Validate a single domain:  ```
  python cli.py validate example.com  ```

- List all domains in the database:  ```
  python cli.py list_domains  ```

## API Usage

The API endpoint is available at `/api/domains`. You need to be authenticated to access the API. The API is rate-limited to 100 requests per day.

Example API request:
