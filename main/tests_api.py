import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.password = "Temporary-test-password-731!"
        self.owner = User.objects.create_superuser(
            username="api-owner",
            email="owner@example.com",
            password=self.password,
        )
        self.visitor = User.objects.create_user(
            username="api-visitor",
            password=self.password,
        )
        self.project = Project.objects.create(
            title="Portfolio",
            description="My website",
            category="web",
            year=2026,
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.pk])
        self.star_url = reverse("api:project-star", args=[self.project.pk])
        self.payload = {
            "title": "New project",
            "description": "A useful application",
            "category": "web",
            "year": 2026,
            "project_url": "https://example.com/",
            "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        self.project.starred_by.add(self.visitor)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        project = response.data[0]
        self.assertEqual(project["id"], str(self.project.pk))
        self.assertEqual(project["title"], "Portfolio")
        self.assertEqual(project["year"], 2026)
        self.assertEqual(project["category_display"], "Web Development")
        self.assertEqual(project["star_count"], 1)
        self.assertFalse(project["is_starred"])
        for field in (
            "pk", "fields", "starred_by", "starred_by_names", "password", "email",
        ):
            with self.subTest(field=field):
                self.assertNotIn(field, project)
        self.assertNotContains(response, self.visitor.username)
        self.assertNotContains(response, self.owner.email)

        detail = self.client.get(self.detail_url)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data, project)

        for url in (self.list_url, self.detail_url):
            with self.subTest(method="HEAD", url=url):
                head = self.client.head(url)
                self.assertEqual(head.status_code, 200)
                self.assertEqual(head.content, b"")
            with self.subTest(method="OPTIONS", url=url):
                self.assertEqual(self.client.options(url).status_code, 200)
        self.assertEqual(self.project.starred_by.count(), 1)

    def test_search_and_empty_results(self):
        other = Project.objects.create(
            title="Marketing campaign",
            description="Another project",
            category="marketing",
            year=2025,
        )

        response = self.client.get(self.list_url, {"title": "  PORT  "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [project["id"] for project in response.data],
            [str(self.project.pk)],
        )

        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

        response = self.client.get(self.list_url, {"title": "   "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [project["id"] for project in response.data],
            [str(self.project.pk), str(other.pk)],
        )

    def test_missing_project(self):
        missing_id = uuid.uuid4()
        detail_url = reverse("api:project-detail", args=[missing_id])
        star_url = reverse("api:project-star", args=[missing_id])

        self.assertEqual(self.client.get(detail_url).status_code, 404)

        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.patch(detail_url, {"title": "Changed"}, format="json").status_code,
            404,
        )
        self.assertEqual(self.client.delete(detail_url).status_code, 404)
        self.assertEqual(self.client.post(star_url).status_code, 404)
        self.assertEqual(Project.objects.count(), 1)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            for method, url, payload in (
                ("post", self.list_url, self.payload),
                ("patch", self.detail_url, {"title": "Changed"}),
                ("put", self.detail_url, self.payload),
                ("delete", self.detail_url, None),
            ):
                with self.subTest(user=user, method=method):
                    response = getattr(self.client, method)(
                        url, payload, format="json",
                    )
                    self.assertEqual(response.status_code, 403)

        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")
        self.assertEqual(self.project.description, "My website")
        self.assertEqual(self.project.year, 2026)

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "title": "  <b>New project</b>  ",
                "description": " <p>A useful application</p> ",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.objects.count(), 2)
        saved = Project.objects.get(pk=response.data["id"])
        self.assertEqual(saved.title, "New project")
        self.assertEqual(saved.description, "A useful application")
        self.assertEqual(saved.category, "web")
        self.assertEqual(saved.year, 2026)
        self.assertEqual(saved.project_url, "https://example.com/")
        self.assertEqual(saved.starred_by.count(), 0)

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)

        for changes, field in (
            ({"title": ""}, "title"),
            ({"title": "   "}, "title"),
            ({"title": "x" * 256}, "title"),
            ({"title": '<img src=x onerror="alert(1)">'}, "title"),
            ({"description": "<br>"}, "description"),
            ({"category": "invalid-category"}, "category"),
            ({"year": "not-a-year"}, "year"),
            ({"year": -1}, "year"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
            ({"project_image_url": "not-a-url"}, "project_image_url"),
        ):
            with self.subTest(field=field, changes=changes):
                response = self.client.post(
                    self.list_url, {**self.payload, **changes}, format="json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
                self.assertEqual(Project.objects.count(), 1)

        payload = self.payload.copy()
        del payload["year"]
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("year", response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.project.starred_by.add(self.visitor)
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.detail_url, {"title": "Changed"}, format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Changed")
        self.assertEqual(self.project.description, "My website")
        self.assertEqual(self.project.year, 2026)

        response = self.client.put(
            self.detail_url, {"title": "Incomplete"}, format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("description", response.data)
        self.assertIn("year", response.data)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Changed")

        response = self.client.put(
            self.detail_url,
            {**self.payload, "category": "creative", "year": 2027},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "New project")
        self.assertEqual(self.project.description, "A useful application")
        self.assertEqual(self.project.category, "creative")
        self.assertEqual(self.project.year, 2027)
        self.assertTrue(self.project.starred_by.filter(pk=self.visitor.pk).exists())

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.assertEqual(self.project.starred_by.count(), 0)

        self.project.starred_by.add(self.owner)
        self.client.force_authenticate(user=self.visitor)
        self.assertFalse(self.client.get(self.detail_url).data["is_starred"])

        response = self.client.post(
            self.star_url, {"user_id": self.owner.pk}, format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 2)
        self.assertTrue(self.project.starred_by.filter(pk=self.visitor.pk).exists())
        self.assertTrue(self.project.starred_by.filter(pk=self.owner.pk).exists())
        self.assertTrue(self.client.get(self.list_url).data[0]["is_starred"])

        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertFalse(self.project.starred_by.filter(pk=self.visitor.pk).exists())
        self.assertTrue(self.project.starred_by.filter(pk=self.owner.pk).exists())

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        forged_id = str(uuid.uuid4())
        forged_fields = {
            "id": forged_id,
            "star_count": 99,
            "is_starred": True,
            "category_display": "Forged category",
            "starred_by": [self.visitor.pk],
        }

        response = self.client.post(
            self.list_url, {**self.payload, **forged_fields}, format="json",
        )
        self.assertEqual(response.status_code, 201)
        saved = Project.objects.get(pk=response.data["id"])
        self.assertNotEqual(str(saved.pk), forged_id)

        detail_url = reverse("api:project-detail", args=[saved.pk])
        update = self.client.patch(detail_url, forged_fields, format="json")
        self.assertEqual(update.status_code, 200)
        for data in (response.data, update.data):
            self.assertEqual(data["id"], str(saved.pk))
            self.assertEqual(data["star_count"], 0)
            self.assertFalse(data["is_starred"])
            self.assertEqual(data["category_display"], "Web Development")
            self.assertNotIn("starred_by", data)
        self.assertEqual(saved.starred_by.count(), 0)

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        editor_group = Group.objects.create(name="Editor")

        for is_staff, is_editor in ((True, False), (False, True), (True, True)):
            self.visitor.is_staff = is_staff
            self.visitor.save()
            self.visitor.groups.clear()
            if is_editor:
                self.visitor.groups.add(editor_group)
            self.client.force_authenticate(user=self.visitor)

            for method, url, payload in (
                ("post", self.list_url, self.payload),
                ("patch", self.detail_url, {"title": "Changed"}),
                ("put", self.detail_url, self.payload),
                ("delete", self.detail_url, None),
            ):
                with self.subTest(staff=is_staff, editor=is_editor, method=method):
                    response = getattr(self.client, method)(
                        url, payload, format="json",
                    )
                    self.assertEqual(response.status_code, 403)

        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)

        for method, url in (
            ("delete", self.list_url),
            ("post", self.detail_url),
            ("get", self.star_url),
            ("put", self.star_url),
        ):
            with self.subTest(method=method, url=url):
                self.assertEqual(getattr(self.client, method)(url).status_code, 405)

        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=self.owner.username, password=self.password))

        response = client.post(self.list_url, self.payload, format="json")

        self.assertEqual(response.status_code, 403)
        self.assertIn("CSRF", str(response.data["detail"]))
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=self.owner.username, password=self.password))

        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, 200)
        token = client.cookies["csrftoken"].value

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.objects.count(), 2)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())
