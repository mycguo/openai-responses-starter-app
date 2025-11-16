# Playwright Setup for JavaScript Rendering

The `scrape_website` function uses Playwright to render JavaScript-heavy websites. This allows the assistant to access content that requires JavaScript execution, which the basic `web_search` tool cannot handle.

## Installation

1. **Install Playwright Python package:**
   ```bash
   pip install playwright
   ```
   
   Or if using a virtual environment:
   ```bash
   .venv/bin/pip install playwright
   ```

2. **Install Playwright browsers:**
   
   **Important:** Install browsers using the same Python environment where Playwright is installed.
   
   If using a virtual environment:
   ```bash
   .venv/bin/python -m playwright install chromium
   ```
   
   If using system Python:
   ```bash
   python -m playwright install chromium
   ```
   
   Or install all browsers:
   ```bash
   python -m playwright install
   ```
   
   **Note:** If your backend runs in a virtual environment (`.venv`), make sure to install browsers in that same environment!

## Usage

The `scrape_website` function is automatically available when Functions are enabled in the Tools Panel. The assistant can use it to:

- Scrape JavaScript-rendered websites
- Access single-page applications (SPAs)
- Get content from sites with client-side rendering
- Wait for dynamic content to load

## Function Parameters

- `url` (required): The full URL to scrape
- `wait_for_js` (optional, default: false): Whether to wait for JavaScript execution
- `wait_timeout` (optional, default: 30): Timeout in seconds

## Example Usage

The assistant can call this function like:
- "Scrape https://example.com with JavaScript rendering"
- "Get the content from https://spa-site.com, wait for JS to load"

## Notes

- Playwright requires browser binaries to be installed
- The function falls back to basic HTTP requests if Playwright is not available
- Content is limited to prevent excessive memory usage
- Timeouts are configurable for slow-loading sites

