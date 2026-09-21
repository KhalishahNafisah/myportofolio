from django.urls import path

from main.views import (
    create_project,
    delete_project,
    get_projects_json,
    show_about,
    show_contact,
    show_experience,
    show_life,
    show_main,
    show_projects,
    get_experiences_json,
    create_experience,
    update_experience,
    delete_experience,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("about/", show_about, name="show_about"),
    path("life/", show_life, name="show_life"),
    path("contact/", show_contact, name="show_contact"),
    path("experience/", show_experience, name="show_experience"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path(
        "projects/<uuid:project_id>/delete/",
        delete_project,
        name="delete_project",
    ),
    path(
        "api/experiences/",
        get_experiences_json,
        name="get_experiences_json",
    ),
    path(
        "experience/add/",
        create_experience,
        name="create_experience",
    ),
    path(
        "experience/<uuid:experience_id>/edit/",
        update_experience,
        name="update_experience",
    ),
    path(
        "experience/<uuid:experience_id>/delete/",
        delete_experience,
        name="delete_experience",
    ),
]