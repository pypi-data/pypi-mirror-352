from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError 
from django.conf import settings
from django.utils.timezone import now
from django.http import JsonResponse
from secure_bite.utils import clear_cookie, get_jwt_cookie_settings, get_simple_jwt_settings

cookie_settings = get_jwt_cookie_settings()
jwt_settings = get_simple_jwt_settings()

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that retrieves tokens from HTTP-only cookies
    and handles token rotation.
    """

    def authenticate(self, request):
        access_token = request.COOKIES.get("authToken")
        refresh_token = request.COOKIES.get("refreshToken")

        if not access_token:
            return None  # No authentication if access token is not available.

        try:
            # Try to verify the access token
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token
        except TokenError:
            if not refresh_token:
                raise AuthenticationFailed("Authentication expired. Please log in again.")

            # If access token is expired, try to refresh using the refresh token
            try:
                new_access_token, new_refresh_token = self.refresh_tokens(refresh_token)
                response = JsonResponse({"message": "Tokens refreshed"}, status=200)
                self.set_access_cookie(response, new_access_token)
                self.set_refresh_cookie(response, new_refresh_token)
                return self.get_user(AccessToken(new_access_token)), new_access_token
            except AuthenticationFailed:
                raise AuthenticationFailed("Session expired. Please log in again.")

    def refresh_tokens(self, refresh_token):
        """Attempt to refresh both the access token and the refresh token."""
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            new_refresh_token = str(refresh)
            return new_access_token, new_refresh_token
        except TokenError:
            raise AuthenticationFailed("Invalid refresh token. Please log in again.")

    def set_access_cookie(self, response, access_token):
        """Set the refreshed access token in the response cookies."""
        response.set_cookie(
            cookie_settings["AUTH_COOKIE"],
            access_token,
            max_age=jwt_settings["ACCESS_TOKEN_LIFETIME"],
            httponly=True,
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
        )

    def set_refresh_cookie(self, response, refresh_token):
        """Set the new refresh token in the response cookies."""
        response.set_cookie(
            "refreshToken",
            refresh_token,
            max_age=jwt_settings["REFRESH_TOKEN_LIFETIME"],
            httponly=True,
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
        )

    def clear_auth_cookies(self, response):
        """Clear authentication cookies."""
        clear_cookie(response=response,name=cookie_settings["AUTH_COOKIE"])
        clear_cookie(response=response,name="refreshToken")