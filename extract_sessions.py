# /// script
# dependencies = [
#   "openpyxl",
# ]
# ///

import openpyxl
import json
from datetime import datetime, date

def determine_year_from_date(day, month, current_date=date(2025, 6, 18)):
    """
    Intelligently determine year based on timeline logic.
    - Current date is 18.6.2025 (today)
    - Any date after 18.6 chronologically must be from 2024
    - Dates before/on 18.6 are from 2025
    """
    if month > current_date.month or (month == current_date.month and day > current_date.day):
        # This date is chronologically after today, so it must be 2024
        return 2024
    else:
        # This date is chronologically before/on today, so it's 2025
        return 2025

def enhance_session_dates(sessions_list):
    """
    Enhance sessions with proper years and format as DD.MM.YYYY.
    Also sort chronologically.
    """
    enhanced_sessions = []
    
    for date_str in sessions_list:
        try:
            parts = date_str.split('.')
            if len(parts) == 2:
                day = int(parts[0])
                month = int(parts[1])
                year = determine_year_from_date(day, month)
                enhanced_date = f"{day:02d}.{month:02d}.{year}"
                enhanced_sessions.append(enhanced_date)
            else:
                enhanced_sessions.append(date_str)  # Keep original if can't parse
        except:
            enhanced_sessions.append(date_str)  # Keep original if error
    
    # Sort chronologically
    def date_sort_key(date_str):
        try:
            parts = date_str.split('.')
            if len(parts) == 3:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                return datetime(year, month, day)
            elif len(parts) == 2:
                day, month = int(parts[0]), int(parts[1])
                year = determine_year_from_date(day, month)
                return datetime(year, month, day)
        except:
            pass
        return datetime(1900, 1, 1)  # Fallback
    
    return sorted(enhanced_sessions, key=date_sort_key)

def extract_client_sessions(excel_file_path, max_clients=5, start_from=0):
    """
    Extract client sessions from Excel file with proper color detection.
    
    Pattern:
    - Row X: "Numele" in column B, client name in column C
    - Rows below: colored cells in columns D-M (green=paid, orange=unpaid)
    - Row immediately below colored cells: dates
    """
    wb = openpyxl.load_workbook(excel_file_path, data_only=True)
    ws = wb.active
    
    clients_data = {
        "clients": {},
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "date_enhancement": {
            "enabled": True,
            "reference_date": "2025-06-18",
            "logic": "Dates after 18.6 are 2024, dates before/on 18.6 are 2025",
            "format": "DD.MM.YYYY"
        }
    }
    
    # Find all "Numele" positions
    numele_positions = []
    for row in range(1, ws.max_row + 1):
        cell_b = ws.cell(row=row, column=2)
        if cell_b.value and "Numele" in str(cell_b.value):
            client_name = ws.cell(row=row, column=3).value
            if client_name and str(client_name).strip():
                numele_positions.append((row, str(client_name).strip()))
    
    print(f"Found {len(numele_positions)} clients, processing {max_clients} starting from {start_from}")
    
    # Process clients from start_from to start_from + max_clients
    end_index = min(start_from + max_clients, len(numele_positions))
    for i, (client_row, client_name) in enumerate(numele_positions[start_from:end_index]):
        print(f"\n[{i+1}/{max_clients}] Processing: {client_name} (row {client_row})")
        
        paid_sessions = []
        unpaid_sessions = []
        
        # Look for session data in the next 50 rows after client name
        actual_index = start_from + i
        next_client_row = numele_positions[actual_index + 1][0] if actual_index + 1 < len(numele_positions) else ws.max_row
        search_end = min(client_row + 50, next_client_row)
        
        for row in range(client_row + 1, search_end):
            # Check for colored cells in columns D-M (4-13)
            colored_cells = []
            
            for col in range(4, 14):  # Columns D-M
                cell = ws.cell(row=row, column=col)
                
                if cell.fill and cell.fill.fgColor and cell.fill.fgColor.rgb:
                    rgb = str(cell.fill.fgColor.rgb)
                    
                    # Skip default/empty colors
                    if rgb == "00000000" or rgb == "FFFFFFFF":
                        continue
                    
                    # Green cells = paid (FF00FF00)
                    if rgb == "FF00FF00":
                        colored_cells.append((col, "paid"))
                    # Orange/yellow cells = unpaid (FFFF9900 or similar)
                    elif rgb == "FFFF9900" or "FF99" in rgb or ("FFFF" in rgb[:4] and rgb != "FFFFFFFF"):
                        colored_cells.append((col, "unpaid"))
            
            # If we found colored cells, check the next row for dates
            if colored_cells:
                date_row = row + 1
                for col, session_type in colored_cells:
                    date_cell = ws.cell(row=date_row, column=col)
                    if date_cell.value:
                        date_str = str(date_cell.value).strip()
                        
                        # Convert date format from "2024-06-10 00:00:00" to "10.6"
                        try:
                            # Handle datetime objects or date strings
                            if hasattr(date_cell.value, 'date'):
                                # It's a datetime object
                                date_obj = date_cell.value.date()
                                day = date_obj.day
                                month = date_obj.month
                            elif "-" in date_str and len(date_str) >= 10:
                                # It's a string like "2024-06-10" or "2024-06-10 00:00:00"
                                date_part = date_str.split()[0]  # Remove time part if present
                                parts = date_part.split("-")
                                if len(parts) >= 3:
                                    day = int(parts[2])
                                    month = int(parts[1])
                                else:
                                    continue
                            else:
                                continue
                            
                            formatted_date = f"{day}.{month}"
                            
                            if session_type == "paid":
                                paid_sessions.append(formatted_date)
                            else:
                                unpaid_sessions.append(formatted_date)
                            
                            print(f"  Found {session_type} session: {formatted_date}")
                        except Exception as e:
                            print(f"  Could not parse date: {date_str} - {e}")
        
        # Enhance dates with proper years and chronological sorting
        enhanced_paid = enhance_session_dates(paid_sessions)
        enhanced_unpaid = enhance_session_dates(unpaid_sessions)
        
        # Calculate stats
        total = len(enhanced_paid) + len(enhanced_unpaid)
        packages_needed = (total + 9) // 10  # Round up to nearest 10
        remaining = (packages_needed * 10) - total
        
        # Add client data with enhanced dates
        clients_data["clients"][client_name] = {
            "paid": enhanced_paid,
            "unpaid": enhanced_unpaid,
            "stats": {
                "total": total,
                "paid": len(enhanced_paid),
                "unpaid": len(enhanced_unpaid),
                "remaining": remaining
            }
        }
        
        print(f"  Summary: {len(paid_sessions)} paid, {len(unpaid_sessions)} unpaid, {total} total")
    
    return clients_data

