# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **fitness training session data extraction tool** that processes Excel files containing client training schedules and generates structured JSON output. The main purpose is to track paid vs unpaid training sessions for fitness/training management.

**Business Context**: A fitness trainer uses an Excel spreadsheet to track client sessions. Each client has colored cells indicating payment status (green = paid, orange/yellow = unpaid) with dates stored below the colored cells. The tool extracts this data into a structured format for reporting and billing purposes.

## Project Structure

```
/scripts/
├── excel.xlsx                 # Source Excel file with client training data (409KB)
├── extract_sessions.py        # 🎯 MAIN WORKING SCRIPT - Use this one!
├── extract.py                 # Original script (deprecated, kept for reference)
├── all_clients_sessions.json  # Complete extracted data (all 185 clients)
├── file.json                  # Reference validation data (subset)
├── CLAUDE.md                  # This file - project documentation
└── DEVELOPMENT_JOURNEY.md     # Detailed development process documentation
```

## Main Script: extract_sessions.py

**This is the working script** - fully tested and validated against known data.

### Key Features
- ✅ Extracts all 185 clients from Excel file
- ✅ Detects paid sessions (green cells: FF00FF00) vs unpaid sessions (orange cells: FFFF9900)
- ✅ Converts Excel datetime objects to simple day.month format (e.g., "10.6" for June 10th)
- ✅ Generates comprehensive JSON with session statistics
- ✅ Calculates 10-session packages and remaining sessions
- ✅ Configurable client range processing

### Excel File Structure Understanding
The Excel file (`excel.xlsx`) has this structure:
- **Row with "Numele"** in column B → **Client name** in column C
- **Colored cells** in columns D-M indicate session payment status
- **Dates** are stored in the row immediately below colored cells
- **Color coding**: 
  - Green (RGB: FF00FF00) = Paid session
  - Orange (RGB: FFFF9900) = Unpaid session

### Usage Examples

**Extract all clients:**
```bash
python extract_sessions.py
# Output: all_clients_sessions.json with all 185 clients
```

**Extract specific range (modify script):**
```python
# In extract_sessions.py, modify the main section:
session_data = extract_client_sessions("excel.xlsx", max_clients=10, start_from=50)
```

**Extract single client for testing:**
```python
session_data = extract_client_sessions("excel.xlsx", max_clients=1, start_from=5)  # Alexandra Boboc
```

## Expected Output Format

```json
{
  "clients": {
    "Alexandra Boboc": {
      "paid": ["10.6", "14.6", "17.6", "26.7", ...],
      "unpaid": ["21.3"],
      "stats": {
        "total": 24,
        "paid": 23,
        "unpaid": 1,
        "remaining": 6
      }
    }
  },
  "updated": "2025-06-18"
}
```

## Validation Data
- **Alexandra Boboc** is a known test case: 23 paid sessions + 1 unpaid session ("21.3")
- This matches the reference data in `file.json`
- Use this client to validate any changes to the extraction logic

## Technical Implementation Notes

### Color Detection Logic
```python
# Green cells (paid)
if rgb == "FF00FF00":
    colored_cells.append((col, "paid"))
# Orange/yellow cells (unpaid)  
elif rgb == "FFFF9900" or "FF99" in rgb or ("FFFF" in rgb[:4] and rgb != "FFFFFFFF"):
    colored_cells.append((col, "unpaid"))
```

### Date Processing
- Excel stores dates as datetime objects (e.g., `2024-06-10 00:00:00`)
- Script converts to simple format: `f"{day}.{month}"` → `"10.6"`
- Handles both datetime objects and string formats

### Package Calculation
- Sessions are sold in packages of 10
- Formula: `packages_needed = (total + 9) // 10` (rounds up)
- Remaining: `(packages_needed * 10) - total`

## Dependencies
- **openpyxl**: Excel file reading and cell color detection
- **json**: Output formatting
- **datetime**: Timestamp generation

Uses PEP 723 script dependencies declaration - run directly with `python extract_sessions.py`

## Troubleshooting

**No sessions found for a client:**
- Check if client has colored cells in columns D-M
- Verify dates are in the row immediately below colored cells

**Wrong session count:**
- Compare with manual count in Excel
- Check color detection logic for edge cases

**Date format issues:**
- Ensure Excel file has datetime objects, not text
- Check for mixed date formats in the same file

## Development Notes
- See `DEVELOPMENT_JOURNEY.md` for complete development process
- Original `extract.py` had pandas dependency - removed for simplicity
- Tested with 185 real clients, processing takes ~2-3 minutes for full dataset