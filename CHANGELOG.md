# Changelog

All notable changes to this project will be documented in this file.

## [2.13.0] - 2024-10-23

### Added
- Implemented additional domain categorization rules to handle new gTLDs.
- Improved the 'remove_ns' function to handle a wider range of DNS server domains, including *.NS.CLOUDFLARE.COM.
- Added hashtag functionality for domains, including a new field in the Domain model, an API endpoint for adding hashtags, and UI elements in the list_domains.html template.
- Added timestamps to exported file names.

### Fixed
- Fixed the 'remove_selected' function to correctly return the count of removed domains.
- Corrected the categorization of domains with new gTLDs (e.g., solo.startup is now recognized as a TLD).

## [2.12.0] - 2024-10-23

### Added
- Created separate `models.py` file for database models
- Implemented Flask-Migrate for database migrations

### Changed
- Refactored `app.py` and `auth.py` to resolve circular imports
- Updated database initialization process

### Fixed
- Resolved circular import issue between `app.py` and `auth.py`
- Fixed missing `users` table issue by properly initializing the database

## [2.11.0] - 2024-10-23

### Added
- Integrated Flask-Migrate for database migrations
- Created initial database migration for User and Domain models

### Changed
- Updated User model to use SQLAlchemy ORM
- Modified auth.py to use SQLAlchemy for user operations
- Updated app initialization to include Flask-Migrate

### Fixed
- Resolved issue with missing 'users' table by creating proper database schema

## [2.10.0] - 2024-10-23

### Added
- New `hashtags` field for Domain model
- Database migration to add `hashtags` column to the domain table
- Flask-Migrate integration for handling database schema changes

### Changed
- Updated export functionality to include hashtags in exported data
- Modified `list_domains.html` to display hashtags for each domain

### Fixed
- Resolved issue with missing `hashtags` column in domain table

## [2.9.0] - 2024-10-23

### Added
- Display of total domain count in the navigation menu
- Context processor to inject total domain count into all templates
- Sorting functionality for domain list (by domain name and category)
- Extended DNS server removal to include popular providers like Cloudflare and Sedo
- Hashtag functionality for domains
  - New field 'hashtags' added to Domain model
  - API endpoint for adding hashtags to selected domains
  - UI elements in list_domains.html for adding hashtags
- Timestamp added to exported file names

### Changed
- Updated `list_domains` function to include sorting options
- Modified `list_domains.html` template to include sorting links and indicators
- Updated `base.html` template to show domain count in the menu
- Improved `remove_ns` function to remove a wider range of DNS server domains, including *.NS.CLOUDFLARE.COM
- Updated JavaScript in `list_domains.html` to reflect changes in DNS server removal and hashtag functionality
- Improved domain categorization to correctly identify new gTLDs like .startup
- Modified export functionality to include timestamps in file names and add hashtags to exported data

### Fixed
- Fixed `remove_selected` function to correctly return the count of removed domains
- Corrected categorization of domains with new gTLDs (e.g., solo.startup is now recognized as a TLD)

## [2.8.0] - 2024-10-23

### Added
- Sorting functionality for domain list (by domain name and category)
- Display all domains without pagination

### Changed
- Updated list_domains route in app.py to support sorting
- Modified list_domains.html template to include sorting links and indicators

## [2.7.0] - 2024-10-23

### Added
- Real-time statistics update after each domain extraction
- Display of current statistics on the index page

### Changed
- Removed pagination from the domain list page
- Updated domain list filtering to use form submission instead of dynamic updates

## [2.6.0] - 2024-10-23

### Added
- New actions to clean up domain list:
  - Remove NS server domains
  - Remove subdomains
  - Remove selected domains
- Checkboxes for selecting individual domains
- API endpoints for new domain list actions

### Changed
- Updated list_domains.html to include new action buttons and checkboxes
- Modified app.py to include new API routes for domain list actions

## [2.5.0] - 2024-10-23

### Added
- Dynamic filtering and searching for domain list
- New API endpoint for listing domains with filters

### Changed
- Updated list_domains.html to use JavaScript for dynamic updates
- Modified app.py to include new API route for listing domains

## [2.4.0] - 2024-10-23

### Added
- Created a base template using Bootstrap for consistent styling
- Updated all HTML templates to extend from the base template

### Changed
- Improved overall UI/UX with Bootstrap-based design
- Reorganized navigation into a responsive navbar

