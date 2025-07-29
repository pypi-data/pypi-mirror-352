from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from unittest.mock import patch, MagicMock
from secure_bite.middleware import RefreshTokenMiddleware
from django.contrib.auth import get_user_model
from django.conf import settings
from secure_bite.utils import get_jwt_cookie_settings

cookie_settings = get_jwt_cookie_settings()
User = get_user_model()

class RefreshTokenMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.middleware = RefreshTokenMiddleware(lambda req: HttpResponse())

    @patch('secure_bite.middleware.RefreshToken')  # <-- patch the class, not for_user
    def test_process_request_valid_refresh_token(self, mock_refresh_token_class):
        # Setup fake refresh token
        mock_refresh_token = MagicMock()
        mock_refresh_token.access_token = 'mocked-access-token'
        mock_refresh_token_class.return_value = mock_refresh_token

        request = self.factory.get('/')
        request.COOKIES['refreshToken'] = 'fake-refresh-token'

        response = self.middleware(request)
        response = self.middleware.process_response(request, response)

        auth_cookie_name = cookie_settings["AUTH_COOKIE"]
        self.assertIn(auth_cookie_name, response.cookies)
        self.assertEqual(response.cookies[auth_cookie_name].value, 'mocked-access-token')

    @patch('secure_bite.middleware.RefreshToken')
    def test_process_request_no_refresh_token(self, mock_refresh_token_class):
        request = self.factory.get('/')
        response = self.middleware(request)
        response = self.middleware.process_response(request, response)

        auth_cookie_name = cookie_settings["AUTH_COOKIE"]
        self.assertNotIn(auth_cookie_name, response.cookies)
