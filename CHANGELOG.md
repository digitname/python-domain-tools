# Changelog

All notable changes to this project will be documented in this file.

## [1.1.2] - 2023-04-18

### Fixed
- Updated markdown package to version 3.4.1 to resolve compatibility issues
- Modified init.sh script to force reinstall packages

## [1.1.1] - 2023-04-17

### Fixed
- Updated init.sh script to use python3 explicitly
- Added importlib-metadata to requirements.txt to resolve compatibility issues

## [1.1.0] - 2023-04-16

### Added
- Implemented more sophisticated domain categorization using tldextract
- Added user roles (admin and regular user)
- Implemented rate limiting for API access
- Created an admin page for user management

### Changed
- Updated domain_extractor.py to provide more detailed categorization
- Modified auth.py to include user roles
- Updated app.py to include rate limiting and admin functionality

## [1.0.0] - 2023-04-15

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

## [0.1.0] - 2023-04-14

### Added
- Initial release of the Domain Extractor application
- Basic domain extraction from plain text
- Simple web interface for input and display of results
