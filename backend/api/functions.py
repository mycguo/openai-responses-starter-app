from fastapi import APIRouter, Query
import httpx

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

