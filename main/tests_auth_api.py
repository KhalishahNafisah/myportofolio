from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from main.models import Project


@override_settings(CORS_ALLOW_ALL_ORIGINS=True)
class TokenAuthenticationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model()
        cls.password = "integration-test-password"
        cls.owner = users.objects.create_superuser(
            username="token-owner", email="owner@example.com", password=cls.password,
        )
        cls.visitor = users.objects.create_user(
            username="token-visitor", password=cls.password,
        )

    def setUp(self):
        self.token_url = reverse("api:api_token_auth")
        self.logout_url = reverse("api:api_logout")
        self.projects_url = reverse("api:project-list")
        self.payload = {
            "title": "Mobile portfolio",
            "description": "Created through token authentication.",
            "category": "web",
            "year": 2026,
            "project_url": "https://example.com",
            "project_image_url": "",
        }

    def login_token(self, user=None):
        response = self.client.post(
            self.token_url,
            {"username": (user or self.owner).username, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        return response.data["token"]

    def test_owner_can_create_project_using_real_token_header(self):
        token = self.login_token()
        response = self.client.post(
            self.projects_url, self.payload, format="json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())
        self.assertEqual(response.data["category"], "web")
        self.assertEqual(response.data["year"], 2026)

    def test_wrong_credentials_do_not_issue_token(self):
        response = self.client.post(
            self.token_url,
            {"username": self.owner.username, "password": "incorrect"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Token.objects.exists())

    def test_projects_remain_public_but_anonymous_writes_are_rejected(self):
        self.assertEqual(self.client.get(self.projects_url).status_code, 200)
        response = self.client.post(self.projects_url, self.payload, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Project.objects.count(), 0)

    def test_visitor_token_does_not_bypass_owner_permission(self):
        token = self.login_token(self.visitor)
        response = self.client.post(
            self.projects_url, self.payload, format="json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Project.objects.count(), 0)

    def test_logout_revokes_token_and_login_issues_a_new_token(self):
        old_token = self.login_token()
        response = self.client.post(
            self.logout_url, HTTP_AUTHORIZATION=f"Token {old_token}",
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Token.objects.filter(key=old_token).exists())
        rejected = self.client.post(
            self.projects_url, self.payload, format="json",
            HTTP_AUTHORIZATION=f"Token {old_token}",
        )
        self.assertEqual(rejected.status_code, 401)
        self.assertNotEqual(self.login_token(), old_token)

    def test_logout_requires_authentication(self):
        self.assertEqual(self.client.post(self.logout_url).status_code, 401)

    def test_cors_preflight_allows_mobile_web_headers(self):
        response = self.client.options(
            self.projects_url,
            HTTP_ORIGIN="http://localhost:5000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,content-type",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
        self.assertIn("authorization", response.headers["Access-Control-Allow-Headers"])

    @override_settings(ALLOWED_HOSTS=["localhost", "127.0.0.1", "10.0.2.2"])
    def test_android_emulator_host_is_accepted(self):
        response = self.client.get(self.projects_url, HTTP_HOST="10.0.2.2:8000")
        self.assertEqual(response.status_code, 200)
