from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from main.models import Project, Experience


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "category",
            "year",
            "project_url",
            "project_image_url",
        ]
        labels = {
            "title": "Project title",
            "description": "Description",
            "category": "Category",
            "year": "Year",
            "project_url": "Project link",
            "project_image_url": "Image link",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Nama proyek atau kegiatan"}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Jelaskan proyek dan peranmu.",
                }
            ),
            "year": forms.NumberInput(
                attrs={"placeholder": "2026"}
            ),
            "project_url": forms.URLInput(
                attrs={"placeholder": "https://..."}
            ),
            "project_image_url": forms.URLInput(
                attrs={"placeholder": "https://..."}
            ),
        }

    def clean_title(self):
        title = strip_tags(
            self.cleaned_data["title"]
        ).strip()

        if not title:
            raise ValidationError(
                "Nama proyek tidak boleh hanya berisi tag HTML."
            )

        return title

    def clean_description(self):
        description = strip_tags(
            self.cleaned_data["description"]
        ).strip()

        if not description:
            raise ValidationError(
                "Deskripsi tidak boleh hanya berisi tag HTML."
            )

        return description

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "ended_at",
        ]
        labels = {
            "title": "Experience title",
            "description": "Description",
            "category": "Category",
            "thumbnail": "Image URL",
            "ended_at": "End date and time (UTC)",
        }
        help_texts = {
            "thumbnail": "Optional. Use a direct image URL.",
            "ended_at": (
                "Leave blank if this experience is ongoing. "
                "Enter the time in UTC."
            ),
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Nama peran atau pengalaman",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Jelaskan kegiatan dan peranmu.",
                }
            ),
            "thumbnail": forms.URLInput(
                attrs={
                    "placeholder": "https://...",
                }
            ),
            "ended_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                },
            ),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()

        if not title:
            raise ValidationError(
                "Judul pengalaman tidak boleh hanya berisi tag HTML."
            )

        return title

    def clean_description(self):
        description = strip_tags(
            self.cleaned_data["description"]
        ).strip()

        if not description:
            raise ValidationError(
                "Deskripsi pengalaman tidak boleh hanya berisi tag HTML."
            )

        return description
