# Domain Extractor

A web application for extracting, validating, and categorizing domain names from various input formats.

## Features

- Extract domains from plain text, HTML, and Markdown inputs
- Validate and categorize extracted domains
- User authentication and authorization
- Bulk import of domains from CSV files
- Search functionality for stored domains
- Export domains in CSV and JSON formats
- RESTful API for programmatic access
- Responsive web interface

## Installation

1. Clone the repository:   ```
   git clone https://github.com/yourusername/domain-extractor.git
   cd domain-extractor   ```

2. Create a virtual environment and activate it:   ```
   python3 -m venv venv
   source venv/bin/activate   ```

3. Install the required dependencies:   ```
   pip install -r requirements.txt   ```

4. Initialize the database and create an admin user:   ```
   python init_db.py   ```

5. Run the application:   ```
   python app.py   ```

6. Access the application in your web browser at `http://localhost:5000`

## Usage

1. Log in using your credentials
2. Enter text containing domain names in the input field
3. Select the input type (plain text, HTML, or Markdown)
4. Click "Extract Domains" to process the input
5. View the extracted domains and their categories
6. Use the search function to find specific domains
7. Export the results in CSV or JSON format

## API Usage

The API endpoint is available at `/api/domains`. You need to be authenticated to access the API.

Example API request:
