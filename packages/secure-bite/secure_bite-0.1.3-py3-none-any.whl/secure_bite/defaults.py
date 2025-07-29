from datetime import timedelta

# These are only defaults. The main project settings can override them.

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

JWT_AUTH_COOKIE_SETTINGS = {
    "AUTH_COOKIE": "authToken",                 # Access token cookie name
    "REFRESH_COOKIE": "refreshToken",           # Refresh token cookie name
    "AUTH_COOKIE_HTTP_ONLY": True,              # Prevents JavaScript access
    "AUTH_COOKIE_SECURE": False,                 # Use True in production (HTTPS)
    "AUTH_COOKIE_SAMESITE": "Lax",              # Or 'Strict' or 'None'
    "AUTH_COOKIE_PATH": "/",                    # Path scope of the cookie
    "USER_SERIALIZER": "secure_bite.serializers.UserSerializer"
}
