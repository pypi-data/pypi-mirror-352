# EspressoNow ☕

Python CLI tool to find specialty coffee shops near your current location.

## Features

- 🌍 **Auto-location detection** - Automatically detects your current location
- 📍 **Custom location search** - Search near any address or coordinates
- ☕ **Specialty coffee focus** - Finds high-quality, specialty coffee shops
- 🎨 **Beautiful output** - Rich, colorful CLI interface with tables and progress bars
- 🔍 **Flexible search** - Customizable search radius and result limits
- 🗺️ **Google Places API integration** - Real-time coffee shop data from Google's database

## Installation

### From Source

```bash
git clone https://github.com/ethanqcarter/EspressoNow.git
cd EspressoNow
pip install -e .
```

### Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Configuration

**Required:** You'll need a Google Places API key to search for coffee shops:

1. Get an API key at [Google Places API](https://developers.google.com/places/web-service/get-api-key)
2. Set it as an environment variable:
   ```bash
   export GOOGLE_PLACES_API_KEY=your_key_here
   ```
3. Or create a `.env` file:
   ```bash
   cp env.example .env
   # Edit .env and add your API key
   ```

### Basic Usage

```bash
# Find coffee shops near your current location
espresso search

# Search with custom radius
espresso search --radius 5

# Search near a specific address
espresso search --location "123 Main St, San Francisco, CA"

# Search near coordinates
espresso search --location "37.7749,-122.4194"
```

## Commands

### `search` - Find coffee shops

```bash
espresso search [OPTIONS]

Options:
  -r, --radius FLOAT         Search radius (default: 3.0)
  -n, --max-results INTEGER  Maximum number of results (default: 10)
  -l, --location TEXT        Search location (address or "lat,lng")
  --api-key TEXT             Google Places API key
  --min-rating FLOAT         Minimum rating (e.g., 4.0 for >4 stars)
  --exclude-chains           Exclude chain coffee shops (Starbucks, Dunkin, etc.)
  --specialty-only           Show only specialty coffee (4+ stars, no chains) - DEFAULT
  --include-all              Include all coffee shops (disables specialty-only default)
  --miles                    Use miles instead of kilometers (DEFAULT)
  --km                       Use kilometers instead of miles
  --open                     Show only currently open coffee shops
  --export-yaml TEXT         Export results to YAML file (e.g., --export-yaml results.yaml)
  --help                     Show help message
```

### `config` - Show configuration

```bash
espresso config
```

Shows current configuration status and setup instructions.

## Examples

### Find coffee shops near current location
```bash
espresso search
```

### Search with 5-mile radius, max 20 results
```bash
espresso search --radius 5 --max-results 20
```

### Search near specific coordinates (San Francisco)
```bash
espresso search --location "37.7749,-122.4194"
```

### Search near coordinates (New York City)
```bash
espresso search --location "40.7128,-74.0060"
```

### Find only specialty coffee (4+ stars, no chains)
```bash
espresso search --specialty-only
```

### Show only currently open coffee shops
```bash
espresso search --open
```

### Exclude chain coffee shops
```bash
espresso search --exclude-chains
```

### Use kilometers instead of miles
```bash
espresso search --km
```

### Use specific API key
```bash
espresso search --api-key your_google_places_api_key
```

## Example Output

Here's what you'll see when searching for specialty coffee in San Francisco:

```bash
$ espresso search --location "37.7749,-122.4194" --radius 2 --max-results 5
Using provided coordinates: 37.7749, -122.4194
⠋ Searching for coffee shops...

╭─────────────────────────────────────────────────────── Search Info ───────────────────────────────────────────────────────╮
│ 📍 Search Location: 37.7749, -122.4194                                                                                    │
│ 🔍 Search Radius: 2.0mi                                                                                                   │
│ 📊 Results Found: 38                                                                                                      │
│ 🔧 Filters: ⭐ Min Rating: 4.0 | 🚫 Chains Excluded | ☕ Specialty Only (Default)                                         │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

                            ☕ Specialty Coffee Shops Near You                             
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Name                ┃ Google Maps     ┃      Rating      ┃ Today's Hours     ┃ Distance ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Social Cafe         │ 📍 View on Maps │ ⭐⭐⭐⭐⭐ (5.0) │ 7:30 AM – 3:00 PM │    0.9mi │
│ Third Wheel Coffee  │ 📍 View on Maps │ ⭐⭐⭐⭐⭐ (5.0) │ 7:00 AM – 3:00 PM │    0.9mi │
│ Cable Car CoffeeSF  │ 📍 View on Maps │  ⭐⭐⭐⭐ (4.9)  │ 4:30 AM – 4:30 PM │    0.9mi │
│ Cafe Suspiro        │ 📍 View on Maps │  ⭐⭐⭐⭐ (4.8)  │ 8:00 AM – 3:00 PM │    0.5mi │
│ Unexpected Era Café │ 📍 View on Maps │  ⭐⭐⭐⭐ (4.8)  │ 7:00 AM – 3:00 PM │    0.5mi │
└─────────────────────┴─────────────────┴──────────────────┴───────────────────┴──────────┘
```

EspressoNow displays results in a beautiful table format showing:

- ☕ **Name** - Coffee shop name
- 📍 **Google Maps** - Link to view location on Google Maps
- ⭐ **Rating** - Star rating (1-5) with visual stars
- 🕐 **Today's Hours** - Current day's opening hours with color coding (red=closed, green=open)
- 📏 **Distance** - Distance from search location in miles or kilometers

## API Integration

### Google Places API (New) with Pagination

EspressoNow uses the latest Google Places API (New) with intelligent pagination to find comprehensive coffee shop results:
- **Text Search API** with location bias for better coverage
- **Automatic pagination** using `nextPageToken` to get up to 60 results
- **Deduplication** to ensure no duplicate coffee shops
- **Real-time data** from Google's comprehensive database
- **Detailed place information** including ratings, prices, hours, and contact details
- **Supports up to 50km search radius**

**Note:** A Google Places API key is required for the application to function.

## Development

### Project Structure

```
espressonow/
├── __init__.py          # Package initialization
├── cli.py              # Command-line interface
├── core.py             # Core coffee shop finding logic
├── location.py         # Location detection and services
└── models.py           # Data models (Pydantic)
```

### Running Tests

```bash
# Install in development mode
pip install -e .

# Test the CLI
espresso search --help
espresso config

# Test with API key
export GOOGLE_PLACES_API_KEY=your_key_here
espresso search --location "San Francisco, CA"
```

## Changelog


### v0.4.3 (Latest)
- **🔧 Packaging Fix**: Fixed PyPI installation issue by correcting license field format in pyproject.toml

### v0.4.2
- **🎨 UI Enhancement**: Improved table formatting with fixed column width for better coffee shop name display

### v0.4.1
- **📚 Documentation**: Updated README with real San Francisco output examples
- **🧹 Cleanup**: Removed YAML export documentation section for cleaner focus
- **✨ Better Examples**: Added actual CLI output showing beautiful table formatting
- **🎯 Improved UX**: Enhanced documentation with real-world usage examples

### v0.4.0
- **🚀 Enhanced Packaging**: Added modern pyproject.toml configuration for better packaging standards
- **📦 Build System**: Enhanced build system with comprehensive dependency management
- **📊 YAML Export**: Added YAML export functionality for search results
- **🕐 Open Filter**: Improved CLI with --open flag to filter currently open coffee shops
- **📏 Distance Units**: Enhanced distance filtering with proper miles/km unit support
- **🔄 API Upgrade**: Upgraded to Google Places Text Search API with intelligent pagination
- **🎯 Better UX**: Better error handling and user experience improvements

### v0.3.0
- **🚀 Major Performance Improvement**: Implemented intelligent pagination using Google Places Text Search API
- **📈 10x Better Coverage**: Now finds 40+ coffee shops in 2km radius vs 3-4 previously
- **🔄 Comprehensive Results**: Uses `nextPageToken` to get up to 60 results with automatic deduplication
- **✅ Consistent Results**: Smaller radius results are always included in larger radius searches
- **⚡ Optimized API Usage**: Respectful delays between paginated requests
- **🎯 Better Search Strategy**: Switched from Nearby Search to Text Search API for superior coverage

### v0.2.0
- Google Places API (New) integration
- Real-time coffee shop data
- Beautiful CLI interface with Rich library
- Auto-location detection
- Custom location search
- Chain coffee shop filtering

### v0.1.0
- Initial release
- Basic coffee shop search functionality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/ethanqcarter/EspressoNow/issues)

---

Made with ☕ and ❤️ by coffee enthusiasts, for coffee enthusiasts.
