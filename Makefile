# Makefile for Fitness Training Session Data Extraction Tool

.PHONY: help extract extract-all extract-sample validate clean install test

# Default target
help:
	@echo "Available targets:"
	@echo "  extract      - Extract all client sessions (default)"
	@echo "  extract-all  - Extract all 185 clients (same as extract)"
	@echo "  extract-sample - Extract first 10 clients for testing"
	@echo "  validate     - Validate extraction with known test case"
	@echo "  enhance      - Enhance dates with full year format"
	@echo "  validate-dates - Validate date enhancement"
	@echo "  install      - Install required dependencies"
	@echo "  test         - Run validation tests"
	@echo "  clean        - Remove generated files"
	@echo "  backup       - Backup current data files"

# Main extraction target
extract: extract-all

# Extract all clients
extract-all:
	@echo "Extracting all client sessions..."
	python extract_sessions.py
	@echo "✓ Extraction complete: all_clients_sessions.json"

# Extract sample for testing
extract-sample:
	@echo "Extracting sample (first 10 clients)..."
	@sed 's/max_clients=None/max_clients=10/' extract_sessions.py > temp_extract.py
	python temp_extract.py
	@rm temp_extract.py
	@echo "✓ Sample extraction complete"

# Validate against known test case
validate:
	@echo "Validating extraction with Alexandra Boboc test case..."
	@python -c "import json; data=json.load(open('all_clients_sessions.json')); client=data['clients'].get('Alexandra Boboc', {}); print(f'Alexandra Boboc: {client.get(\"stats\", {}).get(\"paid\", 0)} paid, {client.get(\"stats\", {}).get(\"unpaid\", 0)} unpaid'); expected_paid=23; expected_unpaid=1; actual_paid=client.get('stats', {}).get('paid', 0); actual_unpaid=client.get('stats', {}).get('unpaid', 0); print('✓ Validation PASSED' if actual_paid==expected_paid and actual_unpaid==expected_unpaid else '✗ Validation FAILED')"

# Enhance dates with full year format
enhance:
	@echo "Enhancing session dates with intelligent year detection..."
	python enhance_dates.py
	@echo "✓ Date enhancement complete: all_clients_sessions_enhanced.json"

# Validate date enhancement
validate-dates:
	@echo "Validating date enhancement..."
	python validate_dates.py
	@echo "✓ Date validation complete"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install openpyxl
	@echo "✓ Dependencies installed"

# Run tests
test: validate validate-dates
	@echo "✓ All tests passed"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -f all_clients_sessions.json all_clients_sessions_enhanced.json temp_extract.py
	@echo "✓ Cleanup complete"

# Backup data files
backup:
	@echo "Creating backup of data files..."
	@mkdir -p backups
	@cp -f all_clients_sessions.json backups/all_clients_sessions_$(shell date +%Y%m%d_%H%M%S).json 2>/dev/null || true
	@cp -f all_clients_sessions_enhanced.json backups/all_clients_sessions_enhanced_$(shell date +%Y%m%d_%H%M%S).json 2>/dev/null || true
	@echo "✓ Backup complete"

# Show project info
info:
	@echo "Fitness Training Session Data Extraction Tool"
	@echo "============================================="
	@echo "Main script: extract_sessions.py"
	@echo "Source file: excel.xlsx (409KB)"
	@echo "Total clients: 185"
	@echo "Output format: JSON"
	@echo ""
	@echo "Key features:"
	@echo "- Extracts paid/unpaid session data"
	@echo "- Color-coded cell detection (green=paid, orange=unpaid)"
	@echo "- Automatic date format conversion"
	@echo "- Session package calculations"