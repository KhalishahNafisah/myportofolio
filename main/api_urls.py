from django.urls import path

from main import api_views

app_name = "api"

urlpatterns = [
    path(
        "projects/<uuid:project_id>/",
        api_views.project_detail,
        name="project-detail",
    ),  
]