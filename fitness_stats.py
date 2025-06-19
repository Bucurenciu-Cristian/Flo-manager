# /// script
# dependencies = [
#   "rich",
# ]
# ///

import json
import sys
from datetime import datetime, date
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.progress import track

console = Console()

def load_fitness_data(filename: str = "fitness_sessions_api.json") -> Dict[str, Any]:
    """Load the fitness sessions data from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: {filename} not found![/red]")
        console.print("[yellow]Make sure to run extract_sessions.py first to generate the data.[/yellow]")
        sys.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]Error: Invalid JSON in {filename}![/red]")
        sys.exit(1)

def parse_date(date_str: str) -> date:
    """Parse ISO date string to date object."""
    try:
        return datetime.fromisoformat(date_str).date()
    except:
        return None

def get_overview_stats(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overview statistics."""
    clients = data['clients']
    total_clients = len(clients)
    
    # Basic counts
    active_clients = len([c for c in clients if c['stats']['totalCurrent'] > 0])
    clients_with_previous = len([c for c in clients if c['stats']['previousCompleted'] > 0])
    clients_with_unpaid = len([c for c in clients if c['stats']['currentUnpaid'] > 0])
    
    # Session totals
    total_sessions_current = sum(c['stats']['totalCurrent'] for c in clients)
    total_sessions_all_time = sum(c['stats']['totalAllTime'] for c in clients)
    total_previous_sessions = sum(c['stats']['previousCompleted'] for c in clients)
    total_paid_used = sum(c['stats']['currentPaidUsed'] for c in clients)
    total_remaining = sum(c['stats']['currentRemaining'] for c in clients)
    total_unpaid = sum(c['stats']['currentUnpaid'] for c in clients)
    
    # Financial calculations (assuming average session price)
    avg_session_price = 100  # Lei per session (configurable)
    revenue_from_paid = total_paid_used * avg_session_price
    potential_revenue_remaining = total_remaining * avg_session_price
    outstanding_unpaid = total_unpaid * avg_session_price
    
    return {
        'total_clients': total_clients,
        'active_clients': active_clients,
        'clients_with_previous': clients_with_previous,
        'clients_with_unpaid': clients_with_unpaid,
        'total_sessions_current': total_sessions_current,
        'total_sessions_all_time': total_sessions_all_time,
        'total_previous_sessions': total_previous_sessions,
        'total_paid_used': total_paid_used,
        'total_remaining': total_remaining,
        'total_unpaid': total_unpaid,
        'revenue_from_paid': revenue_from_paid,
        'potential_revenue_remaining': potential_revenue_remaining,
        'outstanding_unpaid': outstanding_unpaid,
        'avg_session_price': avg_session_price
    }

