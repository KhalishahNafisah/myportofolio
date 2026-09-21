from django import forms

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