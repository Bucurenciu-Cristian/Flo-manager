# /// script
# dependencies = [
#   "openpyxl",
# ]
# ///

import openpyxl
import json
from datetime import datetime

def extract_training_data(excel_file_path, max_clients=5):
    """
    Extract training session data from Excel file and convert to simplified JSON format.
    
    Args:
        excel_file_path: Path to the Excel file
        max_clients: Maximum number of clients to process (default: 5 for testing)
    """
    
    # Load the workbook
    wb = openpyxl.load_workbook(excel_file_path, data_only=True)
    ws = wb.active
    
    clients_data = {
        "clients": {},
        "updated": datetime.now().strftime("%Y-%m-%d")
    }
    
    # Find clients by looking for "Numele" cells
    row = 1
    clients_processed = 0
    
    while row <= ws.max_row and clients_processed < max_clients:
        cell_a = ws.cell(row=row, column=1)
        
        if cell_a.value and "Numele" in str(cell_a.value):
            # Get client name
            client_name = ws.cell(row=row, column=2).value
            
            if client_name:
                print(f"Processing: {client_name}")
                
                paid_sessions = []
                unpaid_sessions = []
                
                # Process session rows (starting from row+3)
                session_row = row + 3
                
                while session_row <= ws.max_row:
                    has_data = False
                    
                    # Check columns C through T for dates
                    for col in range(3, 21):
                        cell = ws.cell(row=session_row, column=col)
                        
                        if cell.value:
                            has_data = True
                            date_str = str(cell.value)
                            
                            # Check if cell is green (paid)
                            is_paid = False
                            fill = cell.fill
                            
                            if fill and fill.fgColor and fill.fgColor.rgb:
                                rgb = str(fill.fgColor.rgb)
                                # Simple green detection
                                if 'FF00FF00' in rgb or '00FF00' in rgb:
                                    is_paid = True
                                elif len(rgb) >= 6:
                                    try:
                                        # Check if it's mostly green
                                        r = int(rgb[-6:-4], 16)
                                        g = int(rgb[-4:-2], 16)
                                        b = int(rgb[-2:], 16)
                                        if g > 200 and r < 100 and b < 100:
                                            is_paid = True
                                    except:
                                        pass
                            
                            # Add to appropriate list
                            if is_paid:
                                paid_sessions.append(date_str)
                            else:
                                unpaid_sessions.append(date_str)
                    
                    if not has_data:
                        break
                    
                    session_row += 1
                
                # Calculate stats
                total = len(paid_sessions) + len(unpaid_sessions)
                packages_needed = (total + 9) // 10  # Round up to nearest 10
                remaining = (packages_needed * 10) - total
                
                clients_processed += 1
                
                # Add client data
                clients_data["clients"][client_name] = {
                    "paid": paid_sessions,
                    "unpaid": unpaid_sessions,
                    "stats": {
                        "total": total,
                        "paid": len(paid_sessions),
                        "unpaid": len(unpaid_sessions),
                        "remaining": remaining
                    }
                }
                
                print(f"  [{clients_processed}/{max_clients}] Processed {client_name}")
                
                # Move to next potential client
                row += 4
            else:
                row += 1
        else:
            row += 1
    
    return clients_data

def save_to_json(data, output_file="training_sessions.json"):
    """Save the extracted data to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nData saved to {output_file}")

def print_summary(data):
    """Print a summary of the extracted data."""
    print("\n=== SUMMARY ===")
    print(f"Clients processed: {len(data['clients'])}")
    
    for name, info in data['clients'].items():
        stats = info['stats']
        print(f"\n{name}:")
        print(f"  Sessions: {stats['total']} ({stats['paid']} paid, {stats['unpaid']} unpaid)")
        print(f"  Remaining: {stats['remaining']}")
    
    print("\n[This is a TEST RUN - only first 5 clients processed]")

# Main execution
if __name__ == "__main__":
    excel_file = "excel.xlsx"
    
    try:
        # Extract data (only first 5 clients for testing)
        print("Starting extraction (TEST MODE - first 5 clients only)...")
        training_data = extract_training_data(excel_file)
        
        # Save to JSON
        save_to_json(training_data, "training_sessions_test.json")
        
        # Print summary
        print_summary(training_data)
        
    except FileNotFoundError:
        print(f"Error: Could not find file '{excel_file}'")
    except Exception as e:
        print(f"Error: {e}")