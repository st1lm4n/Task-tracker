from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "executor",
            "due_date",
            "status",
            "priority",
            "parent_task",
        ]
        widgets = {
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "parent_task": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ограничиваем выбор родительских задач только теми, которые не являются подзадачами этой задачи
        if self.instance and self.instance.pk:
            self.fields["parent_task"].queryset = Task.objects.exclude(
                pk=self.instance.pk
            )
        else:
            self.fields["parent_task"].queryset = Task.objects.all()
