from django.shortcuts import render

from main.models import Experience


def show_main(request):
    context = {
        "logo": "KN",
        "name": "Khalishah",
        "npm": "2506605840",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada Project and Product Management."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "logo": "KN",
        "name": "Khalishah",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_projects(request):
    context = {
        "logo": "KN",
        "name": "Khalishah",
        "project_list": Project.objects.all(),
    }
    return render(request, "projects.html", context)