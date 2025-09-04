from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("employee", "Employee"),
        ("manager", "Manager"),
        ("admin", "Admin"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="employee")

    @property
    def active_tasks_count(self):
        """Количество активных задач пользователя"""
        from django.db.models import Q
        return self.tasks.filter(
            Q(status="new") | Q(status="in_progress") | Q(status="review")
        ).count()