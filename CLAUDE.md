# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a training session data extraction tool that processes Excel files containing client training schedules and generates structured JSON output. The main purpose is to track paid vs unpaid training sessions for fitness/training management.

## Architecture

- **extract.py**: Main extraction script using openpyxl to parse Excel files
  - Searches for client names by finding "Numele" cells
  - Identifies paid sessions by cell color (green background detection)
  - Calculates session statistics and remaining sessions needed
  - Outputs structured JSON with client data
- **excel.xlsx**: Source Excel file containing client training data
- **file.json**: Generated output with processed client session data

## Key Implementation Details

- Uses PEP 723 script dependencies declaration for openpyxl
- Cell color detection logic for identifying paid sessions (RGB analysis)
- Processes sessions in 10-session packages with remaining calculation
- Limited to 5 clients by default for testing purposes
- Date format appears to be DD.M or DD.MM format

## Running the Script

```bash
python extract.py
```

The script processes `excel.xlsx` by default and outputs structured JSON data to console and `file.json`.