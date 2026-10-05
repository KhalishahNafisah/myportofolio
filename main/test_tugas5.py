from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience


class AssignmentFiveExperienceTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="tugas5-owner",
            is_superuser=True,
            is_staff=True,
        )

        self.editor = User.objects.create_user(
            username="tugas5-editor"
        )
        self.editor.groups.add(
            Group.objects.create(name="Editor")
        )

        self.reader = User.objects.create_user(
            username="tugas5-reader"
        )

        self.experience = Experience.objects.create(
            title="Research Assistant",
            description="Membantu penelitian sistem informasi.",
            category="research",
        )

        self.list_url = reverse("main:show_experience")
        self.json_url = reverse("main:get_experiences_json")
        self.create_url = reverse("main:create_experience_ajax")

    def payload(self, **changes):
        data = {
            "title": "Koordinator Acara",
            "description": "Mengelola koordinasi kegiatan mahasiswa.",
            "category": "volunteer",
            "thumbnail": "",
            "ended_at": "",
        }
        data.update(changes)
        return data

    def test_page_is_a_public_ajax_shell(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")

        for marker in (
            'id="experience-grid"',
            'id="experience-loading"',
            'id="experience-empty"',
            'id="experience-error"',
            'id="experience-search"',
            "js/experiences.js",
            "js/experiences-search.js",
        ):
            with self.subTest(marker=marker):
                self.assertContains(response, marker)

        self.assertNotContains(
            response,
            self.experience.title,
        )

    def test_json_has_display_fields_without_account_list(self):
        self.experience.starred_by.add(self.reader)

        response = self.client.get(self.json_url)
        fields = response.json()[0]["fields"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            fields["title"],
            "Research Assistant",
        )
        self.assertEqual(
            fields["category_display"],
            "Research",
        )
        self.assertEqual(fields["star_count"], 1)
        self.assertFalse(fields["is_starred"])
        self.assertTrue(fields["is_ongoing"])
        self.assertIsNone(fields["ended_at"])
        self.assertNotIn("starred_by", fields)
        self.assertNotContains(response, self.reader.username)

    def test_star_status_is_specific_to_current_user(self):
        self.experience.starred_by.add(self.reader)

        self.client.force_login(self.reader)
        reader_data = self.client.get(self.json_url).json()
        self.assertTrue(
            reader_data[0]["fields"]["is_starred"]
        )

        self.client.force_login(self.editor)
        editor_data = self.client.get(self.json_url).json()
        self.assertFalse(
            editor_data[0]["fields"]["is_starred"]
        )

        self.assertEqual(
            editor_data[0]["fields"]["star_count"],
            1,
        )

    def test_search_ignores_case_and_outer_spaces(self):
        Experience.objects.create(
            title="Panitia Festival",
            description="Membantu pelaksanaan festival.",
            category="volunteer",
        )

        response = self.client.get(
            self.json_url,
            {"title": "  RESEARCH  "},
        )

        items = response.json()

        self.assertEqual(len(items), 1)
        self.assertEqual(
            items[0]["pk"],
            str(self.experience.pk),
        )

    def test_search_without_matches_returns_empty_list(self):
        response = self.client.get(
            self.json_url,
            {"title": "tidak-ada-judul-ini"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_empty_search_returns_all_items(self):
        response = self.client.get(
            self.json_url,
            {"title": "   "},
        )

        self.assertEqual(len(response.json()), 1)

    def test_owner_can_create_experience(self):
        self.client.force_login(self.owner)
        before = Experience.objects.count()

        response = self.client.post(
            self.create_url,
            self.payload(),
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Experience.objects.count(),
            before + 1,
        )

        saved = Experience.objects.get(
            pk=response.json()["pk"]
        )

        self.assertEqual(saved.title, "Koordinator Acara")
        self.assertEqual(saved.category, "volunteer")
        self.assertIsNone(saved.ended_at)
        self.assertTrue(saved.is_ongoing)
        self.assertEqual(saved.starred_by.count(), 0)

    def test_other_roles_cannot_create_experience(self):
        before = Experience.objects.count()

        for user in (None, self.reader, self.editor):
            with self.subTest(user=user):
                self.client.logout()

                if user:
                    self.client.force_login(user)

                response = self.client.post(
                    self.create_url,
                    self.payload(),
                )

                self.assertEqual(response.status_code, 403)
                self.assertIn("message", response.json())
                self.assertEqual(
                    Experience.objects.count(),
                    before,
                )

    def test_get_is_not_allowed_on_create_endpoint(self):
        self.client.force_login(self.owner)
        before = Experience.objects.count()

        response = self.client.get(self.create_url)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(
            Experience.objects.count(),
            before,
        )

    def test_invalid_input_returns_field_errors_without_saving(self):
        self.client.force_login(self.owner)

        cases = (
            ("title", ""),
            ("description", ""),
            ("category", "kategori-tidak-valid"),
            ("thumbnail", "bukan-url"),
            ("ended_at", "bukan-tanggal"),
            ("title", "x" * 256),
        )

        before = Experience.objects.count()

        for field, value in cases:
            with self.subTest(field=field, value=value):
                response = self.client.post(
                    self.create_url,
                    self.payload(**{field: value}),
                )

                self.assertEqual(response.status_code, 400)
                self.assertIn(
                    field,
                    response.json()["errors"],
                )
                self.assertEqual(
                    Experience.objects.count(),
                    before,
                )

    def test_html_tags_are_removed_from_text_fields(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.create_url,
            self.payload(
                title="  <b>Koordinator</b>  ",
                description=" <p>Deskripsi <em>aman</em>.</p> ",
            ),
        )

        self.assertEqual(response.status_code, 201)

        saved = Experience.objects.get(
            pk=response.json()["pk"]
        )

        self.assertEqual(saved.title, "Koordinator")
        self.assertEqual(saved.description, "Deskripsi aman.")

    def test_html_only_text_is_rejected(self):
        self.client.force_login(self.owner)
        before = Experience.objects.count()

        for field in ("title", "description"):
            with self.subTest(field=field):
                response = self.client.post(
                    self.create_url,
                    self.payload(
                        **{
                            field: '<img src="x" onerror="alert(1)">'
                        }
                    ),
                )

                self.assertEqual(response.status_code, 400)
                self.assertIn(
                    field,
                    response.json()["errors"],
                )
                self.assertEqual(
                    Experience.objects.count(),
                    before,
                )

    def test_completed_experience_is_returned_correctly(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.create_url,
            self.payload(
                ended_at=timezone.now().strftime(
                    "%Y-%m-%dT%H:%M"
                )
            ),
        )

        self.assertEqual(response.status_code, 201)

        saved_id = response.json()["pk"]

        items = self.client.get(self.json_url).json()
        saved_item = next(
            item for item in items
            if item["pk"] == saved_id
        )

        self.assertFalse(
            saved_item["fields"]["is_ongoing"]
        )
        self.assertIsNotNone(
            saved_item["fields"]["ended_at"]
        )

    def test_post_cannot_assign_star_membership(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.create_url,
            self.payload(
                starred_by=[self.reader.pk]
            ),
        )

        self.assertEqual(response.status_code, 201)

        saved = Experience.objects.get(
            pk=response.json()["pk"]
        )

        self.assertEqual(saved.starred_by.count(), 0)

    def test_csrf_is_required_and_valid_token_succeeds(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)

        before = Experience.objects.count()

        missing_token = client.post(
            self.create_url,
            self.payload(),
        )

        self.assertEqual(missing_token.status_code, 403)
        self.assertEqual(
            Experience.objects.count(),
            before,
        )

        client.get(self.list_url)
        token = client.cookies["csrftoken"].value

        invalid_token = client.post(
            self.create_url,
            self.payload(),
            HTTP_X_CSRFTOKEN="invalid",
        )

        self.assertEqual(invalid_token.status_code, 403)
        self.assertEqual(
            Experience.objects.count(),
            before,
        )

        valid_token = client.post(
            self.create_url,
            self.payload(),
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(valid_token.status_code, 201)
        self.assertEqual(
            Experience.objects.count(),
            before + 1,
        )

    def test_role_controls_match_permissions(self):
        for user, can_create, can_edit, can_delete in (
            (None, False, False, False),
            (self.reader, False, False, False),
            (self.editor, False, True, False),
            (self.owner, True, True, True),
        ):
            with self.subTest(user=user):
                self.client.logout()

                if user:
                    self.client.force_login(user)

                response = self.client.get(self.list_url)

                for marker, visible in (
                    ('id="experience-form"', can_create),
                    ('data-edit-url=', can_edit),
                    ('data-delete-url=', can_delete),
                ):
                    assertion = (
                        self.assertContains
                        if visible
                        else self.assertNotContains
                    )
                    assertion(response, marker)

    def test_ajax_view_does_not_bypass_revoked_access(self):
        self.client.force_login(self.owner)

        self.owner.is_superuser = False
        self.owner.save(update_fields=["is_superuser"])

        response = self.client.post(
            self.create_url,
            self.payload(),
        )

        self.assertEqual(response.status_code, 403)
