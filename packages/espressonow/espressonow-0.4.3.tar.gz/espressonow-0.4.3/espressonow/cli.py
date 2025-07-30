"""
Command Line Interface for EspressoNow
"""

import click
import os
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv
import urllib.parse
from datetime import datetime
import yaml
import yaypp

from .core import CoffeeShopFinder
from .location import LocationService
from .models import CoffeeShop, Location

# Load environment variables
load_dotenv()

console = Console()


def format_rating(rating: Optional[float]) -> str:
    """Format rating with stars"""
    if rating is None:
        return "No rating"
    
    stars = "⭐" * int(rating)
    return f"{stars} ({rating:.1f})"


def format_distance(distance: Optional[float], use_miles: bool = False) -> str:
    """Format distance in km or miles"""
    if distance is None:
        return "Unknown"
    
    if use_miles:
        distance_miles = distance * 0.621371  # Convert km to miles
        if distance_miles < 0.1:
            return f"{distance_miles * 5280:.0f}ft"  # Show feet for very short distances
        else:
            return f"{distance_miles:.1f}mi"
    else:
        if distance < 1:
            return f"{distance * 1000:.0f}m"
        else:
            return f"{distance:.1f}km"


def generate_google_maps_link(coffee_shop: CoffeeShop) -> str:
    """Generate a short Google Maps link for the coffee shop"""
    # Use the coffee shop name and coordinates for the search
    query = f"{coffee_shop.name} {coffee_shop.location.latitude},{coffee_shop.location.longitude}"
    encoded_query = urllib.parse.quote(query)
    return f"https://maps.google.com/?q={encoded_query}"


def get_current_day_hours(opening_hours: Optional[list]) -> str:
    """Get opening hours for the current day with color coding"""
    if not opening_hours:
        return "[dim]Hours N/A[/dim]"
    
    # Get current day of week (0=Monday, 6=Sunday)
    current_day = datetime.now().weekday()
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    current_day_name = day_names[current_day]
    
    # Look for today's hours
    for hours in opening_hours:
        if current_day_name.lower() in hours.lower():
            # Extract just the hours part, removing the day name
            hours_part = hours.split(": ", 1)
            if len(hours_part) > 1:
                hours_text = hours_part[1]
            else:
                hours_text = hours
            
            # Check if currently open
            if is_currently_open(hours_text):
                return f"[green]{hours_text}[/green]"
            else:
                return f"[red]{hours_text}[/red]"
    
    # If no specific day found, return first entry or default
    if opening_hours:
        hours_text = opening_hours[0]
        if is_currently_open(hours_text):
            return f"[green]{hours_text}[/green]"
        else:
            return f"[red]{hours_text}[/red]"
    
    return "[dim]Hours N/A[/dim]"


def is_currently_open(hours_text: str) -> bool:
    """Check if a coffee shop is currently open based on hours text"""
    if not hours_text or hours_text.lower() in ['closed', 'hours n/a']:
        return False
    
    try:
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_total_minutes = current_hour * 60 + current_minute
        
        # Handle common formats like "7:00 AM – 3:00 PM" or "7:30 AM – 2:30 PM"
        if '–' in hours_text or '-' in hours_text:
            # Split on either dash type
            separator = '–' if '–' in hours_text else '-'
            parts = hours_text.split(separator)
            if len(parts) == 2:
                start_time_str = parts[0].strip()
                end_time_str = parts[1].strip()
                
                # Parse start time
                start_minutes = parse_time_to_minutes(start_time_str)
                end_minutes = parse_time_to_minutes(end_time_str)
                
                if start_minutes is not None and end_minutes is not None:
                    # Handle overnight hours (like 10 PM - 2 AM)
                    if end_minutes < start_minutes:
                        # Overnight hours
                        return current_total_minutes >= start_minutes or current_total_minutes <= end_minutes
                    else:
                        # Normal hours
                        return start_minutes <= current_total_minutes <= end_minutes
        
        return False  # Default to closed if we can't parse
    except:
        return False  # Default to closed on any error


