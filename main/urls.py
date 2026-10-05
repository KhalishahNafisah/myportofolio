from django.urls import path

from main.views import (
    create_project,
    delete_project,
    update_project,
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
    register,
    login_user,
    logout_user,
    toggle_star,
    toggle_experience_star,
    experience_detail,
    create_project_ajax,
    create_experience_ajax,
)

app_name = "main"

urlpatterns = [
    path(
        "experience/add-ajax/",
        create_experience_ajax,
        name="create_experience_ajax",
    ),
    path("", show_main, name="show_main"),
    path("about/", show_about, name="show_about"),
    path("life/", show_life, name="show_life"),
    path("contact/", show_contact, name="show_contact"),
    path("experience/", show_experience, name="show_experience"),
    path("experience/<uuid:experience_id>/", experience_detail, name="experience_detail"),
    path("experience/<uuid:experience_id>/star/", toggle_experience_star, name="toggle_experience_star"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/add-ajax/", create_project_ajax, name="create_project_ajax"),
    path("projects/<uuid:project_id>/edit/", update_project, name="update_project"),
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
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path(
        "projects/<uuid:project_id>/star/",
        toggle_star,
        name="toggle_star",
    ),
]
