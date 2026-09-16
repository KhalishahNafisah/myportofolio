from django.test import TestCase
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

        self.assertRedirects(response, reverse("main:show_projects"))
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