def parse_time_to_minutes(time_str: str) -> Optional[int]:
    """Parse time string like '7:30 AM' to minutes since midnight"""
    try:
        time_str = time_str.strip()
        
        # Handle AM/PM
        is_pm = 'PM' in time_str.upper()
        is_am = 'AM' in time_str.upper()
        
        # Remove AM/PM
        time_str = time_str.replace('AM', '').replace('PM', '').replace('am', '').replace('pm', '').strip()
        
        # Parse hour:minute
        if ':' in time_str:
            hour_str, minute_str = time_str.split(':')
            hour = int(hour_str)
            minute = int(minute_str)
        else:
            hour = int(time_str)
            minute = 0
        
        # Convert to 24-hour format
        if is_pm and hour != 12:
            hour += 12
        elif is_am and hour == 12:
            hour = 0
        
        return hour * 60 + minute
    except:
        return None


def display_coffee_shops(coffee_shops: list[CoffeeShop], location: Location, use_miles: bool = False):
    """Display coffee shops in a beautiful table"""
    if not coffee_shops:
        console.print("[yellow]No coffee shops found in the area.[/yellow]")
        return
    
    table = Table(title="☕ Specialty Coffee Shops Near You", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", width=40)
    table.add_column("Google Maps", style="blue")
    table.add_column("Rating", justify="center")
    table.add_column("Today's Hours", style="white")  # Changed from green to white since we color-code inside
    table.add_column("Distance", justify="right", style="yellow")
    
    for shop in coffee_shops:
        maps_link = generate_google_maps_link(shop)
        today_hours = get_current_day_hours(shop.opening_hours)
        
        table.add_row(
            shop.name,
            f"[link={maps_link}]📍 View on Maps[/link]",
            format_rating(shop.rating),
            today_hours,
            format_distance(shop.distance, use_miles)
        )
    
    console.print(table)


@click.group(invoke_without_command=True)
@click.version_option(version="0.4.3", prog_name="EspressoNow")
@click.option('--radius', '-r', default=3.0, help='Search radius (default: 3.0)')
@click.option('--max-results', '-n', default=10, help='Maximum number of results (default: 10)')
@click.option('--location', '-l', help='Search location (address or "lat,lng")')
@click.option('--api-key', help='Google Places API key (or set GOOGLE_PLACES_API_KEY env var)')
@click.option('--min-rating', type=float, help='Minimum rating (e.g., 4.0 for >4 stars)')
@click.option('--exclude-chains', is_flag=True, help='Exclude chain coffee shops (Starbucks, Dunkin, etc.)')
@click.option('--specialty-only', is_flag=True, default=True, help='Show only specialty coffee (4+ stars, no chains) - DEFAULT')
@click.option('--include-all', is_flag=True, help='Include all coffee shops (disables specialty-only default)')
@click.option('--miles', is_flag=True, default=True, help='Use miles instead of kilometers (DEFAULT)')
@click.option('--km', is_flag=True, help='Use kilometers instead of miles')
@click.option('--open', is_flag=True, help='Show only currently open coffee shops')
@click.option('--export-yaml', help='Export results to YAML file (e.g., --export-yaml results.yaml)')
@click.pass_context
def cli(ctx, radius: float, max_results: int, location: Optional[str], api_key: Optional[str], 
        min_rating: Optional[float], exclude_chains: bool, specialty_only: bool, include_all: bool, miles: bool, km: bool, open: bool, export_yaml: Optional[str]):
    """☕ EspressoNow - Find specialty coffee shops near you!
    
    Run 'espresso' to search with default settings, or use 'espresso search' for the same functionality.
    Use 'espresso config' to check your API key configuration.
    """
    # Handle km flag overriding miles default
    if km:
        miles = False
    
    if ctx.invoked_subcommand is None:
        # No subcommand provided, run search with the provided options
        ctx.invoke(search, radius=radius, max_results=max_results, location=location, 
                  api_key=api_key, min_rating=min_rating, exclude_chains=exclude_chains,
                  specialty_only=specialty_only, include_all=include_all, miles=miles, open=open, export_yaml=export_yaml)


@cli.command()
@click.option('--radius', '-r', default=3.0, help='Search radius (default: 3.0)')
@click.option('--max-results', '-n', default=10, help='Maximum number of results (default: 10)')
@click.option('--location', '-l', help='Search location (address or "lat,lng")')
@click.option('--api-key', help='Google Places API key (or set GOOGLE_PLACES_API_KEY env var)')
@click.option('--min-rating', type=float, help='Minimum rating (e.g., 4.0 for >4 stars)')
@click.option('--exclude-chains', is_flag=True, help='Exclude chain coffee shops (Starbucks, Dunkin, etc.)')
@click.option('--specialty-only', is_flag=True, default=True, help='Show only specialty coffee (4+ stars, no chains) - DEFAULT')
@click.option('--include-all', is_flag=True, help='Include all coffee shops (disables specialty-only default)')
@click.option('--miles', is_flag=True, default=True, help='Use miles instead of kilometers (DEFAULT)')
@click.option('--km', is_flag=True, help='Use kilometers instead of miles')
@click.option('--open', is_flag=True, help='Show only currently open coffee shops')
@click.option('--export-yaml', help='Export results to YAML file (e.g., --export-yaml results.yaml)')
def search(radius: float, max_results: int, location: Optional[str], api_key: Optional[str], 
          min_rating: Optional[float], exclude_chains: bool, specialty_only: bool, include_all: bool, miles: bool, km: bool, open: bool, export_yaml: Optional[str]):
    """Search for specialty coffee shops near your location"""
    
    # Handle km flag overriding miles default
    if km:
        miles = False
    
    # Handle the new default behavior
    if include_all:
        specialty_only = False
        exclude_chains = False
        min_rating = None
    elif specialty_only and not min_rating and not exclude_chains:
        # Default specialty-only behavior
        min_rating = 4.0
        exclude_chains = True
    elif specialty_only:
        # Explicit specialty-only flag
        min_rating = 4.0
        exclude_chains = True
    
    # Initialize services
    location_service = LocationService()
    finder = CoffeeShopFinder(api_key=api_key)
    
    # Determine search location
    search_location = None
    
    if location:
        # Parse provided location
        if ',' in location and location.replace(',', '').replace('.', '').replace('-', '').replace(' ', '').isdigit():
            # Looks like coordinates
            try:
                lat, lng = map(float, location.split(','))
                search_location = Location(latitude=lat, longitude=lng)
                console.print(f"[green]Using provided coordinates: {lat}, {lng}[/green]")
            except ValueError:
                console.print(f"[red]Invalid coordinates format: {location}[/red]")
                return
        else:
            # Treat as address
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Geocoding address...", total=None)
                search_location = location_service.get_location_from_address(location)
            
            if not search_location:
                console.print(f"[red]Could not find location: {location}[/red]")
                return
            
            console.print(f"[green]Found location: {location_service.format_location(search_location)}[/green]")
    else:
        # Auto-detect current location
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Detecting your location...", total=None)
            search_location = location_service.get_current_location()
        
        if not search_location:
            console.print("[red]Could not detect your location. Please provide a location with --location[/red]")
            return
        
        console.print(f"[green]Detected location: {location_service.format_location(search_location)}[/green]")
    
    # Search for coffee shops
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Searching for coffee shops...", total=None)
        result = finder.search_nearby(
            search_location, 
            radius, 
            max_results,
            min_rating=min_rating,
            exclude_chains=exclude_chains,
            use_miles=miles,
            open_only=open
        )
    
    # Display results
    console.print()
    
    # Create search info with filter details
    filter_info = []
    if min_rating:
        filter_info.append(f"⭐ Min Rating: {min_rating}")
    if exclude_chains:
        filter_info.append("🚫 Chains Excluded")
    if open:
        filter_info.append("🕐 Open Now Only")
    if specialty_only and not include_all:
        filter_info.append("☕ Specialty Only (Default)")
    if include_all:
        filter_info.append("🔍 All Coffee Shops")
    
    filter_text = " | ".join(filter_info)
    
    # Format radius display
    radius_unit = "mi" if miles else "km"
    search_info_text = (
        f"📍 Search Location: {location_service.format_location(search_location)}\n"
        f"🔍 Search Radius: {radius}{radius_unit}\n"
        f"📊 Results Found: {result.total_results}"
    )
    
    if filter_text:
        search_info_text += f"\n🔧 Filters: {filter_text}"
    
    location_info = Panel(
        search_info_text,
        title="Search Info",
        border_style="blue"
    )
    console.print(location_info)
    console.print()
    
    display_coffee_shops(result.coffee_shops, search_location, miles)
    
    # Export to YAML if requested
    if export_yaml:
        try:
            exported_count = export_to_yaml(result.coffee_shops, search_location, radius, miles, export_yaml)
            console.print()
            console.print(Panel(
                f"✅ Successfully exported {exported_count} coffee shops to [cyan]{export_yaml}[/cyan]\n\n"
                f"📄 File contains:\n"
                f"   • Search metadata (location, radius, timestamp)\n"
                f"   • Complete coffee shop details\n"
                f"   • Formatted with yaypp for clean YAML structure",
                title="YAML Export Complete",
                border_style="green"
            ))
        except Exception as e:
            console.print()
            console.print(Panel(
                f"❌ Failed to export to YAML: {str(e)}",
                title="Export Error",
                border_style="red"
            ))
    
    if not finder.api_key:
        console.print()
        console.print(Panel(
            "🔑 [yellow]API Key Required:[/yellow] To search for coffee shops, you need a Google Places API key.\n\n"
            "   • Set environment variable: [cyan]GOOGLE_PLACES_API_KEY=your_key[/cyan]\n"
            "   • Or use: [cyan]--api-key your_key[/cyan]\n"
            "   • Get a key at: https://developers.google.com/places/web-service/get-api-key",
            title="No API Key Configured",
            border_style="red"
        ))
    elif result.total_results == 0:
        console.print()
        suggestions = [
            "🔍 Try expanding your search:",
            "   • Increase the search radius with [cyan]--radius[/cyan]",
            "   • Search in a different location with [cyan]--location[/cyan]"
        ]
        
        if min_rating or exclude_chains:
            suggestions.extend([
                "   • Include all coffee shops with [cyan]--include-all[/cyan]",
                "   • Lower the minimum rating with [cyan]--min-rating[/cyan]"
            ])
        else:
            suggestions.append("   • Check that your location has coffee shops nearby")
        
        console.print(Panel(
            "\n".join(suggestions),
            title="No Results Found",
            border_style="yellow"
        ))


@cli.command()
def config():
    """Show configuration information"""
    
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    
    config_table = Table(title="EspressoNow Configuration", show_header=True, header_style="bold cyan")
    config_table.add_column("Setting", style="white", no_wrap=True)
    config_table.add_column("Value", style="green")
    config_table.add_column("Status", justify="center")
    
    config_table.add_row(
        "Google Places API Key",
        "***" + api_key[-4:] if api_key else "Not set",
        "✅ Set" if api_key else "❌ Missing"
    )
    
    console.print(config_table)
    
    if not api_key:
        console.print()
        console.print(Panel(
            "To get real coffee shop data, you need a Google Places API key:\n\n"
            "1. Go to: https://developers.google.com/places/web-service/get-api-key\n"
            "2. Create a project and enable the Places API\n"
            "3. Create an API key\n"
            "4. Set it as an environment variable:\n"
            "   [cyan]export GOOGLE_PLACES_API_KEY=your_key_here[/cyan]\n"
            "5. Or create a .env file with:\n"
            "   [cyan]GOOGLE_PLACES_API_KEY=your_key_here[/cyan]",
            title="Setup Instructions",
            border_style="blue"
        ))


def export_to_yaml(coffee_shops: list[CoffeeShop], search_location: Location, search_radius: float, use_miles: bool, filename: str):
    """Export coffee shop results to a YAML file using yaypp"""
    
    # Convert coffee shops to dictionaries
    shops_data = []
    for shop in coffee_shops:
        shop_dict = {
            'name': shop.name,
            'address': shop.address,
            'location': {
                'latitude': shop.location.latitude,
                'longitude': shop.location.longitude
            },
            'rating': shop.rating,
            'price_level': shop.price_level,
            'phone': shop.phone,
            'opening_hours': shop.opening_hours,
            'distance': shop.distance,
            'distance_unit': 'miles' if use_miles else 'kilometers',
            'place_id': shop.place_id
        }
        shops_data.append(shop_dict)
    
    # Create the complete export data
    export_data = {
        'search_info': {
            'location': {
                'latitude': search_location.latitude,
                'longitude': search_location.longitude,
                'address': search_location.address,
                'city': search_location.city,
                'country': search_location.country
            },
            'search_radius': search_radius,
            'radius_unit': 'miles' if use_miles else 'kilometers',
            'total_results': len(coffee_shops),
            'exported_at': datetime.now().isoformat()
        },
        'coffee_shops': shops_data
    }
    
    # Convert to YAML and format with yaypp
    yaml_str = yaml.dump(export_data, default_flow_style=False, sort_keys=False)
    formatted_yaml = yaypp.format_yaml(yaml_str)
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(formatted_yaml)
    
    return len(coffee_shops)


def main():
    """Main entry point"""
    cli()


if __name__ == '__main__':
    main() 