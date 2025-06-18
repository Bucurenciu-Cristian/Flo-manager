# /// script
# dependencies = [
#   "openpyxl",
# ]
# ///

import json
from datetime import datetime, date

def parse_day_month(date_str):
    """Parse day.month format and return day, month as integers."""
    try:
        parts = date_str.split('.')
        if len(parts) == 2:
            day = int(parts[0])
            month = int(parts[1])
            return day, month
        return None, None
    except:
        return None, None

def determine_year_intelligent(sessions_list, current_date=date(2025, 6, 18)):
    """
    Intelligently determine years for sessions based on timeline order.
    
    Logic:
    - Current date is 18.6.2025 (today)
    - Sessions are in chronological order within the array
    - Any date after 18.6 chronologically must be from 2024
    - Dates before/on 18.6 are from 2025
    """
    enhanced_sessions = []
    
    for date_str in sessions_list:
        day, month = parse_day_month(date_str)
        
        if day is None or month is None:
            # Keep original if can't parse
            enhanced_sessions.append(date_str)
            continue
        
        # Determine year based on position relative to current date
        if month > current_date.month or (month == current_date.month and day > current_date.day):
            # This date is chronologically after today, so it must be 2024
            year = 2024
        else:
            # This date is chronologically before/on today, so it's 2025
            year = 2025
        
        # Create enhanced date format
        enhanced_date = f"{day:02d}.{month:02d}.{year}"
        enhanced_sessions.append(enhanced_date)
    
    return enhanced_sessions

def sort_sessions_chronologically(sessions_with_years):
    """Sort sessions chronologically across years."""
    def date_sort_key(date_str):
        try:
            parts = date_str.split('.')
            if len(parts) == 3:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                return datetime(year, month, day)
            elif len(parts) == 2:
                # Fallback for old format
                day, month = int(parts[0]), int(parts[1])
                return datetime(2025, month, day)  # Default to 2025
        except:
            pass
        return datetime(1900, 1, 1)  # Fallback for unparseable dates
    
    return sorted(sessions_with_years, key=date_sort_key)

def enhance_client_dates(client_data):
    """Enhance dates for a single client."""
    enhanced_client = client_data.copy()
    
    # Process paid sessions
    if 'paid' in client_data and client_data['paid']:
        enhanced_paid = determine_year_intelligent(client_data['paid'])
        enhanced_client['paid'] = sort_sessions_chronologically(enhanced_paid)
    
    # Process unpaid sessions  
    if 'unpaid' in client_data and client_data['unpaid']:
        enhanced_unpaid = determine_year_intelligent(client_data['unpaid'])
        enhanced_client['unpaid'] = sort_sessions_chronologically(enhanced_unpaid)
    
    return enhanced_client

def enhance_all_dates(input_file, output_file):
    """
    Process the entire JSON file and enhance all dates with proper years.
    """
    print(f"Loading data from {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {input_file} not found!")
        return False
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {input_file}!")
        return False
    
    enhanced_data = {
        "clients": {},
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "date_enhancement": {
            "enhanced_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reference_date": "2025-06-18",
            "logic": "Dates after 18.6 are 2024, dates before/on 18.6 are 2025"
        }
    }
    
    total_clients = len(data.get('clients', {}))
    processed = 0
    
    print(f"Processing {total_clients} clients...")
    
    for client_name, client_data in data.get('clients', {}).items():
        enhanced_client = enhance_client_dates(client_data)
        enhanced_data['clients'][client_name] = enhanced_client
        
        processed += 1
        if processed % 20 == 0:
            print(f"  Processed {processed}/{total_clients} clients...")
    
    # Save enhanced data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Enhanced data saved to {output_file}")
    return True

def show_sample_enhancements(input_file, sample_clients=3):
    """Show before/after examples for a few clients."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        print("Could not load sample data")
        return
    
    print("\n📋 SAMPLE ENHANCEMENTS:")
    print("=" * 60)
    
    clients_shown = 0
    for client_name, client_data in data.get('clients', {}).items():
        if clients_shown >= sample_clients:
            break
        
        if client_data.get('paid') or client_data.get('unpaid'):
            print(f"\n👤 {client_name}:")
            
            # Show paid sessions enhancement
            if client_data.get('paid'):
                original_paid = client_data['paid'][:5]  # First 5
                enhanced_paid = determine_year_intelligent(client_data['paid'])[:5]
                
                print(f"  💰 Paid sessions (first 5):")
                print(f"    Before: {original_paid}")
                print(f"    After:  {enhanced_paid}")
            
            # Show unpaid sessions enhancement  
            if client_data.get('unpaid'):
                original_unpaid = client_data['unpaid'][:3]  # First 3
                enhanced_unpaid = determine_year_intelligent(client_data['unpaid'])[:3]
                
                print(f"  ⏳ Unpaid sessions:")
                print(f"    Before: {original_unpaid}")
                print(f"    After:  {enhanced_unpaid}")
            
            clients_shown += 1

def main():
    input_file = "all_clients_sessions.json"
    output_file = "all_clients_sessions_enhanced.json"
    
    print("🗓️  FITNESS SESSION DATE ENHANCER")
    print("=" * 50)
    print("📅 Reference: Today is 18.06.2025")
    print("🔍 Logic: Dates after 18.6 → 2024, dates before/on 18.6 → 2025")
    print()
    
    # Show sample enhancements first
    show_sample_enhancements(input_file)
    
    # Process all data
    print("\n🚀 PROCESSING ALL CLIENTS...")
    success = enhance_all_dates(input_file, output_file)
    
    if success:
        print(f"\n📊 SUMMARY:")
        print(f"✅ Input:  {input_file}")
        print(f"✅ Output: {output_file}")
        print(f"✅ All dates enhanced with proper years")
        print(f"✅ Sessions sorted chronologically")
        print("\n🎯 Enhanced format: DD.MM.YYYY (e.g., 10.06.2024)")

if __name__ == "__main__":
    main()