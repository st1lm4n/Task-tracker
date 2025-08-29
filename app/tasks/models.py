from django.db import models
from django.conf import settings


class Task(models.Model):
    STATUS_CHOICES = (
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("review", "Review"),
        ("completed", "Completed"),
    )
    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="medium"
    )
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_tasks",
    )
    # Новое поле: ссылка на родительскую задачу
    parent_task = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="subtasks"
    )

    def __str__(self):
        return self.title

    @property
    def has_subtasks_in_progress(self):
        """Проверяет, есть ли у задачи подзадачи в работе"""
        return self.subtasks.filter(status="in_progress").exists()

    @property
    def active_subtasks_count(self):
        """Количество активных подзадач (не завершенных)"""
        return self.subtasks.exclude(status="completed").count()
