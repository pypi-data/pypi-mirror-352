from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username="testUser", password="Testing321")
        self.credentials = {
            "username": "testUser",
            "password": "Testing321"
        }

    def test_login_sets_cookies(self):
        url = reverse("secure_bite:auth-login")  # ViewSet action
        response = self.client.post(
            url,
            data=self.credentials,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("authToken", response.cookies)
        self.assertIn("refreshToken", response.cookies)

        def test_logout_clears_cookies(self):
            # Login first
            self.client.post(reverse("secure_bite:login"), data=self.credentials, content_type="application/json")
            
            # Logout request
            response = self.client.post(reverse("secure_bite:logout"))
            
            # Check if the cookies are cleared (i.e., marked for deletion)
            self.assertIn("authToken", response.cookies)
            self.assertIn("refreshToken", response.cookies)

            self.assertTrue(response.cookies["authToken"]["max-age"] == 0)
            self.assertTrue(response.cookies["refreshToken"]["max-age"] == 0)

    def test_protected_route_requires_authentication(self):
        url = reverse("secure_bite:auth-auth-check")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_protected_route_with_authentication(self):
        # Login
        login_url = reverse("secure_bite:auth-login")
        login_response = self.client.post(
            login_url,
            data=self.credentials,
            content_type="application/json"
        )
        self.assertEqual(login_response.status_code, 200)

        # Inject cookie manually
        self.client.cookies["authToken"] = login_response.cookies["authToken"].value

        # Access protected route
        protected_url = reverse("secure_bite:auth-auth-check")
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, 200)
