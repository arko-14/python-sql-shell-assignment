# Q1 — Python Web Scraping

A robust web scraper for extracting product information from mdcomputers.in with pagination support and comprehensive price extraction.

## Overview

This scraper searches for products on mdcomputers.in, handles pagination automatically, and extracts detailed product information including current and old prices.

## Features

- **Search-based scraping**: Accepts any search term as input
- **Automatic pagination**: Follows "next page" links automatically
- **Price extraction**: Extracts both current and old prices from product pages
- **Multiple output formats**: Supports JSON, JSONL, and CSV
- **Robust parsing**: Multiple fallback strategies for price detection
- **Polite scraping**: Built-in rate limiting to avoid overwhelming the server
- **Debug mode**: Saves HTML for troubleshooting when products aren't found

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Dependencies:
- `requests` - HTTP library for making web requests
- `beautifulsoup4` - HTML parsing library

## Usage

Basic usage:

```bash
python scraper.py "external harddrive"
```

With options:

```bash
# Output as JSON
python scraper.py "laptop" --format json

# Output as CSV
python scraper.py "graphics card" --format csv

# Enable debug mode
python scraper.py "ssd" --debug

# Custom sleep interval between pages (default: 0.2s)
python scraper.py "monitor" --sleep 0.5
```

## Command Line Arguments

- `term` (required): Search term to query (e.g., "external harddrive")
- `--format`: Output format - `jsonl` (default), `json`, or `csv`
- `--sleep`: Sleep duration between page requests in seconds (default: 0.2)
- `--debug`: Enable debug mode to save HTML and print diagnostic info

## Output Format

Each product contains:
- `name`: Product name/title
- `url`: Direct link to product page
- `price_current`: Current price (if available)
- `price_old`: Original/old price (if available)

Example JSONL output:

```json
{"name": "Seagate Backup Plus 2TB External Hard Drive", "url": "https://mdcomputers.in/...", "price_current": "5999", "price_old": "7999"}
```

## Implementation Details

### Price Extraction Strategy

The scraper uses multiple fallback methods to extract prices:

1. **CSS selectors**: `.price-new` and `.price-old` classes
2. **Visible price blocks**: Common price container classes
3. **JSON-LD structured data**: Schema.org Offer markup
4. **Meta tags**: `product:price:amount` and `itemprop="price"`

### Price Normalization

Automatically detects and corrects reversed prices (when old price appears before current price in HTML).

### Pagination

Automatically follows pagination by:
- Looking for `>` link in `.pagination` elements
- Fallback to any `>` link on the page
- Tracks visited pages to avoid loops

## Notes

- The scraper is polite with 0.1s delay between product requests and configurable delay between pages
- Duplicate products (same URL) are automatically filtered
- Debug mode saves the last searched page as `debug_mdcomputers.html` for inspection
- All prices are extracted in Indian Rupees (₹)

## Example

```bash
python scraper.py "external harddrive" --format json > products.json
```

This will search for "external harddrive", scrape all pages, and save results to `products.json`.
