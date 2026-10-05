from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.db.models import BooleanField, Count, Exists, OuterRef, Value
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project
from main.permissions import is_editor, portfolio_permission_required


def with_star_status(queryset, user):
    """Fetch counts and the current user's status without loading other accounts."""
    status = Value(False, output_field=BooleanField())
    if user.is_authenticated:
        status = Exists(
            queryset.model.objects.filter(pk=OuterRef("pk"), starred_by=user)
        )
    return queryset.annotate(star_count=Count("starred_by"), is_starred=status)


def deserialize_with_star_status(response, model, user):
    """Preserve the JSON flow from Assignment 3 without exposing account data."""
    items = [
        item.object
        for item in serializers.deserialize("json", response.content.decode("utf-8"))
    ]
    queryset = model.objects.filter(pk__in=[item.pk for item in items])
    states = {
        pk: (count, starred)
        for pk, count, starred in with_star_status(queryset, user).values_list(
            "pk", "star_count", "is_starred"
        )
    }
    for item in items:
        item.star_count, item.is_starred = states.get(item.pk, (0, False))
    return items


def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
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
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def show_experience(request):
    experiences = with_star_status(
        Experience.objects.order_by("-started_at", "title"),
        request.user,
    )

    return render(request, "experience.html", {
        "logo": "KN",
        "name": "Khalishah",
        "experience_list": experiences,
        "is_editor": is_editor(request.user),
    })


def experience_detail(request, experience_id):
    experience = get_object_or_404(
        with_star_status(Experience.objects.all(), request.user), pk=experience_id
    )
    return render(request, "experience_detail.html", {
        "experience": experience,
        "is_editor": is_editor(request.user),
    })


@login_required(login_url="main:login")
@require_POST
def toggle_experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
        messages.success(request, "Star pada experience dibatalkan.")
    else:
        experience.starred_by.add(request.user)
        messages.success(request, "Experience diberi star.")
    detail_url = reverse("main:experience_detail", args=[experience.pk])
    if request.POST.get("next") == detail_url:
        return redirect(detail_url)
    return redirect("main:show_experience")

def show_projects(request):
    return render(request, "projects.html", {
        "logo": "KN",
        "name": "Khalishah",
        "is_editor": is_editor(request.user),
        "title_query": request.GET.get("title", "").strip(),
        "form": ProjectForm(),
    })

def show_about(request):
    return render(request, "detail.html", {"page_title": "About me", "section_template": "includes/about.html"})


def show_life(request):
    return render(request, "detail.html", {"page_title": "Life lately", "section_template": "includes/life.html"})


def show_contact(request):
    return render(request, "detail.html", {"page_title": "Let’s connect", "section_template": "includes/contact.html"})

@portfolio_permission_required()
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
            "page_title": "Add a project",
        },
    )

def get_projects_json(request):
    query = request.GET.get("title", "").strip()

    projects = Project.objects.order_by("-year", "title")

    if query:
        projects = projects.filter(title__icontains=query)

    projects = with_star_status(projects, request.user)

    data = []

    for project in projects:
        data.append({
            "model": "main.project",
            "pk": str(project.pk),
            "fields": {
                "title": project.title,
                "description": project.description,
                "category": project.category,
                "category_display": project.get_category_display(),
                "year": project.year,
                "project_url": project.project_url,
                "project_image_url": project.project_image_url,
                "star_count": project.star_count,
                "is_starred": project.is_starred,
            },
        })

    return JsonResponse(data, safe=False)

@portfolio_permission_required(allow_editor=True)
def update_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST if request.method == "POST" else None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project berhasil diperbarui.")
        return redirect("main:show_projects")
    return render(request, "projects_form.html", {
        "logo": "KN", "name": "Khalishah", "form": form, "page_title": "Edit project",
    })


@portfolio_permission_required()
@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, "Project berhasil dihapus.")
    return redirect("main:show_projects")


def get_experiences_json(request):
    experiences = with_star_status(
        Experience.objects.order_by("-started_at", "title"),
        request.user,
    )

    data = []

    for experience in experiences:
        data.append({
            "model": "main.experience",
            "pk": str(experience.pk),
            "fields": {
                "title": experience.title,
                "description": experience.description,
                "category": experience.category,
                "category_display": experience.get_category_display(),
                "thumbnail": experience.thumbnail or "",
                "started_at": experience.started_at.isoformat(),
                "ended_at": (
                    experience.ended_at.isoformat()
                    if experience.ended_at
                    else None
                ),
                "is_ongoing": experience.is_ongoing,
                "star_count": experience.star_count,
                "is_starred": experience.is_starred,
            },
        })

    return JsonResponse(data, safe=False)

@portfolio_permission_required()
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

@portfolio_permission_required(allow_editor=True)
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

@portfolio_permission_required()
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


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Khalishah",
        "form": form,
    }
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST if request.method == "POST" else None)
    next_url = request.POST.get("next", request.GET.get("next", ""))
    if not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_url = reverse("main:show_main")

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect(next_url)
        response.set_cookie(
            "last_login", timezone.localtime().strftime("%Y-%m-%d %H:%M:%S %Z"),
            httponly=True, samesite="Lax", secure=request.is_secure(),
        )
        return response

    context = {
        "name": "Khalishah",
        "form": form,
    }
    context["next"] = next_url
    return render(request, "login.html", context)

@require_POST
def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

# All authenticated roles may star a project; only POST can change state.
@login_required(login_url="main:login")
@require_POST
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
        messages.success(request, "Star pada project dibatalkan.")
    else:
        project.starred_by.add(request.user)
        messages.success(request, "Project diberi star.")
    return redirect("main:show_projects")

@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {
                "message": (
                    "Hanya pemilik portofolio "
                    "yang dapat menambahkan proyek."
                )
            },
            status=403,
        )

    form = ProjectForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {"errors": form.errors.get_json_data()},
            status=400,
        )

    project = form.save()

    return JsonResponse(
        {
            "message": "Proyek berhasil ditambahkan.",
            "pk": str(project.pk),
        },
        status=201,
    )