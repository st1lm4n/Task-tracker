import django_filters
from .models import Task


class TaskFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    status = django_filters.ChoiceFilter(choices=Task.STATUS_CHOICES)
    priority = django_filters.ChoiceFilter(choices=Task.PRIORITY_CHOICES)
    executor = django_filters.NumberFilter(field_name="executor__id")

    class Meta:
        model = Task
        fields = ["status", "priority", "executor", "created_after", "created_before"]
