# How to Use the scrape_website Function

The `scrape_website` function allows the assistant to scrape websites with full JavaScript rendering support using Playwright.

## Prerequisites

1. **Enable Functions in the UI:**
   - Open the Streamlit app
   - In the sidebar, expand "🔧 Functions"
   - Check "Enable Functions"
   - The function will be automatically available to the assistant

2. **Install Playwright (if not already installed):**
   ```bash
   pip install playwright
   playwright install chromium
   ```

## How to Trigger

The assistant will automatically use `scrape_website` when you ask it to access websites that require JavaScript rendering. Here are some example prompts:

### Direct Requests:
- "Scrape https://example.com"
- "Get the content from https://spa-site.com"
- "Can you scrape https://example.com with JavaScript rendering?"

### Context-Based Requests:
- "What's on https://example.com?"
- "Check what's displayed on https://spa-site.com"
- "Read the content from https://example.com"

### For JavaScript-Heavy Sites:
- "Scrape https://example.com and wait for JavaScript to load"
- "Get content from https://spa-site.com with JS rendering enabled"

## Function Parameters

The assistant can use these parameters:

- **`url`** (required): The website URL to scrape
- **`wait_for_js`** (optional): Set to `true` for JavaScript-heavy sites
- **`wait_timeout`** (optional): Timeout in seconds (default: 30)

## Example Usage

1. **Simple scrape:**
   ```
   User: "Scrape https://example.com"
   ```
   Assistant will call: `scrape_website(url="https://example.com")`

2. **With JavaScript rendering:**
   ```
   User: "Get content from https://spa-site.com with JavaScript"
   ```
   Assistant will call: `scrape_website(url="https://spa-site.com", wait_for_js=True)`

3. **With custom timeout:**
   ```
   User: "Scrape https://slow-site.com, it takes a while to load"
   ```
   Assistant will call: `scrape_website(url="https://slow-site.com", wait_timeout=60)`

## How It Works

1. You send a message requesting website content
2. The assistant recognizes it needs to scrape a website
3. It automatically calls the `scrape_website` function
4. The function uses Playwright to render the page (including JavaScript)
5. The rendered content is returned to the assistant
6. The assistant uses that content to answer your question

## Troubleshooting

- **If Playwright is not installed:** The function will fall back to basic HTTP requests (no JavaScript rendering)
- **For slow sites:** Ask the assistant to increase the timeout
- **For JavaScript-heavy sites:** Explicitly mention "with JavaScript" or "wait for JS"

## Note

The `scrape_website` function is more powerful than the basic `web_search` tool because it can:
- Execute JavaScript
- Render single-page applications (SPAs)
- Access dynamically loaded content
- Wait for content to load

Use it when you need content from modern, JavaScript-heavy websites!

