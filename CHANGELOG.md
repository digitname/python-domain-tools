# Changelog

All notable changes to this project will be documented in this file.

## [2.2.1] - 2024-11-04

### Added
- Database migration script to add email column to users table

### Fixed
- Issue with missing email column in users table

## [2.2.0] - 2024-11-03

### Added
- Implemented caching mechanism using Flask-Caching
- Added caching to search, export, API, and statistics routes

### Changed
- Updated app.py to include caching configuration and decorators
- Added Flask-Caching to requirements.txt

## [2.1.0] - 2024-11-02

### Added
- User registration functionality
- New registration page and form
- Email field for user accounts

### Changed
- Updated User model to include email field
- Modified auth.py to support user creation
- Updated login page to include link to registration

## [2.0.0] - 2024-11-01

### Added
- Support for custom domain categorization rules
- New page for managing custom rules
- JSON file storage for custom rules

### Changed
- Updated domain_extractor.py to use custom rules in categorization
- Modified app.py to include routes for managing custom rules
- Updated index.html to include a link to the custom rules page

## [1.9.0] - 2024-10-31

### Added
- Implemented automated testing with GitHub Actions
- Created GitHub Actions workflow for running tests
- Expanded unit tests in test_app.py

### Changed
- Updated TODO.md to reflect the implementation of automated testing

## [1.8.0] - 2024-10-30

### Added
- Implemented multi-factor authentication using TOTP
- New routes for two-factor authentication and enabling 2FA
- Added pyotp library for generating and verifying TOTP tokens

### Changed
- Updated User model to include two_factor_secret
- Modified login process to support 2FA
- Added new templates for 2FA authentication and setup

## [1.7.0] - 2024-10-29

### Added
- Email notifications for bulk import results
- Flask-Mail integration for sending emails

### Changed
- Updated bulk_import function in app.py to send email notifications
- Added Flask-Mail to requirements.txt

## [1.6.0] - 2024-10-28

### Added
- Implemented data visualization for domain statistics
- New statistics page with pie chart showing domain categories
- Added Chart.js library for creating interactive charts

### Changed
- Updated app.py to include a new route for domain statistics
- Modified index.html to include a link to the statistics page

## [1.5.0] - 2024-10-27

### Added
- Support for exporting domains to Excel format
- Added openpyxl library for Excel file generation

### Changed
- Updated export functionality in app.py to include Excel export
- Modified index.html template to include Excel export option
- Updated requirements.txt with openpyxl dependency

## [1.4.0] - 2024-10-26

### Added
- Improved documentation in README.md
- Added usage instructions for CLI in README.md

### Changed
- Updated init.sh script to include CLI setup

### Fixed
- Minor bug fixes and code improvements

## [1.3.0] - 2024-10-25

### Added
- Command-line interface (CLI) for the application
- New CLI commands: extract, validate, and list_domains
- Click library for building the CLI

### Changed
- Updated requirements.txt to include Click library

## [1.2.0] - 2024-10-24

### Added
- Improved documentation in README.md
- Created git_update.sh script for easier version management
- Updated init.sh script to create git_update.sh

### Changed
- Refactored domain_extractor.py to use tldextract for better domain categorization
- Updated app.py to include admin functionality and rate limiting

### Fixed
- Resolved compatibility issues with markdown package

## [1.1.2] - 2024-10-23

### Fixed
- Updated markdown package to version 3.4.1 to resolve compatibility issues
- Modified init.sh script to force reinstall packages

## [1.1.1] - 2024-10-23

### Fixed
- Updated init.sh script to use python3 explicitly
- Added importlib-metadata to requirements.txt to resolve compatibility issues

## [1.1.0] - 2024-10-23

### Added
- Implemented more sophisticated domain categorization using tldextract
- Added user roles (admin and regular user)
- Implemented rate limiting for API access
- Created an admin page for user management

### Changed
- Updated domain_extractor.py to provide more detailed categorization
- Modified auth.py to include user roles
- Updated app.py to include rate limiting and admin functionality

## [1.0.0] - 2024-10-23

### Added
- User authentication and authorization
- Bulk domain import from CSV files
- Domain validation and categorization
- RESTful API for programmatic access
- Improved error handling and logging
- Search functionality for domains
- Export options for CSV and JSON formats
- Responsive design for the web interface

### Changed
- Updated Flask and Werkzeug versions to 2.0.3 for compatibility
- Restructured the application to use separate modules for authentication and domain extraction

### Fixed
- Duplicate domain removal in extraction process

## [0.1.0] - 2024-10-23

### Added
- Initial release of the Domain Extractor application
- Basic domain extraction from plain text
- Simple web interface for input and display of results
