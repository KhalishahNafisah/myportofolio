from django.urls import path

from main.views import show_main, show_experience, show_projects, show_about, show_life, show_contact

app_name = "main"

urlpatterns = [
    path("about/", show_about, name="show_about"),
    path("life/", show_life, name="show_life"),
    path("contact/", show_contact, name="show_contact"),
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("projects/", show_projects, name="show_projects"),
]