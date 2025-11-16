# List of tools available to the assistant
# More information on function calling: https://platform.openai.com/docs/guides/function-calling

tools_list = [
    {
        "name": "get_weather",
        "description": "Get the weather for a given location",
        "parameters": {
            "location": {
                "type": "string",
                "description": "Location to get weather for",
            },
            "unit": {
                "type": "string",
                "description": "Unit to get weather in",
                "enum": ["celsius", "fahrenheit"],
            },
        },
    },
    {
        "name": "get_joke",
        "description": "Get a programming joke",
        "parameters": {},
    },
    {
        "name": "scrape_website",
        "description": "Scrape a website with full JavaScript rendering support. Use this when you need to access content that requires JavaScript to load, such as dynamic web pages, single-page applications (SPAs), or sites with client-side rendering. This is more powerful than the basic web_search tool.",
        "parameters": {
            "url": {
                "type": "string",
                "description": "The full URL of the website to scrape (e.g., https://example.com)",
            },
            "wait_for_js": {
                "type": "boolean",
                "description": "Whether to wait for JavaScript to execute and render content. Set to true for JavaScript-heavy sites. Defaults to false if not specified.",
            },
            "wait_timeout": {
                "type": "integer",
                "description": "Timeout in seconds for page load. Defaults to 30 seconds if not specified.",
            },
        },
    },
]