def get_date_analytics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze session dates and patterns."""
    all_sessions = []
    monthly_counts = defaultdict(int)
    daily_counts = defaultdict(int)
    
    for client in track(data['clients'], description="Analyzing dates..."):
        # Paid sessions
        for session in client['sessions']['paid']:
            session_date = parse_date(session['date'])
            if session_date:
                all_sessions.append(session_date)
                month_key = session_date.strftime('%Y-%m')
                day_key = session_date.strftime('%A')
                monthly_counts[month_key] += 1
                daily_counts[day_key] += 1
        
        # Unpaid sessions
        for session in client['sessions']['unpaid']:
            session_date = parse_date(session['date'])
            if session_date:
                all_sessions.append(session_date)
                month_key = session_date.strftime('%Y-%m')
                day_key = session_date.strftime('%A')
                monthly_counts[month_key] += 1
                daily_counts[day_key] += 1
    
    # Sort dates
    all_sessions.sort()
    
    # Find date range
    first_session = all_sessions[0] if all_sessions else None
    last_session = all_sessions[-1] if all_sessions else None
    
    # Most active periods
    busiest_month = max(monthly_counts.items(), key=lambda x: x[1]) if monthly_counts else (None, 0)
    busiest_day = max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else (None, 0)
    
    return {
        'total_dated_sessions': len(all_sessions),
        'first_session': first_session,
        'last_session': last_session,
        'monthly_counts': dict(monthly_counts),
        'daily_counts': dict(daily_counts),
        'busiest_month': busiest_month,
        'busiest_day': busiest_day
    }

def get_client_rankings(data: Dict[str, Any]) -> Dict[str, List[Tuple[str, int]]]:
    """Get client rankings by various metrics."""
    clients = data['clients']
    
    # Sort by different metrics
    by_total_sessions = sorted(clients, key=lambda c: c['stats']['totalAllTime'], reverse=True)[:10]
    by_current_activity = sorted(clients, key=lambda c: c['stats']['totalCurrent'], reverse=True)[:10]
    by_previous_sessions = sorted(clients, key=lambda c: c['stats']['previousCompleted'], reverse=True)[:10]
    by_unpaid = sorted(clients, key=lambda c: c['stats']['currentUnpaid'], reverse=True)[:10]
    
    return {
        'top_all_time': [(c['name'], c['stats']['totalAllTime']) for c in by_total_sessions],
        'top_current': [(c['name'], c['stats']['totalCurrent']) for c in by_current_activity],
        'top_previous': [(c['name'], c['stats']['previousCompleted']) for c in by_previous_sessions],
        'top_unpaid': [(c['name'], c['stats']['currentUnpaid']) for c in by_unpaid if c['stats']['currentUnpaid'] > 0]
    }

def get_session_patterns(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze session patterns and distributions."""
    clients = data['clients']
    
    # Session count distributions
    session_ranges = {
        '0 sessions': 0,
        '1-5 sessions': 0,
        '6-10 sessions': 0,
        '11-20 sessions': 0,
        '21-50 sessions': 0,
        '51-100 sessions': 0,
        '100+ sessions': 0
    }
    
    # Payment patterns
    payment_patterns = {
        'only_paid': 0,
        'only_unpaid': 0,
        'mixed_payment': 0,
        'no_sessions': 0
    }
    
    # Remaining session distribution
    remaining_ranges = {
        '0 remaining': 0,
        '1-5 remaining': 0,
        '6-10 remaining': 0,
        '11-20 remaining': 0,
        '20+ remaining': 0
    }
    
    for client in clients:
        total = client['stats']['totalCurrent']
        paid = client['stats']['currentPaidUsed']
        unpaid = client['stats']['currentUnpaid']
        remaining = client['stats']['currentRemaining']
        
        # Session count ranges
        if total == 0:
            session_ranges['0 sessions'] += 1
        elif total <= 5:
            session_ranges['1-5 sessions'] += 1
        elif total <= 10:
            session_ranges['6-10 sessions'] += 1
        elif total <= 20:
            session_ranges['11-20 sessions'] += 1
        elif total <= 50:
            session_ranges['21-50 sessions'] += 1
        elif total <= 100:
            session_ranges['51-100 sessions'] += 1
        else:
            session_ranges['100+ sessions'] += 1
        
        # Payment patterns
        if total == 0:
            payment_patterns['no_sessions'] += 1
        elif paid > 0 and unpaid == 0:
            payment_patterns['only_paid'] += 1
        elif paid == 0 and unpaid > 0:
            payment_patterns['only_unpaid'] += 1
        elif paid > 0 and unpaid > 0:
            payment_patterns['mixed_payment'] += 1
        
        # Remaining sessions
        if remaining == 0:
            remaining_ranges['0 remaining'] += 1
        elif remaining <= 5:
            remaining_ranges['1-5 remaining'] += 1
        elif remaining <= 10:
            remaining_ranges['6-10 remaining'] += 1
        elif remaining <= 20:
            remaining_ranges['11-20 remaining'] += 1
        else:
            remaining_ranges['20+ remaining'] += 1
    
    return {
        'session_ranges': session_ranges,
        'payment_patterns': payment_patterns,
        'remaining_ranges': remaining_ranges
    }

