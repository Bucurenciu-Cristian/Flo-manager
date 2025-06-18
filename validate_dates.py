# /// script
# dependencies = [
#   "openpyxl",
# ]
# ///

import json
from datetime import datetime

def validate_date_enhancements():
    """Compare original vs enhanced dates to validate the enhancement logic."""
    
    print("🔍 DATE ENHANCEMENT VALIDATION")
    print("=" * 50)
    
    # Load original data
    try:
        with open("all_clients_sessions.json", 'r', encoding='utf-8') as f:
            original_data = json.load(f)
    except:
        print("❌ Could not load original data")
        return
    
    # Load enhanced data
    try:
        with open("all_clients_sessions_enhanced.json", 'r', encoding='utf-8') as f:
            enhanced_data = json.load(f)
    except:
        print("❌ Could not load enhanced data")
        return
    
    print("✅ Loaded both datasets successfully\n")
    
    # Test key clients
    test_clients = ["Alexandra Boboc", "Ada Pinciu", "Adriana Bazarea"]
    
    for client_name in test_clients:
        if client_name in original_data['clients'] and client_name in enhanced_data['clients']:
            print(f"👤 {client_name}:")
            
            original_client = original_data['clients'][client_name]
            enhanced_client = enhanced_data['clients'][client_name]
            
            # Compare paid sessions
            if original_client.get('paid'):
                print(f"  💰 Paid sessions:")
                print(f"    Original (first 5): {original_client['paid'][:5]}")
                print(f"    Enhanced (first 5): {enhanced_client['paid'][:5]}")
                
                # Show chronological improvement
                enhanced_sorted = enhanced_client['paid']
                if len(enhanced_sorted) > 1:
                    print(f"    ✅ Chronologically sorted: {enhanced_sorted[0]} → {enhanced_sorted[-1]}")
            
            # Compare unpaid sessions
            if original_client.get('unpaid'):
                print(f"  ⏳ Unpaid sessions:")
                print(f"    Original: {original_client['unpaid']}")
                print(f"    Enhanced: {enhanced_client['unpaid']}")
            
            print()
    
    # Validation summary
    total_clients = len(enhanced_data['clients'])
    sessions_with_years = 0
    
    for client_data in enhanced_data['clients'].values():
        for session in client_data.get('paid', []) + client_data.get('unpaid', []):
            if '2024' in session or '2025' in session:
                sessions_with_years += 1
    
    print("📊 VALIDATION SUMMARY:")
    print(f"✅ Total clients processed: {total_clients}")
    print(f"✅ Sessions with years: {sessions_with_years}")
    print(f"✅ Enhancement metadata: {enhanced_data.get('date_enhancement', {}).get('logic', 'N/A')}")
    print(f"✅ Reference date: {enhanced_data.get('date_enhancement', {}).get('reference_date', 'N/A')}")

def show_year_distribution():
    """Show distribution of 2024 vs 2025 sessions."""
    try:
        with open("all_clients_sessions_enhanced.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        print("❌ Could not load enhanced data")
        return
    
    year_2024_count = 0
    year_2025_count = 0
    
    for client_data in data['clients'].values():
        for session in client_data.get('paid', []) + client_data.get('unpaid', []):
            if '2024' in session:
                year_2024_count += 1
            elif '2025' in session:
                year_2025_count += 1
    
    total = year_2024_count + year_2025_count
    
    print("\n📅 YEAR DISTRIBUTION:")
    print(f"📊 2024 sessions: {year_2024_count} ({year_2024_count/total*100:.1f}%)")
    print(f"📊 2025 sessions: {year_2025_count} ({year_2025_count/total*100:.1f}%)")
    print(f"📊 Total sessions: {total}")

if __name__ == "__main__":
    validate_date_enhancements()
    show_year_distribution()