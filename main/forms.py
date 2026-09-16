from django import forms

from main.models import Project


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