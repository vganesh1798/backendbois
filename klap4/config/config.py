from datetime import timedelta

# Spotify IDs are purposefully broken, as they will be environmental variables in future
def config():
    return {
        "clientOrigin": "http://localhost:8080",
        "accessExpiration": timedelta(hours=6),
        "refreshExpiration": timedelta(hours=6),
        "spotifyClient": "broken",
        "spotifySecret": "broken"
        }
        