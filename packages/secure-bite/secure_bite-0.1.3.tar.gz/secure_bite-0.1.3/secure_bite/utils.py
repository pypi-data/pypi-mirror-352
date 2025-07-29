from django.conf import settings
from secure_bite import defaults

def get_jwt_cookie_settings():
    """
    Returns the JWT auth cookie settings, falling back to defaults if not overridden.
    """
    user_settings = getattr(settings, "JWT_AUTH_COOKIE_SETTINGS", {})
    final = defaults.JWT_AUTH_COOKIE_SETTINGS.copy()
    final.update(user_settings)
    return final

def get_simple_jwt_settings():
    """
    Returns SIMPLE_JWT settings, falling back to defaults if not overridden.
    """
    user_settings = getattr(settings, "SIMPLE_JWT", {})
    final = defaults.SIMPLE_JWT.copy()
    final.update(user_settings)
    return final

cookie_settings = get_jwt_cookie_settings()
jwt_settings = get_simple_jwt_settings()

def clear_cookie(response, name, path="/",domain=None):
    response.set_cookie(
        name,
        max_age=0,
        expires="Thu, 01 Jan 1970 00:00:00 GMT",
        path=path,
        domain=domain,
        secure=cookie_settings["AUTH_COOKIE_SECURE"],
        httponly=cookie_settings["AUTH_COOKIE_HTTP_ONLY"],
        samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
    )