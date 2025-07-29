from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from secure_bite.authentication import CookieJWTAuthentication
from secure_bite.utils import clear_cookie
from secure_bite.utils import get_jwt_cookie_settings, get_simple_jwt_settings

cookie_settings = get_jwt_cookie_settings()
jwt_settings = get_simple_jwt_settings()

class AuthenticationViewset(ViewSet):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = cookie_settings["USER_SERIALIZER"]

    @action(methods=["POST"], detail=False)
    def login(self, request, *args, **kwargs):
        """Authenticates the user using the dynamic username field and password and sets JWT tokens in cookies."""
        if request.user and request.user.is_authenticated:
            return Response({"message": "Already authenticated"}, status=status.HTTP_200_OK)
        # Get the custom user model dynamically
        User = get_user_model()

        # Get the USERNAME_FIELD from the user model (it could be 'username', 'email', or another custom field)
        username_field = User.USERNAME_FIELD
        # Get identifier (username, email or phone) and password from request
        identifier = request.data.get(username_field)  # Expecting "username_or_email_or_phone" as the input field
        password = request.data.get("password")
        
        if not identifier or not password:
            return Response({"error": f"Both '{username_field}' and 'password' are required."}, status=400)
        
        # Create a dictionary to authenticate with the correct username field
        credentials = {username_field: identifier, 'password': password}
        
        # Attempt authentication with the provided username field and password
        user = authenticate(**credentials)
        
        # If user is not found or password doesn't match
        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Prepare the response
        response = Response({"message": "Login successful"})

        # Set the access token in a cookie
        response.set_cookie(
            cookie_settings["AUTH_COOKIE"],
            access_token,
            max_age=jwt_settings["ACCESS_TOKEN_LIFETIME"],
            httponly=True,
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
        )

        # Set the refresh token in a cookie
        response.set_cookie(
            "refreshToken",
            refresh_token,
            max_age=jwt_settings["REFRESH_TOKEN_LIFETIME"],
            httponly=True,
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
        )

        return response
    
    @action(methods=["POST"], detail=False)
    def logout(self, request, *args, **kwargs):
        """Clears JWT cookies on logout."""
        try:
            refresh_token = request.COOKIES.get("refreshToken")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except TokenError:
            pass

        response = Response({"message": "Logged out"}, status=status.HTTP_200_OK)
        clear_cookie(response, name=cookie_settings["AUTH_COOKIE"])
        clear_cookie(response, name="refreshToken")
        return response

    @action(methods=["GET"], detail=False)
    def me(self, request, *args, **kwargs):
        """Get the current user"""
        user = request.user
        # Serialize the user data using your custom serializer (without including 'id')
        serializer = self.serializer_class(user)

        # Pop the tokens from the serialized data to avoid including them in the response
        data = serializer.data.copy()
        data.pop('access', None)
        data.pop('refresh', None)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False)
    def auth_check(self, request, *args, **kwargs):
        """
        Protected endpoint requiring authentication.
        """
        return Response({"message": "You are authenticated"}, status=status.HTTP_200_OK)
    

    def get_permissions(self):
        if self.action == "login":
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()
    

    

