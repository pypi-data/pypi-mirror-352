"""
Enhanced CLI for App Store Icon Hunter
"""

import click
import asyncio
import os
from pathlib import Path
from typing import Dict, List, Optional
import time

try:
    from ..core.app_store import AppStoreAPI
    from ..core.google_play import GooglePlayAPI
    from ..core.downloader import IconDownloader
    from ..utils.helpers import (
        format_app_name, clean_filename, validate_store_name, 
        validate_country_code, validate_icon_sizes, format_price, format_rating
    )
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.app_store import AppStoreAPI
    from core.google_play import GooglePlayAPI
    from core.downloader import IconDownloader
    from utils.helpers import (
        format_app_name, clean_filename, validate_store_name, 
        validate_country_code, validate_icon_sizes, format_price, format_rating
    )


class AppIconHunterCLI:
    """Main CLI class for App Store Icon Hunter"""
    
    def __init__(self):
        self.app_store_api = AppStoreAPI()
        self.google_play_api = GooglePlayAPI()
        self.downloader = IconDownloader()
        self.output_dir = Path("icons")
    
    def search_apps_combined(self, term: str, store: str = "both", 
                           country: str = "us", limit: int = 10) -> List[Dict]:
        """Search apps from specified stores"""
        all_apps = []
        
        # Search App Store
        if store in ["appstore", "both"]:
            click.echo("🔍 Searching App Store...")
            app_store_results = self.app_store_api.search_apps(term, country, limit)
            all_apps.extend(app_store_results)
            click.echo(f"  Found {len(app_store_results)} apps in App Store")
        
        # Search Google Play
        if store in ["googleplay", "both"]:
            click.echo("🔍 Searching Google Play...")
            google_play_results = self.google_play_api.search_apps(term, country, limit)
            all_apps.extend(google_play_results)
            click.echo(f"  Found {len(google_play_results)} apps in Google Play")
        
        return all_apps
    
    def display_apps_table(self, apps: List[Dict]) -> None:
        """Display apps in a formatted table"""
        if not apps:
            click.echo("No apps found.")
            return
        
        click.echo("\n" + "="*90)
        click.echo(f"{'#':<3} {'App Name':<30} {'Store':<12} {'Price':<12} {'Rating':<10} {'Developer':<20}")
        click.echo("="*90)
        
        for i, app in enumerate(apps, 1):
            name = format_app_name(app.get('name', 'Unknown'))
            if len(name) > 27:
                name = name[:27] + "..."
            
            store = app.get('store', '').upper()
            price = format_price(app.get('price', 'Free'))
            rating = format_rating(app.get('rating'))
            developer = app.get('developer', 'Unknown')
            if len(developer) > 17:
                developer = developer[:17] + "..."
            
            click.echo(f"{i:<3} {name:<30} {store:<12} {price:<12} {rating:<10} {developer:<20}")
        
        click.echo("="*90)
    
    def get_user_selection(self, apps: List[Dict]) -> List[Dict]:
        """Get user selection for which apps to download"""
        while True:
            click.echo("\nOptions:")
            click.echo("• Enter numbers separated by commas (e.g., 1,3,5)")
            click.echo("• Enter 'all' to download all apps")
            click.echo("• Enter 'q' to quit")
            
            selection = click.prompt("Your choice", type=str).strip().lower()
            
            if selection == 'q':
                return []
            elif selection == 'all':
                return apps
            else:
                try:
                    # Parse comma-separated numbers
                    indices = [int(x.strip()) for x in selection.split(',')]
                    selected_apps = []
                    
                    for idx in indices:
                        if 1 <= idx <= len(apps):
                            selected_apps.append(apps[idx - 1])
                        else:
                            click.echo(f"Invalid selection: {idx}")
                            break
                    else:
                        return selected_apps
                        
                except ValueError:
                    click.echo("Invalid input. Please enter numbers separated by commas.")
                except Exception as e:
                    click.echo(f"Error processing selection: {e}")
    
    def get_icon_sizes(self) -> List[int]:
        """Get desired icon sizes from user"""
        default_sizes = [64, 128, 256, 512]
        
        click.echo(f"\nDefault icon sizes: {', '.join(map(str, default_sizes))}")
        custom = click.confirm("Use custom sizes?", default=False)
        
        if custom:
            while True:
                sizes_input = click.prompt(
                    "Enter sizes separated by commas (16,32,48,64,128,256,512,1024)",
                    type=str
                )
                try:
                    sizes = [int(x.strip()) for x in sizes_input.split(',')]
                    valid_sizes = validate_icon_sizes(sizes)
                    
                    if valid_sizes:
                        return valid_sizes
                    else:
                        click.echo("No valid sizes provided. Valid sizes: 16,32,48,64,128,256,512,1024")
                        
                except ValueError:
                    click.echo("Invalid input. Please enter numbers separated by commas.")
        
        return default_sizes
    
    def download_selected_apps(self, apps: List[Dict], sizes: List[int]) -> None:
        """Download icons for selected apps"""
        if not apps:
            return
        
        click.echo(f"\n📥 Starting download for {len(apps)} apps...")
        click.echo(f"Icon sizes: {', '.join(map(str, sizes))}")
        
        successful_downloads = 0
        failed_downloads = 0
        
        with click.progressbar(apps, label='Downloading icons') as progress_apps:
            for app in progress_apps:
                app_name = app.get('name', 'Unknown App')
                icon_url = app.get('icon_url', '')
                
                if not icon_url:
                    click.echo(f"\n❌ No icon URL for {app_name}")
                    failed_downloads += 1
                    continue
                
                try:
                    downloaded_files = self.downloader.download_icon_sync(
                        icon_url, app_name, sizes
                    )
                    
                    if downloaded_files:
                        successful_downloads += 1
                        click.echo(f"\n✅ Downloaded {len(downloaded_files)} files for {app_name}")
                    else:
                        failed_downloads += 1
                        click.echo(f"\n❌ Failed to download {app_name}")
                        
                except Exception as e:
                    failed_downloads += 1
                    click.echo(f"\n❌ Error downloading {app_name}: {e}")
        
        # Summary
        click.echo(f"\n📊 Download Summary:")
        click.echo(f"✅ Successful: {successful_downloads}")
        click.echo(f"❌ Failed: {failed_downloads}")
        click.echo(f"📁 Output directory: {self.output_dir.absolute()}")