## [2.3.0] - 2024-10-23

### Added
- New page for listing domains with filtering and pagination
- Search functionality for domains by name and category
- Pagination for the domain list

### Changed
- Updated navigation to include a link to the new domain list page
- Added flask-paginate to requirements.txt

## [2.2.2] - 2024-10-23

### Fixed
- Resolved issue with custom rules not being properly loaded in the template

## [2.2.1] - 2024-10-23

### Added
- Database migration script to add email column to users table

### Fixed
- Issue with missing email column in users table

## [2.2.0] - 2024-10-23

### Added
- Implemented caching mechanism using Flask-Caching
- Added caching to search, export, API, and statistics routes

### Changed
- Updated app.py to include caching configuration and decorators
- Added Flask-Caching to requirements.txt

## [2.1.0] - 2024-10-23

### Added
- User registration functionality
- New registration page and form
- Email field for user accounts

### Changed
- Updated User model to include email field
- Modified auth.py to support user creation
- Updated login page to include link to registration

## [2.0.0] - 2024-10-23

### Added
- Support for custom domain categorization rules
- New page for managing custom rules
- JSON file storage for custom rules

### Changed
- Updated domain_extractor.py to use custom rules in categorization
- Modified app.py to include routes for managing custom rules
- Updated index.html to include a link to the custom rules page

## [1.9.0] - 2024-10-23

### Added
- Implemented automated testing with GitHub Actions
- Created GitHub Actions workflow for running tests
- Expanded unit tests in test_app.py

### Changed
- Updated TODO.md to reflect the implementation of automated testing

## [1.8.0] - 2024-10-23

### Added
- Implemented multi-factor authentication using TOTP
- New routes for two-factor authentication and enabling 2FA
- Added pyotp library for generating and verifying TOTP tokens

### Changed
- Updated User model to include two_factor_secret
- Modified login process to support 2FA
- Added new templates for 2FA authentication and setup

## [1.7.0] - 2024-10-23

### Added
- Email notifications for bulk import results
- Flask-Mail integration for sending emails

### Changed
- Updated bulk_import function in app.py to send email notifications
- Added Flask-Mail to requirements.txt

## [1.6.0] - 2024-10-23

### Added
- Implemented data visualization for domain statistics
- New statistics page with pie chart showing domain categories
- Added Chart.js library for creating interactive charts

### Changed
- Updated app.py to include a new route for domain statistics
- Modified index.html to include a link to the statistics page

## [1.5.0] - 2024-10-23

### Added
- Support for exporting domains to Excel format
- Added openpyxl library for Excel file generation

### Changed
- Updated export functionality in app.py to include Excel export
- Modified index.html template to include Excel export option
- Updated requirements.txt with openpyxl dependency

## [1.4.0] - 2024-10-23

### Added
- Improved documentation in README.md
- Added usage instructions for CLI in README.md

### Changed
- Updated init.sh script to include CLI setup

### Fixed
- Minor bug fixes and code improvements

## [1.3.0] - 2024-10-23

### Added
- Command-line interface (CLI) for the application
- New CLI commands: extract, validate, and list_domains
- Click library for building the CLI

### Changed
- Updated requirements.txt to include Click library

## [1.2.0] - 2024-10-23

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

## [Unreleased]

### Added
- Display of total domain count in the navigation menu
- Context processor to inject total domain count into all templates
- Sorting functionality for domain list (by domain name and category)
- Extended DNS server removal to include popular providers like Cloudflare and Sedo
- Hashtag functionality for domains
  - New field 'hashtags' added to Domain model
  - API endpoint for adding hashtags to selected domains
  - UI elements in list_domains.html for adding hashtags
- Timestamp added to exported file names

### Changed
- Updated `list_domains` function to include sorting options
- Modified `list_domains.html` template to include sorting links and indicators
- Updated `base.html` template to show domain count in the menu
- Improved `remove_ns` function to remove a wider range of DNS server domains, including *.NS.CLOUDFLARE.COM
- Updated JavaScript in `list_domains.html` to reflect changes in DNS server removal and hashtag functionality
- Improved domain categorization to correctly identify new gTLDs like .startup
- Modified export functionality to include timestamps in file names and add hashtags to exported data

### Fixed
- Fixed `remove_selected` function to correctly return the count of removed domains
- Corrected categorization of domains with new gTLDs (e.g., solo.startup is now recognized as a TLD)
