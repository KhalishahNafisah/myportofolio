import uuid
from django.db import models
from django.contrib.auth.models import User  # Tambahkan baris ini


# Create your models here.
import uuid

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

class Project(models.Model):
    PROJECT_CATEGORY_CHOICES = [
        ("event", "Event Management"),
        ("marketing", "Marketing & Communications"),
        ("creative", "Creative Production"),
        ("web", "Web Development"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=PROJECT_CATEGORY_CHOICES,
        default="event",
    )
    year = models.PositiveIntegerField()
    project_url = models.URLField(blank=True, default="")

    project_image_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
    )

    def __str__(self):
        return self.title

    project_image_url = models.URLField(blank=True, max_length=500)
    # Tambahkan field berikut: satu proyek bisa di-star banyak pengguna,
    # dan satu pengguna bisa mem-star banyak proyek
    starred_by = models.ManyToManyField(
        User, related_name="starred_projects", blank=True
    )