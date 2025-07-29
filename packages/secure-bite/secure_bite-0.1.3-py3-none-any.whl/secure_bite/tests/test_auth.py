from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed
from secure_bite.authentication import CookieJWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

class CookieJWTAuthenticationTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.authenticator = CookieJWTAuthentication()
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_authenticate_valid_token(self):
        token = AccessToken.for_user(self.user)
        request = self.factory.get('/')
        request.COOKIES['authToken'] = str(token)  # fixed cookie name

        user, validated_token = self.authenticator.authenticate(request)
        self.assertEqual(user, self.user)
        self.assertEqual(str(validated_token), str(token))

    def test_authenticate_no_token(self):
        request = self.factory.get('/')
        result = self.authenticator.authenticate(request)
        self.assertIsNone(result)

    def test_authenticate_invalid_token(self):
        request = self.factory.get('/')
        request.COOKIES['authToken'] = 'invalidtoken'  # fixed cookie name

        with self.assertRaises(AuthenticationFailed):
            self.authenticator.authenticate(request)
