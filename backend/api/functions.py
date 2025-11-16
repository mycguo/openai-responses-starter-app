from fastapi import APIRouter, Query
import httpx
from typing import Optional

router = APIRouter()


@router.get("/get_weather")
async def get_weather(
    location: str = Query(...),
    unit: str = Query("celsius"),
):
    """Get weather for a location"""
    try:
        # 1. Get coordinates for the city
        async with httpx.AsyncClient() as client:
            geo_res = await client.get(
                f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
            )
            geo_data = geo_res.json()
        
        if not geo_data:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content={"error": "Invalid location"},
                status_code=404
            )
        
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        
        # 2. Fetch weather data from Open-Meteo
        async with httpx.AsyncClient() as client:
            weather_res = await client.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m&temperature_unit={unit}"
            )
            weather_res.raise_for_status()
            weather = weather_res.json()
        
        # 3. Get current UTC time in ISO format
        from datetime import datetime
        now = datetime.utcnow()
        current_hour_iso = now.strftime("%Y-%m-%dT%H:00")
        
        # 4. Get current temperature
        index = weather["hourly"]["time"].index(current_hour_iso) if current_hour_iso in weather["hourly"]["time"] else -1
        current_temperature = (
            weather["hourly"]["temperature_2m"][index] if index != -1 else None
        )
        
        if current_temperature is None:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content={"error": "Temperature data unavailable"},
                status_code=500
            )
        
        return {"temperature": current_temperature}
    except Exception as e:
        print(f"Error getting weather: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"error": "Error getting weather"},
            status_code=500
        )


@router.get("/get_joke")
async def get_joke():
    """Get a programming joke"""
    try:
        async with httpx.AsyncClient() as client:
            joke_res = await client.get("https://v2.jokeapi.dev/joke/Programming")
            joke_res.raise_for_status()
            joke_data = joke_res.json()
        
        # Format joke response based on its type
        joke = (
            f"{joke_data['setup']} - {joke_data['delivery']}"
            if joke_data.get("type") == "twopart"
            else joke_data.get("joke", "")
        )
        
        return {"joke": joke}
    except Exception as e:
        print(f"Error fetching joke: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"error": "Could not fetch joke"},
            status_code=500
        )


@router.get("/scrape_website")
async def scrape_website(
    url: str = Query(..., description="URL to scrape"),
    wait_for_js: Optional[bool] = Query(None, description="Wait for JavaScript to execute"),
    wait_timeout: Optional[int] = Query(None, description="Timeout in seconds for page load"),
):
    """
    Scrape a website with optional JavaScript rendering using Playwright.
    This function can render JavaScript-heavy websites that the basic web_search tool cannot.
    """
    try:
        # Try to import playwright
        try:
            from playwright.async_api import async_playwright
            PLAYWRIGHT_AVAILABLE = True
        except ImportError:
            PLAYWRIGHT_AVAILABLE = False
        
        if not PLAYWRIGHT_AVAILABLE:
            # Fallback to basic HTTP request if Playwright not available
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                return {
                    "url": url,
                    "content": response.text[:50000],  # Limit content size
                    "note": "Playwright not installed. Install with: pip install playwright && playwright install",
                    "rendered": False,
                }
        
        # Use Playwright for JavaScript rendering
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            try:
                # Use defaults if not provided
                should_wait_for_js = wait_for_js if wait_for_js is not None else False
                timeout_seconds = wait_timeout if wait_timeout is not None else 30
                
                # Navigate to the page
                await page.goto(url, wait_until="networkidle" if should_wait_for_js else "domcontentloaded", timeout=timeout_seconds * 1000)
                
                # Wait for JavaScript if requested
                if should_wait_for_js:
                    # Wait a bit for dynamic content to load
                    await page.wait_for_timeout(2000)
                
                # Get the rendered content
                content = await page.content()
                
                # Also get visible text (cleaner for reading)
                visible_text = await page.evaluate("() => document.body.innerText")
                
                await browser.close()
                
                return {
                    "url": url,
                    "content": content[:100000],  # Limit HTML content size
                    "text": visible_text[:50000],  # Limit text content size
                    "rendered": True,
                    "status": "success",
                }
            except Exception as e:
                await browser.close()
                raise e
                
    except Exception as e:
        print(f"Error scraping website {url}: {e}")
        import traceback
        traceback.print_exc()
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={
                "error": str(e),
                "url": url,
                "status": "error"
            },
            status_code=500
        )