# CLI Commands
@click.group()
@click.version_option(version="2.0.0")
def cli():
    """🚀 App Store Icon Hunter - Search and download app icons"""
    pass


@cli.command()
@click.argument('term')
@click.option('--store', '-s', default='both', 
              type=click.Choice(['appstore', 'googleplay', 'both']),
              help='Store to search (default: both)')
@click.option('--country', '-c', default='us', 
              help='Country code (default: us)')
@click.option('--limit', '-l', default=10, type=int,
              help='Maximum results per store (default: 10)')
@click.option('--auto-download', '-a', is_flag=True,
              help='Automatically download all results')
@click.option('--sizes', '-z', default='64,128,256,512',
              help='Icon sizes to download (default: 64,128,256,512)')
@click.option('--output', '-o', default='icons',
              help='Output directory (default: icons)')
def search(term, store, country, limit, auto_download, sizes, output):
    """Search for apps and optionally download their icons"""
    
    # Validate inputs
    if not validate_store_name(store):
        click.echo("❌ Invalid store name", err=True)
        return
    
    if not validate_country_code(country):
        click.echo("❌ Invalid country code", err=True)
        return
    
    # Parse sizes
    try:
        size_list = [int(x.strip()) for x in sizes.split(',')]
        size_list = validate_icon_sizes(size_list)
        if not size_list:
            click.echo("❌ No valid icon sizes provided", err=True)
            return
    except ValueError:
        click.echo("❌ Invalid sizes format", err=True)
        return
    
    # Initialize CLI
    hunter = AppIconHunterCLI()
    hunter.output_dir = Path(output)
    
    # Search for apps
    click.echo(f"🔍 Searching for '{term}' in {store}...")
    apps = hunter.search_apps_combined(term, store, country, limit)
    
    if not apps:
        click.echo("❌ No apps found.")
        return
    
    # Display results
    hunter.display_apps_table(apps)
    
    if auto_download:
        # Auto download all
        click.echo(f"\n🚀 Auto-downloading all {len(apps)} apps...")
        hunter.download_selected_apps(apps, size_list)
    else:
        # Interactive selection
        selected_apps = hunter.get_user_selection(apps)
        if selected_apps:
            hunter.download_selected_apps(selected_apps, size_list)


@cli.command()
@click.argument('term')
@click.option('--store', '-s', default='both',
              type=click.Choice(['appstore', 'googleplay', 'both']),
              help='Store to search')
@click.option('--country', '-c', default='us',
              help='Country code')
@click.option('--limit', '-l', default=10, type=int,
              help='Maximum results')
def list(term, store, country, limit):
    """Search and list apps without downloading"""
    
    hunter = AppIconHunterCLI()
    apps = hunter.search_apps_combined(term, store, country, limit)
    
    if apps:
        hunter.display_apps_table(apps)
        click.echo(f"\nFound {len(apps)} apps total.")
    else:
        click.echo("❌ No apps found.")


@cli.command()
def interactive():
    """Run in interactive mode with prompts"""
    
    hunter = AppIconHunterCLI()
    
    click.echo("🎮 Welcome to App Store Icon Hunter Interactive Mode")
    click.echo("=" * 60)
    
    # Get search parameters
    term = click.prompt("Enter app name to search", type=str)
    
    store = click.prompt(
        "Store to search",
        type=click.Choice(['appstore', 'googleplay', 'both']),
        default='both'
    )
    
    country = click.prompt("Country code", default="us")
    limit = click.prompt("Maximum results per store", type=int, default=10)
    
    # Search
    apps = hunter.search_apps_combined(term, store, country, limit)
    
    if not apps:
        click.echo("❌ No apps found.")
        return
    
    # Display and select
    hunter.display_apps_table(apps)
    selected_apps = hunter.get_user_selection(apps)
    
    if selected_apps:
        sizes = hunter.get_icon_sizes()
        hunter.download_selected_apps(selected_apps, sizes)


if __name__ == "__main__":
    cli()