def save_to_json(data, output_file="sessions_extracted.json"):
    """Save the extracted data to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nData saved to {output_file}")

if __name__ == "__main__":
    try:
        print("Extracting session data for ALL clients...")
        session_data = extract_client_sessions("excel.xlsx", max_clients=185, start_from=0)
        
        # Save to JSON with enhanced dates
        save_to_json(session_data, "all_clients_sessions_enhanced.json")
        
        # Print enhancement summary
        total_clients = len(session_data['clients'])
        total_sessions = sum(info['stats']['total'] for info in session_data['clients'].values())
        year_2024_count = 0
        year_2025_count = 0
        
        for client_data in session_data['clients'].values():
            for session in client_data.get('paid', []) + client_data.get('unpaid', []):
                if '2024' in session:
                    year_2024_count += 1
                elif '2025' in session:
                    year_2025_count += 1
        
        print("\n🎯 EXTRACTION & ENHANCEMENT SUMMARY")
        print("=" * 50)
        print(f"✅ Total clients processed: {total_clients}")
        print(f"✅ Total sessions extracted: {total_sessions}")
        print(f"📅 Sessions from 2024: {year_2024_count} ({year_2024_count/total_sessions*100:.1f}%)")
        print(f"📅 Sessions from 2025: {year_2025_count} ({year_2025_count/total_sessions*100:.1f}%)")
        print(f"🗓️  Enhanced format: DD.MM.YYYY")
        print(f"📊 Logic: Dates after 18.6 → 2024, dates before/on 18.6 → 2025")
        
        print(f"\n📋 Sample clients:")
        sample_count = 0
        for name, info in session_data['clients'].items():
            if sample_count >= 3:
                break
            stats = info['stats']
            if stats['total'] > 0:
                paid_sample = info['paid'][:2] if info['paid'] else []
                unpaid_sample = info['unpaid'][:1] if info['unpaid'] else []
                print(f"  {name}: {stats['total']} sessions")
                if paid_sample:
                    print(f"    Paid: {paid_sample}")
                if unpaid_sample:
                    print(f"    Unpaid: {unpaid_sample}")
                sample_count += 1
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()