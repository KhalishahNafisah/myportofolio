import uuid
from datetime import datetime, timezone

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Experience


class ExperienceAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "Temporary-experience-test-947!"
        cls.owner = User.objects.create_superuser(
            username="experience-api-owner",
            email="owner@example.com",
            password=cls.password,
        )
        cls.visitor = User.objects.create_user(
            username="experience-api-reader", password=cls.password,
        )
        cls.editor = User.objects.create_user(
            username="experience-api-editor", password=cls.password,
        )
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.experience = Experience.objects.create(
            title="Research Assistant",
            description="Original research work",
            category="research",
        )
        cls.list_url = reverse("api:experience-list")
        cls.detail_url = reverse("api:experience-detail", args=[cls.experience.pk])
        cls.star_url = reverse("api:experience-star", args=[cls.experience.pk])
        cls.payload = {
            "title": "New experience",
            "description": "Helping with research",
            "category": "research",
            "thumbnail": "https://example.com/work.png",
            "ended_at": None,
        }

    def test_public_list_and_detail(self):
        self.experience.starred_by.add(self.visitor)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        experience = response.data[0]
        self.assertEqual(set(experience), {
            "id", "title", "description", "category", "category_display",
            "thumbnail", "started_at", "ended_at", "is_ongoing",
            "star_count", "is_starred",
        })
        self.assertEqual(experience["id"], str(self.experience.pk))
        self.assertEqual(experience["title"], "Research Assistant")
        self.assertEqual(experience["category_display"], "Research")
        self.assertEqual(experience["star_count"], 1)
        self.assertFalse(experience["is_starred"])
        self.assertTrue(experience["is_ongoing"])
        self.assertIsNone(experience["ended_at"])
        self.assertTrue(experience["started_at"])
        self.assertNotContains(response, self.visitor.username)
        self.assertNotContains(response, self.owner.email)

        detail = self.client.get(self.detail_url)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data, experience)
        for url in (self.list_url, self.detail_url):
            with self.subTest(method="HEAD", url=url):
                head = self.client.head(url)
                self.assertEqual(head.status_code, 200)
                self.assertEqual(head.content, b"")
            with self.subTest(method="OPTIONS", url=url):
                self.assertEqual(self.client.options(url).status_code, 200)
        self.assertEqual(self.experience.starred_by.count(), 1)

    def test_search_and_empty_results(self):
        newer = Experience.objects.create(
            title="Community event", description="Another experience",
            category="volunteer",
        )

        response = self.client.get(self.list_url, {"title": "  RESEARCH  "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.data], [str(self.experience.pk)],
        )

        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

        response = self.client.get(self.list_url, {"title": "   "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.data],
            [str(newer.pk), str(self.experience.pk)],
        )

    def test_missing_experience(self):
        missing_id = uuid.uuid4()
        detail_url = reverse("api:experience-detail", args=[missing_id])
        star_url = reverse("api:experience-star", args=[missing_id])
        self.assertEqual(self.client.get(detail_url).status_code, 404)

        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.patch(detail_url, {"title": "Changed"}, format="json").status_code,
            404,
        )
        self.assertEqual(self.client.delete(detail_url).status_code, 404)
        self.assertEqual(self.client.post(star_url).status_code, 404)
        self.assertEqual(Experience.objects.count(), 1)

    def test_guest_and_reader_cannot_manage_experience(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            for method, url, payload in (
                ("post", self.list_url, self.payload),
                ("patch", self.detail_url, {"title": "Changed"}),
                ("put", self.detail_url, self.payload),
                ("delete", self.detail_url, None),
            ):
                with self.subTest(user=user, method=method):
                    response = getattr(self.client, method)(url, payload, format="json")
                    self.assertEqual(response.status_code, 403)

        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Research Assistant")
        self.assertEqual(self.experience.description, "Original research work")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "title": "  <b>New experience</b>  ",
                "description": " <p>Helping with research</p> ",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Experience.objects.count(), 2)
        saved = Experience.objects.get(pk=response.data["id"])
        self.assertEqual(saved.title, "New experience")
        self.assertEqual(saved.description, "Helping with research")
        self.assertEqual(saved.category, "research")
        self.assertEqual(saved.thumbnail, "https://example.com/work.png")
        self.assertIsNotNone(saved.started_at)
        self.assertIsNone(saved.ended_at)
        self.assertTrue(response.data["is_ongoing"])
        self.assertEqual(saved.starred_by.count(), 0)

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in (
            ({"title": ""}, "title"),
            ({"title": "   "}, "title"),
            ({"title": "x" * 256}, "title"),
            ({"title": '<img src=x onerror="alert(1)" >'}, "title"),
            ({"description": ""}, "description"),
            ({"description": "<br>"}, "description"),
            ({"category": "invalid-category"}, "category"),
            ({"thumbnail": "javascript:alert(1)"}, "thumbnail"),
            ({"ended_at": "not-a-date"}, "ended_at"),
            ({"ended_at": ""}, "ended_at"),
        ):
            with self.subTest(field=field, changes=changes):
                response = self.client.post(
                    self.list_url, {**self.payload, **changes}, format="json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
                self.assertEqual(Experience.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.experience.starred_by.add(self.visitor)
        started_at = self.experience.started_at
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.detail_url, {"title": "Changed"}, format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Changed")
        self.assertEqual(self.experience.description, "Original research work")
        self.assertEqual(self.experience.started_at, started_at)

        response = self.client.put(
            self.detail_url, {"title": "Incomplete"}, format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("description", response.data)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Changed")

        response = self.client.put(
            self.detail_url,
            {**self.payload, "ended_at": "2026-11-01T09:30:00Z"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["is_ongoing"])
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "New experience")
        self.assertEqual(self.experience.started_at, started_at)
        self.assertEqual(
            self.experience.ended_at, datetime(2026, 11, 1, 9, 30, tzinfo=timezone.utc),
        )
        self.assertTrue(self.experience.starred_by.filter(pk=self.visitor.pk).exists())

        response = self.client.patch(
            self.detail_url, {"ended_at": None, "thumbnail": None}, format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_ongoing"])
        self.experience.refresh_from_db()
        self.assertIsNone(self.experience.ended_at)
        self.assertIsNone(self.experience.thumbnail)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.experience.starred_by.add(self.visitor)
        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(
            self.detail_url, {"title": "Edited by Editor"}, format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Edited by Editor")
        self.assertEqual(self.experience.description, "Original research work")

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.description, "Helping with research")
        self.assertTrue(self.experience.starred_by.filter(pk=self.visitor.pk).exists())

        self.assertEqual(
            self.client.post(self.list_url, self.payload, format="json").status_code,
            403,
        )
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)

        self.editor.groups.clear()
        response = self.client.patch(
            self.detail_url, {"title": "Access revoked"}, format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "New experience")

    def test_staff_flag_alone_does_not_grant_write_access(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.client.force_authenticate(user=self.visitor)
        for method, url, payload in (
            ("post", self.list_url, self.payload),
            ("patch", self.detail_url, {"title": "Changed"}),
            ("put", self.detail_url, self.payload),
            ("delete", self.detail_url, None),
        ):
            with self.subTest(method=method):
                response = getattr(self.client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Research Assistant")

    def test_computed_fields_and_start_time_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        forged_id = str(uuid.uuid4())
        forged_fields = {
            "id": forged_id,
            "started_at": "2020-01-01T00:00:00Z",
            "is_ongoing": False,
            "star_count": 99,
            "is_starred": True,
            "category_display": "Forged category",
            "starred_by": [self.visitor.pk],
        }
        response = self.client.post(
            self.list_url, {**self.payload, **forged_fields}, format="json",
        )
        self.assertEqual(response.status_code, 201)
        saved = Experience.objects.get(pk=response.data["id"])
        self.assertNotEqual(str(saved.pk), forged_id)
        self.assertNotEqual(
            saved.started_at, datetime(2020, 1, 1, tzinfo=timezone.utc),
        )
        started_at = saved.started_at

        update = self.client.patch(
            reverse("api:experience-detail", args=[saved.pk]),
            forged_fields,
            format="json",
        )
        self.assertEqual(update.status_code, 200)
        saved.refresh_from_db()
        self.assertEqual(saved.started_at, started_at)
        for data in (response.data, update.data):
            self.assertEqual(data["id"], str(saved.pk))
            self.assertTrue(data["is_ongoing"])
            self.assertEqual(data["star_count"], 0)
            self.assertFalse(data["is_starred"])
            self.assertEqual(data["category_display"], "Research")
            self.assertNotIn("starred_by", data)
        self.assertEqual(saved.starred_by.count(), 0)

    def test_star_requires_login_and_uses_current_account(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.assertEqual(self.experience.starred_by.count(), 0)

        self.experience.starred_by.add(self.owner)
        self.client.force_authenticate(user=self.visitor)
        self.assertFalse(self.client.get(self.detail_url).data["is_starred"])
        response = self.client.post(
            self.star_url, {"user_id": self.owner.pk}, format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 2)
        self.assertTrue(self.experience.starred_by.filter(pk=self.visitor.pk).exists())
        self.assertTrue(self.experience.starred_by.filter(pk=self.owner.pk).exists())
        self.assertTrue(self.client.get(self.list_url).data[0]["is_starred"])

        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertFalse(self.experience.starred_by.filter(pk=self.visitor.pk).exists())
        self.assertTrue(self.experience.starred_by.filter(pk=self.owner.pk).exists())

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
        self.assertEqual(Experience.objects.count(), 1)
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_session_write_without_csrf_is_rejected(self):
        for user, method, url, payload in (
            (self.owner, "post", self.list_url, self.payload),
            (self.editor, "patch", self.detail_url, {"title": "Edited"}),
            (self.visitor, "post", self.star_url, {}),
        ):
            with self.subTest(user=user, method=method):
                client = APIClient(enforce_csrf_checks=True)
                self.assertTrue(client.login(username=user.username, password=self.password))
                response = getattr(client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, 403)
                self.assertIn("CSRF", str(response.data["detail"]))
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Research Assistant")
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_session_write_with_csrf_succeeds(self):
        for user, method, url, payload, expected_status in (
            (self.owner, "post", self.list_url, self.payload, 201),
            (self.editor, "patch", self.detail_url, {"title": "Edited"}, 200),
            (self.visitor, "post", self.star_url, {}, 200),
        ):
            with self.subTest(user=user, method=method):
                client = APIClient(enforce_csrf_checks=True)
                self.assertTrue(client.login(username=user.username, password=self.password))
                page = client.get(reverse("main:show_experience"))
                self.assertEqual(page.status_code, 200)
                token = client.cookies["csrftoken"].value
                response = getattr(client, method)(
                    url, payload, format="json", HTTP_X_CSRFTOKEN=token,
                )
                self.assertEqual(response.status_code, expected_status)
        self.assertEqual(Experience.objects.count(), 2)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Edited")
        self.assertTrue(self.experience.starred_by.filter(pk=self.visitor.pk).exists())