def display_overview(stats: Dict[str, Any]):
    """Display overview statistics."""
    table = Table(title="📊 Fitness Center Overview", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", width=25)
    table.add_column("Value", style="green", width=15)
    table.add_column("Details", style="yellow")
    
    table.add_row("Total Clients", str(stats['total_clients']), "All registered clients")
    table.add_row("Active Clients", str(stats['active_clients']), "Clients with current sessions")
    table.add_row("Clients with History", str(stats['clients_with_previous']), "Clients with previous sessions")
    table.add_row("Clients with Unpaid", str(stats['clients_with_unpaid']), "Clients owing payment")
    
    table.add_section()
    table.add_row("Current Sessions", str(stats['total_sessions_current']), "This tracking period")
    table.add_row("All-Time Sessions", str(stats['total_sessions_all_time']), "Including previous sessions")
    table.add_row("Previous Sessions", str(stats['total_previous_sessions']), "Historical sessions")
    
    table.add_section()
    table.add_row("Paid & Used", str(stats['total_paid_used']), "Completed paid sessions")
    table.add_row("Pre-paid Remaining", str(stats['total_remaining']), "Available sessions")
    table.add_row("Unpaid Sessions", str(stats['total_unpaid']), "Sessions taken but not paid")
    
    table.add_section()
    price = stats['avg_session_price']
    table.add_row("Revenue (Paid)", f"{stats['revenue_from_paid']:,} Lei", f"@ {price} Lei/session")
    table.add_row("Potential Revenue", f"{stats['potential_revenue_remaining']:,} Lei", "From remaining sessions")
    table.add_row("Outstanding Debt", f"{stats['outstanding_unpaid']:,} Lei", "From unpaid sessions")
    
    console.print(table)

def display_rankings(rankings: Dict[str, List[Tuple[str, int]]]):
    """Display client rankings."""
    tables = []
    
    # Top all-time clients
    if rankings['top_all_time']:
        table1 = Table(title="🏆 Top All-Time Clients", show_header=True)
        table1.add_column("Rank", style="yellow", width=5)
        table1.add_column("Client", style="cyan", width=20)
        table1.add_column("Sessions", style="green", width=8)
        
        for i, (name, count) in enumerate(rankings['top_all_time'], 1):
            table1.add_row(str(i), name, str(count))
        tables.append(table1)
    
    # Top current activity
    if rankings['top_current']:
        table2 = Table(title="🔥 Most Active (Current)", show_header=True)
        table2.add_column("Rank", style="yellow", width=5)
        table2.add_column("Client", style="cyan", width=20)
        table2.add_column("Sessions", style="green", width=8)
        
        for i, (name, count) in enumerate(rankings['top_current'], 1):
            table2.add_row(str(i), name, str(count))
        tables.append(table2)
    
    # Top unpaid
    if rankings['top_unpaid']:
        table3 = Table(title="⚠️ Highest Unpaid", show_header=True)
        table3.add_column("Rank", style="yellow", width=5)
        table3.add_column("Client", style="cyan", width=20)
        table3.add_column("Unpaid", style="red", width=8)
        
        for i, (name, count) in enumerate(rankings['top_unpaid'], 1):
            table3.add_row(str(i), name, str(count))
        tables.append(table3)
    
    console.print(Columns(tables, equal=True, expand=True))

def display_date_analytics(date_stats: Dict[str, Any]):
    """Display date and time analytics."""
    if not date_stats['total_dated_sessions']:
        console.print("[yellow]No dated sessions found for analysis.[/yellow]")
        return
    
    # Date range info
    info_panel = Panel(
        f"📅 Date Range: {date_stats['first_session']} to {date_stats['last_session']}\n"
        f"📊 Total Dated Sessions: {date_stats['total_dated_sessions']}\n"
        f"🏆 Busiest Month: {date_stats['busiest_month'][0]} ({date_stats['busiest_month'][1]} sessions)\n"
        f"📈 Busiest Day: {date_stats['busiest_day'][0]} ({date_stats['busiest_day'][1]} sessions)",
        title="Date Analytics",
        title_align="left"
    )
    console.print(info_panel)
    
    # Monthly breakdown (last 12 months)
    monthly_table = Table(title="📅 Monthly Session Distribution", show_header=True)
    monthly_table.add_column("Month", style="cyan")
    monthly_table.add_column("Sessions", style="green")
    monthly_table.add_column("Bar", style="blue")
    
    sorted_months = sorted(date_stats['monthly_counts'].items())[-12:]  # Last 12 months
    max_monthly = max(date_stats['monthly_counts'].values()) if date_stats['monthly_counts'] else 1
    
    for month, count in sorted_months:
        bar_length = int((count / max_monthly) * 20)
        bar = "█" * bar_length
        monthly_table.add_row(month, str(count), bar)
    
    console.print(monthly_table)
    
    # Daily breakdown
    daily_table = Table(title="📈 Day of Week Distribution", show_header=True)
    daily_table.add_column("Day", style="cyan")
    daily_table.add_column("Sessions", style="green")
    daily_table.add_column("Bar", style="blue")
    
    # Order days properly
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    max_daily = max(date_stats['daily_counts'].values()) if date_stats['daily_counts'] else 1
    
    for day in day_order:
        count = date_stats['daily_counts'].get(day, 0)
        bar_length = int((count / max_daily) * 20)
        bar = "█" * bar_length
        daily_table.add_row(day, str(count), bar)
    
    console.print(daily_table)

def display_patterns(patterns: Dict[str, Any]):
    """Display session patterns and distributions."""
    tables = []
    
    # Session count distribution
    table1 = Table(title="📊 Session Count Distribution", show_header=True)
    table1.add_column("Range", style="cyan")
    table1.add_column("Clients", style="green")
    table1.add_column("Percentage", style="yellow")
    
    total_clients = sum(patterns['session_ranges'].values())
    for range_name, count in patterns['session_ranges'].items():
        percentage = (count / total_clients * 100) if total_clients > 0 else 0
        table1.add_row(range_name, str(count), f"{percentage:.1f}%")
    tables.append(table1)
    
    # Payment patterns
    table2 = Table(title="💳 Payment Patterns", show_header=True)
    table2.add_column("Pattern", style="cyan")
    table2.add_column("Clients", style="green")
    table2.add_column("Percentage", style="yellow")
    
    for pattern, count in patterns['payment_patterns'].items():
        percentage = (count / total_clients * 100) if total_clients > 0 else 0
        pattern_display = pattern.replace('_', ' ').title()
        table2.add_row(pattern_display, str(count), f"{percentage:.1f}%")
    tables.append(table2)
    
    console.print(Columns(tables, equal=True, expand=True))
    
    # Remaining sessions
    table3 = Table(title="🎯 Remaining Sessions Distribution", show_header=True)
    table3.add_column("Range", style="cyan")
    table3.add_column("Clients", style="green")
    table3.add_column("Percentage", style="yellow")
    
    for range_name, count in patterns['remaining_ranges'].items():
        percentage = (count / total_clients * 100) if total_clients > 0 else 0
        table3.add_row(range_name, str(count), f"{percentage:.1f}%")
    
    console.print(table3)

def export_stats_summary(stats: Dict[str, Any], filename: str = "fitness_stats_summary.json"):
    """Export statistics summary to JSON file."""
    summary = {
        'generated_at': datetime.now().isoformat(),
        'overview': stats,
        'export_note': 'Detailed statistics exported from fitness_stats.py'
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    
    console.print(f"\n[green]📁 Statistics summary exported to {filename}[/green]")

def main():
    """Main function to run all analytics."""
    console.print("\n[bold magenta]🏋️ Fitness Center Analytics Dashboard[/bold magenta]\n")
    
    # Load data
    console.print("[cyan]Loading fitness session data...[/cyan]")
    data = load_fitness_data()
    
    console.print(f"[green]✅ Loaded data for {len(data['clients'])} clients[/green]\n")
    
    # Calculate all statistics
    with console.status("[cyan]Calculating statistics..."):
        overview_stats = get_overview_stats(data)
        date_analytics = get_date_analytics(data)
        client_rankings = get_client_rankings(data)
        session_patterns = get_session_patterns(data)
    
    # Display results
    display_overview(overview_stats)
    console.print("\n")
    
    display_rankings(client_rankings)
    console.print("\n")
    
    display_date_analytics(date_analytics)
    console.print("\n")
    
    display_patterns(session_patterns)
    
    # Export summary
    export_stats_summary(overview_stats)
    
    console.print("\n[bold green]📊 Analytics complete![/bold green]")

if __name__ == "__main__":
    main()