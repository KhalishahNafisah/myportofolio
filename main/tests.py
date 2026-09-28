from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Project


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )
        self.project = Project.objects.create(
            title="RISTALK Seminar 2026",
            description="Led the development of an AI and career seminar.",
            category="event",
            year=2026,
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_projects")}"',)

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    def test_projects_url_is_accessible_and_uses_correct_template(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")


    def test_project_data_appears_on_projects_page(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.description)
        self.assertContains(response, "Event Management")
        self.assertContains(response, "2026")


    def test_empty_projects_page_displays_empty_message(self):
        Project.objects.all().delete()

        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No projects have been added yet.")

class ProjectFlowTest(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="owner", is_superuser=True)
        self.client.force_login(owner)
        self.project = Project.objects.create(
            title="RISTALK",
            description="Seminar project.",
            category="event",
            year=2026,
        )

    def test_valid_form_saves_project(self):
        response = self.client.post(
            reverse("main:create_project"),
            {
                "title": "New Portfolio",
                "description": "My Django portfolio.",
                "category": "web",
                "year": 2026,
                "project_url": "",
                "project_image_url": "",
            },
        )

        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(
            Project.objects.filter(title="New Portfolio").exists()
        )

    def test_invalid_form_does_not_save(self):
        before = Project.objects.count()

        response = self.client.post(
            reverse("main:create_project"),
            {
                "title": "",
                "description": "Missing title.",
                "category": "web",
                "year": 2026,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.context["form"].errors)
        self.assertEqual(Project.objects.count(), before)

    def test_json_filter_ignores_case_and_outer_spaces(self):
        response = self.client.get(
            reverse("main:get_projects_json"),
            {"title": "  rist  "},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"], "application/json"
        )
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(
            response.json()[0]["fields"]["title"], "RISTALK"
        )

    def test_projects_page_filters_results(self):
        response = self.client.get(
            reverse("main:show_projects"),
            {"title": "does-not-exist"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "RISTALK")
        self.assertContains(response, "No matching projects found.")

    def test_get_request_does_not_delete(self):
        response = self.client.get(
            reverse("main:delete_project", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(
            Project.objects.filter(pk=self.project.pk).exists()
        )

    def test_post_request_deletes_project(self):
        project_id = self.project.pk

        response = self.client.post(
            reverse("main:delete_project", args=[project_id])
        )

        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(
            Project.objects.filter(pk=project_id).exists()
        )

    def test_delete_requires_csrf_token(self):
        from django.test import Client

        client = Client(enforce_csrf_checks=True)
        response = client.post(
            reverse("main:delete_project", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Project.objects.filter(pk=self.project.pk).exists()
        )

class ExperienceFlowTest(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="owner", is_superuser=True)
        self.client.force_login(owner)
        self.experience = Experience.objects.create(
            title="Original experience",
            description="Initial description.",
            category="volunteer",
        )

    def valid_payload(self):
        return {
            "title": "Updated experience",
            "description": "Updated description.",
            "category": "part-time",
            "thumbnail": "",
            "ended_at": "",
        }

    def test_create_experience(self):
        before = Experience.objects.count()

        response = self.client.post(
            reverse("main:create_experience"),
            self.valid_payload(),
        )

        self.assertRedirects(
            response,
            reverse("main:show_experience"),
        )
        self.assertEqual(Experience.objects.count(), before + 1)
        self.assertTrue(
            Experience.objects.filter(
                title="Updated experience",
            ).exists()
        )

    def test_invalid_create_does_not_save(self):
        before = Experience.objects.count()
        payload = self.valid_payload()
        payload["title"] = ""

        response = self.client.post(
            reverse("main:create_experience"),
            payload,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.context["form"].errors)
        self.assertEqual(Experience.objects.count(), before)

    def test_update_changes_existing_record(self):
        before = Experience.objects.count()

        response = self.client.post(
            reverse(
                "main:update_experience",
                args=[self.experience.pk],
            ),
            self.valid_payload(),
        )

        self.assertRedirects(
            response,
            reverse("main:show_experience"),
        )
        self.experience.refresh_from_db()
        self.assertEqual(
            self.experience.title,
            "Updated experience",
        )
        self.assertEqual(Experience.objects.count(), before)

    def test_invalid_update_preserves_saved_data(self):
        payload = self.valid_payload()
        payload["title"] = ""

        response = self.client.post(
            reverse(
                "main:update_experience",
                args=[self.experience.pk],
            ),
            payload,
        )

        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(
            self.experience.title,
            "Original experience",
        )

    def test_json_contains_experience(self):
        response = self.client.get(
            reverse("main:get_experiences_json")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/json",
        )

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["pk"], str(self.experience.pk))
        self.assertEqual(
            data[0]["fields"]["title"],
            self.experience.title,
        )

    def test_get_does_not_delete_experience(self):
        response = self.client.get(
            reverse(
                "main:delete_experience",
                args=[self.experience.pk],
            )
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(
            Experience.objects.filter(
                pk=self.experience.pk,
            ).exists()
        )

    def test_post_deletes_experience(self):
        experience_id = self.experience.pk

        response = self.client.post(
            reverse(
                "main:delete_experience",
                args=[experience_id],
            )
        )

        self.assertRedirects(
            response,
            reverse("main:show_experience"),
        )
        self.assertFalse(
            Experience.objects.filter(
                pk=experience_id,
            ).exists()
        )

    def test_delete_requires_csrf_token(self):
        from django.test import Client

        client = Client(enforce_csrf_checks=True)

        response = client.post(
            reverse(
                "main:delete_experience",
                args=[self.experience.pk],
            )
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Experience.objects.filter(
                pk=self.experience.pk,
            ).exists()
        )


class ExperienceAccessTest(TestCase):
    def setUp(self):
        self.regular = User.objects.create_user(username="reader")
        self.editor = User.objects.create_user(username="editor")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.owner = User.objects.create_user(username="owner", is_superuser=True)
        self.experience = Experience.objects.create(
            title="Protected experience", description="Original", category="volunteer"
        )
        self.payload = {
            "title": "Changed", "description": "Updated", "category": "research",
            "thumbnail": "", "ended_at": "",
        }
        self.urls = {
            "create": reverse("main:create_experience"),
            "update": reverse("main:update_experience", args=[self.experience.pk]),
            "delete": reverse("main:delete_experience", args=[self.experience.pk]),
        }

    def test_guests_are_redirected_before_accessing_mutations(self):
        for action, url in self.urls.items():
            for method in ("get", "post"):
                with self.subTest(action=action, method=method):
                    response = getattr(self.client, method)(url, self.payload if method == "post" else {})
                    self.assertEqual(response.status_code, 302)
                    self.assertEqual(response.url, f'{reverse("main:login")}?next={url}')
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Protected experience")
        self.assertEqual(Experience.objects.count(), 1)

    def test_regular_users_cannot_mutate_even_with_direct_requests(self):
        self.client.force_login(self.regular)
        for action, url in self.urls.items():
            for method in ("get", "post"):
                with self.subTest(action=action, method=method):
                    response = getattr(self.client, method)(url, self.payload if method == "post" else {})
                    self.assertEqual(response.status_code, 403)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Protected experience")
        self.assertEqual(Experience.objects.count(), 1)

    def test_editor_can_only_update(self):
        self.client.force_login(self.editor)
        for action in ("create", "delete"):
            for method in ("get", "post"):
                with self.subTest(action=action, method=method):
                    response = getattr(self.client, method)(self.urls[action], self.payload if method == "post" else {})
                    self.assertEqual(response.status_code, 403)
        self.assertEqual(self.client.get(self.urls["update"]).status_code, 200)
        response = self.client.post(self.urls["update"], self.payload)
        self.assertRedirects(response, reverse("main:show_experience"))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Changed")
        self.assertEqual(Experience.objects.count(), 1)

    def test_controls_match_each_role_and_list_stays_public(self):
        for user, create, update, delete in (
            (None, False, False, False),
            (self.regular, False, False, False),
            (self.editor, False, True, False),
            (self.owner, True, True, True),
        ):
            with self.subTest(user=user):
                self.client.logout()
                if user:
                    self.client.force_login(user)
                response = self.client.get(reverse("main:show_experience"))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, self.experience.title)
                for action, visible in (("create", create), ("update", update), ("delete", delete)):
                    assertion = self.assertContains if visible else self.assertNotContains
                    assertion(response, self.urls[action])

    def test_staff_flag_alone_does_not_grant_portfolio_access(self):
        self.regular.is_staff = True
        self.regular.save()
        self.client.force_login(self.regular)
        self.assertEqual(self.client.post(self.urls["update"], self.payload).status_code, 403)

    def test_revoking_editor_group_removes_edit_access(self):
        self.client.force_login(self.editor)
        self.editor.groups.clear()
        self.assertEqual(self.client.post(self.urls["update"], self.payload).status_code, 403)


class ExperienceStarTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="star-reader")
        self.other = User.objects.create_user(username="other-reader")
        self.experience = Experience.objects.create(title="Star test", description="Public description")
        self.url = reverse("main:toggle_experience_star", args=[self.experience.pk])
        self.detail_url = reverse("main:experience_detail", args=[self.experience.pk])

    def test_guest_is_redirected_without_adding_star(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("main:login")))
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_post_toggles_only_current_users_star(self):
        self.experience.starred_by.add(self.other)
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertEqual(self.experience.starred_by.count(), 2)
        self.assertTrue(self.experience.starred_by.filter(pk=self.user.pk).exists())
        self.client.post(self.url)
        self.assertEqual(list(self.experience.starred_by.all()), [self.other])

    def test_many_to_many_prevents_duplicate_stars(self):
        self.experience.starred_by.add(self.user)
        self.experience.starred_by.add(self.user)
        self.assertEqual(self.experience.starred_by.count(), 1)

    def test_get_cannot_toggle_star(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_csrf_is_required_and_valid_token_works(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(self.url).status_code, 403)
        self.assertEqual(self.experience.starred_by.count(), 0)
        client.get(self.detail_url)
        response = client.post(self.url, {"csrfmiddlewaretoken": client.cookies["csrftoken"].value})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.experience.starred_by.count(), 1)

    def test_list_and_detail_show_public_count_and_personal_state(self):
        self.experience.starred_by.add(self.user, self.other)
        for url in (reverse("main:show_experience"), self.detail_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "Login to star")
                self.assertContains(response, '<span class="star-count">2</span>', html=True)
                self.assertNotContains(response, self.other.username)
                self.client.force_login(self.user)
                response = self.client.get(url)
                self.assertContains(response, 'aria-pressed="true"')
                self.assertContains(response, "Unstar")
                self.client.logout()

    def test_star_returns_to_detail_when_requested(self):
        self.client.force_login(self.user)
        self.assertRedirects(self.client.post(self.url, {"next": self.detail_url}), self.detail_url)
        self.assertRedirects(
            self.client.post(self.url, {"next": "https://example.org/"}),
            reverse("main:show_experience"),
        )

    def test_missing_experience_returns_404(self):
        import uuid
        missing = uuid.uuid4()
        self.assertEqual(self.client.get(reverse("main:experience_detail", args=[missing])).status_code, 404)
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(reverse("main:toggle_experience_star", args=[missing])).status_code, 404)

    def test_public_json_preserves_schema_and_excludes_accounts(self):
        self.experience.starred_by.add(self.user)
        response = self.client.get(reverse("main:get_experiences_json"))
        item = response.json()[0]
        self.assertEqual(item["model"], "main.experience")
        self.assertEqual(item["pk"], str(self.experience.pk))
        self.assertEqual(set(item["fields"]), {
            "title", "description", "category", "thumbnail", "started_at", "ended_at",
        })
        self.assertNotContains(response, self.user.username)
        self.assertNotContains(response, "starred_by")


class AuthAndProjectSecurityTest(TestCase):
    def setUp(self):
        self.password = "Temporary-test-pass-837!"
        self.reader = User.objects.create_user(username="reader", password=self.password)
        self.editor = User.objects.create_user(username="editor")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.owner = User.objects.create_user(username="owner", is_superuser=True, is_staff=True)
        self.project = Project.objects.create(title="Secure project", description="Public", year=2026)
        self.payload = {
            "title": "Edited project", "description": "Updated", "category": "web", "year": 2026,
            "project_url": "", "project_image_url": "",
        }

    def test_login_preserves_safe_next_and_rejects_external_destinations(self):
        for target, expected in (
            ("/experience/", "/experience/"),
            ("/projects/?title=Secure", "/projects/?title=Secure"),
            ("https://example.org/", "/"),
            ("//example.org/", "/"),
            ("javascript:alert(1)", "/"),
        ):
            with self.subTest(target=target):
                self.client.logout()
                response = self.client.post(reverse("main:login"), {
                    "username": self.reader.username, "password": self.password, "next": target,
                })
                self.assertRedirects(response, expected)
                self.assertIn("last_login", response.cookies)
                self.assertTrue(response.cookies["last_login"]["httponly"])
                self.assertEqual(response.cookies["last_login"]["samesite"], "Lax")

    def test_login_form_keeps_next_through_invalid_password(self):
        response = self.client.get(reverse("main:login"), {"next": "/experience/"})
        self.assertContains(response, '<input type="hidden" name="next" value="/experience/">', html=True)
        response = self.client.post(reverse("main:login"), {
            "username": self.reader.username, "password": "incorrect", "next": "/experience/",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(response.context["next"], "/experience/")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_only_accepts_post_and_clears_session_and_cookie(self):
        self.client.force_login(self.reader)
        self.client.cookies["last_login"] = "previous visit"
        self.assertEqual(self.client.get(reverse("main:logout")).status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)
        response = self.client.post(reverse("main:logout"))
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(response.cookies["last_login"]["max-age"], 0)

    def test_registration_cannot_assign_privileged_roles(self):
        response = self.client.post(reverse("main:register"), {
            "username": "new-reader", "password1": self.password, "password2": self.password,
            "is_superuser": "1", "is_staff": "1", "groups": self.editor.groups.first().pk,
        })
        self.assertRedirects(response, reverse("main:login"))
        user = User.objects.get(username="new-reader")
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.groups.exists())

    def test_project_update_permissions_and_controls(self):
        url = reverse("main:update_project", args=[self.project.pk])
        for user, status in ((None, 302), (self.reader, 403), (self.editor, 302), (self.owner, 302)):
            with self.subTest(user=user):
                self.client.logout()
                self.project.title = "Secure project"
                self.project.save()
                if user:
                    self.client.force_login(user)
                response = self.client.post(url, self.payload)
                self.assertEqual(response.status_code, status)
                self.project.refresh_from_db()
                allowed = user in (self.editor, self.owner)
                self.assertEqual(self.project.title, "Edited project" if allowed else "Secure project")
                page = self.client.get(reverse("main:show_projects"))
                (self.assertContains if allowed else self.assertNotContains)(page, url)
                create = reverse("main:create_project")
                delete = reverse("main:delete_project", args=[self.project.pk])
                for action in (create, delete):
                    (self.assertContains if user == self.owner else self.assertNotContains)(page, action)

    def test_reader_and_editor_cannot_create_or_delete_projects(self):
        for user in (self.reader, self.editor):
            self.client.force_login(user)
            for url in (reverse("main:create_project"), reverse("main:delete_project", args=[self.project.pk])):
                for method in ("get", "post"):
                    with self.subTest(user=user, url=url, method=method):
                        self.assertEqual(getattr(self.client, method)(url, self.payload if method == "post" else {}).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_project_json_does_not_expose_star_accounts(self):
        self.project.starred_by.add(self.reader)
        response = self.client.get(reverse("main:get_projects_json"))
        self.assertEqual(set(response.json()[0]["fields"]), {
            "title", "description", "category", "year", "project_url", "project_image_url",
        })
        self.assertNotContains(response, self.reader.username)
        self.assertNotContains(response, "starred_by")

    def test_each_authenticated_role_can_toggle_project_stars(self):
        url = reverse("main:toggle_star", args=[self.project.pk])
        for user in (self.reader, self.editor, self.owner):
            with self.subTest(user=user):
                self.client.force_login(user)
                self.assertEqual(self.client.get(url).status_code, 405)
                self.assertRedirects(self.client.post(url), reverse("main:show_projects"))
                self.assertTrue(self.project.starred_by.filter(pk=user.pk).exists())
                page = self.client.get(reverse("main:show_projects"))
                self.assertContains(page, 'aria-pressed="true"')
                self.assertRedirects(self.client.post(url), reverse("main:show_projects"))
                self.assertFalse(self.project.starred_by.filter(pk=user.pk).exists())

    def test_project_page_does_not_display_other_account_names(self):
        self.project.starred_by.add(self.editor)
        self.client.force_login(self.reader)
        page = self.client.get(reverse("main:show_projects"))
        self.assertNotContains(page, self.editor.username)
        self.assertContains(page, '<span class="star-count">1</span>', html=True)
