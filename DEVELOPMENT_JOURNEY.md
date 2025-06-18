# Excel Data Extraction Development Journey

## Project Overview
Created a Python script to extract training session data from an Excel file containing client fitness/training schedules. The goal was to identify paid vs unpaid sessions and generate structured JSON output.

## Key Challenges & Solutions

### 1. Understanding Excel Structure
**Challenge**: The Excel file had a complex layout that wasn't immediately obvious.
- Client names were in different columns than expected
- Session data was stored using cell colors rather than text values
- Dates were in a specific relationship to colored cells

**Solution**: Created analysis scripts to examine the Excel structure and discovered:
- "Numele" identifier in column B, client names in column C
- Colored cells in columns D-M indicate session payment status
- Dates are stored in the row immediately below colored cells

### 2. Color Detection Logic
**Challenge**: Excel cells used different RGB color codes for payment status.
- Green cells (FF00FF00) = Paid sessions
- Orange/yellow cells (FFFF9900) = Unpaid sessions  
- Many cells had default colors (00000000, FFFFFFFF) that needed filtering

**Solution**: Implemented robust color detection with proper filtering:
```python
if rgb == "FF00FF00":
    colored_cells.append((col, "paid"))
elif rgb == "FFFF9900" or "FF99" in rgb or ("FFFF" in rgb[:4] and rgb != "FFFFFFFF"):
    colored_cells.append((col, "unpaid"))
```

### 3. Date Format Conversion
**Challenge**: Excel stored dates as datetime objects (2024-06-10 00:00:00) but output needed simple format (10.6).

**Solution**: Added datetime handling to extract day and month:
```python
if hasattr(date_cell.value, 'date'):
    date_obj = date_cell.value.date()
    day = date_obj.day
    month = date_obj.month
    formatted_date = f"{day}.{month}"
```

### 4. Client Boundary Detection
**Challenge**: Determining where one client's data ends and another begins.
**Solution**: Used the next client's row position to limit search scope for each client.

## Technical Implementation

### Core Components
1. **Client Discovery**: Scan for "Numele" cells to find all clients
2. **Session Extraction**: Look for colored cells in columns D-M 
3. **Date Processing**: Extract dates from rows below colored cells
4. **Statistics Calculation**: Compute totals, paid/unpaid counts, remaining sessions

### Final Script Features
- Processes all 185 clients found in the Excel file
- Configurable client range (start_from, max_clients parameters)
- Generates structured JSON with session data and statistics
- Calculates 10-session packages and remaining sessions
- Robust error handling for date parsing

## Validation Results
Successfully validated against known data:
- Alexandra Boboc: 23 paid sessions + 1 unpaid session ("21.3") ✅
- Output format matches expected JSON structure ✅
- Color detection correctly identifies both paid and unpaid sessions ✅

## Final File Structure
```
/scripts/
├── excel.xlsx              # Source Excel file with client data
├── extract.py              # Original extraction attempt (deprecated)
├── extract_sessions.py     # Final working extraction script
├── file.json               # Reference output for validation
├── CLAUDE.md               # Project documentation for Claude
└── DEVELOPMENT_JOURNEY.md  # This documentation
```

## Usage
```bash
python extract_sessions.py
```

The script will process all clients and output a comprehensive JSON file with training session data.