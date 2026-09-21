from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from main.forms import ProjectForm, ExperienceForm
from main.models import Experience, Project


def show_main(request):
    context = {
        "logo": "KN",
        "name": "Khalishah",
        "npm": "2506605840",
        "is_homepage": True,
        "project_list": Project.objects.order_by("-year", "title")[:3],
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada Project and Product Management."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    response = get_experiences_json(request)

    experience_list = [
        item.object
        for item in serializers.deserialize(
            "json",
            response.content.decode("utf-8"),
        )
    ]

    context = {
        "logo": "KN",
        "name": "Khalishah",
        "experience_list": experience_list,
    }

    return render(request, "experience.html", context)

def show_projects(request):
    response = get_projects_json(request)

    project_list = [
        item.object
        for item in serializers.deserialize(
            "json",
            response.content.decode("utf-8"),
        )
    ]

    return render(
        request,
        "projects.html",
        {
            "logo": "KN",
            "name": "Khalishah",
            "project_list": project_list,
            "title_query": request.GET.get("title", "").strip(),
        },
    )

def show_about(request):
    return render(request, "detail.html", {"page_title": "About me", "section_template": "includes/about.html"})


def show_life(request):
    return render(request, "detail.html", {"page_title": "Life lately", "section_template": "includes/life.html"})


def show_contact(request):
    return render(request, "detail.html", {"page_title": "Let’s connect", "section_template": "includes/contact.html"})

def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Project berhasil ditambahkan.")
            return redirect("main:show_projects")
    else:
        form = ProjectForm()

    return render(
        request,
        "projects_form.html",
        {
            "logo": "KN",
            "name": "Khalishah",
            "form": form,
        },
    )

def get_projects_json(request):
    query = request.GET.get("title", "").strip()
    queryset = Project.objects.order_by("-year", "title")

    if query:
        queryset = queryset.filter(title__icontains=query)

    return HttpResponse(
        serializers.serialize("json", queryset),
        content_type="application/json",
    )

def delete_project(request, project_id):
    if request.method == "POST":
        project = get_object_or_404(Project, pk=project_id)
        project.delete()
        messages.success(request, "Project berhasil dihapus.")

    return redirect("main:show_projects")

def get_experiences_json(request):
    experiences = Experience.objects.order_by("-started_at", "title")

    return HttpResponse(
        serializers.serialize("json", experiences),
        content_type="application/json",
    )

def create_experience(request):
    if request.method == "POST":
        form = ExperienceForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Experience berhasil ditambahkan.",
            )
            return redirect("main:show_experience")
    else:
        form = ExperienceForm()

    return render(
        request,
        "experience_form.html",
        {
            "logo": "KN",
            "name": "Khalishah",
            "form": form,
            "page_title": "Add experience",
            "submit_label": "Save experience",
        },
    )

def update_experience(request, experience_id):
    experience = get_object_or_404(
        Experience,
        pk=experience_id,
    )

    if request.method == "POST":
        form = ExperienceForm(
            request.POST,
            instance=experience,
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Experience berhasil diperbarui.",
            )
            return redirect("main:show_experience")
    else:
        form = ExperienceForm(instance=experience)

    return render(
        request,
        "experience_form.html",
        {
            "logo": "KN",
            "name": "Khalishah",
            "form": form,
            "page_title": "Edit experience",
            "submit_label": "Save changes",
        },
    )

@require_POST
def delete_experience(request, experience_id):
    experience = get_object_or_404(
        Experience,
        pk=experience_id,
    )
    experience.delete()

    messages.success(
        request,
        "Experience berhasil dihapus.",
    )
    return redirect("main:show_experience")