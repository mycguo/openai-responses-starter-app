def get_google_connector_tools(access_token: str) -> list:
    """Get Google connector tools configuration"""
    if not access_token:
        return []
    return [
        {
            "type": "mcp",
            "server_label": "GoogleCalendar",
            "server_description": "Search the user's calendar and read calendar events",
            "connector_id": "connector_googlecalendar",
            "authorization": access_token,
            "require_approval": "never",  # change this to "always" if you want to require approval
        },
        {
            "type": "mcp",
            "server_label": "GoogleMail",
            "server_description": "Search the user's email inbox and read emails",
            "connector_id": "connector_gmail",
            "authorization": access_token,
            "require_approval": "never",  # change this to "always" if you want to require approval
        },
    ]

