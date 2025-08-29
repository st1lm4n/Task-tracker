from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.contrib import messages
from django.db.models import Count, Q
from .filters import TaskFilter
from .forms import TaskForm
from .models import Task
from .permissions import IsAuthorOrExecutorOrAdmin
from .serializers import TaskSerializer
from users.models import User


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthorOrExecutorOrAdmin]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "priority"]

    def get_queryset(self):
        queryset = Task.objects.select_related("executor", "author").all()
        if self.request.user.role not in ["admin", "manager"]:
            queryset = queryset.filter(executor=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

    # Специальный эндпоинт для важных задач
    @action(detail=False, methods=["get"])
    def important(self, request):
        # Задачи, которые не взяты в работу, но от которых зависят другие задачи, взятые в работу
        important_tasks = Task.objects.filter(
            status="new",  # Не взяты в работу
            subtasks__status="in_progress",  # Есть подзадачи в работе
        ).distinct()

        result = []
        for task in important_tasks:
            # Находим наименее загруженных сотрудников
            least_busy_employees = User.objects.annotate(
                task_count=Count(
                    "tasks",
                    filter=Q(tasks__status__in=["new", "in_progress", "review"]),
                )
            ).order_by("task_count")[
                :5
            ]  # 5 наименее загруженных

            # Проверяем исполнителя родительской задачи
            parent_task_assignee = None
            if task.parent_task and task.parent_task.executor:
                parent_assignee = task.parent_task.executor
                parent_task_count = parent_assignee.tasks.filter(
                    status__in=["new", "in_progress", "review"]
                ).count()

                # Если у исполнителя родительской задачи не больше чем на 2 задачи больше чем у наименее загруженного
                if (
                    least_busy_employees
                    and parent_task_count <= least_busy_employees[0].task_count + 2
                ):
                    parent_task_assignee = parent_assignee

            # Формируем список рекомендуемых исполнителей
            suggested_assignees = []
            if parent_task_assignee:
                suggested_assignees.append(parent_task_assignee)

            # Добавляем наименее загруженных сотрудников
            for employee in least_busy_employees:
                if employee not in suggested_assignees:
                    suggested_assignees.append(employee)

            result.append(
                {
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "due_date": task.due_date,
                    },
                    "suggested_assignees": [
                        {
                            "id": emp.id,
                            "username": emp.username,
                            "full_name": f"{emp.first_name} {emp.last_name}".strip()
                            or emp.username,
                            "role": emp.get_role_display(),
                            "current_task_count": emp.tasks.filter(
                                status__in=["new", "in_progress", "review"]
                            ).count(),
                        }
                        for emp in suggested_assignees[:3]  # Не более 3 рекомендаций
                    ],
                }
            )

        return Response(result)


# Эндпоинт для занятых сотрудников
@api_view(["GET"])
def busy_employees(request):
    # Список сотрудников и их задачи, отсортированный по количеству активных задач
    employees = User.objects.annotate(
        active_tasks_count=Count(
            "tasks", filter=Q(tasks__status__in=["new", "in_progress", "review"])
        )
    ).order_by("-active_tasks_count")

    result = []
    for employee in employees:
        tasks = employee.tasks.filter(status__in=["new", "in_progress", "review"])
        result.append(
            {
                "employee": {
                    "id": employee.id,
                    "username": employee.username,
                    "full_name": f"{employee.first_name} {employee.last_name}".strip()
                    or employee.username,
                    "role": employee.get_role_display(),
                },
                "active_tasks_count": employee.active_tasks_count,
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "status": task.get_status_display(),
                        "due_date": task.due_date,
                    }
                    for task in tasks
                ],
            }
        )

    return Response(result)


# Остальные представления остаются без изменений
@login_required
def task_list(request):
    tasks = Task.objects.filter(executor=request.user)
    return render(request, "tasks/task_list.html", {"tasks": tasks})


@login_required
def task_detail(request, pk):
    from .models import Task

    task = Task.objects.get(pk=pk)
    return render(request, "tasks/task_detail.html", {"task": task})


@login_required
def task_create(request):
    from users.models import User

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.author = request.user
            task.save()
            messages.success(request, "Задача успешно создана!")
            return redirect("task_list")
    else:
        form = TaskForm()

    # Получаем всех пользователей для выпадающего списка
    users = User.objects.all()

    return render(
        request,
        "tasks/task_form.html",
        {
            "form": form,
            "title": "Создать задачу",
            "users": users,  # Передаем пользователей в шаблон
        },
    )


@login_required
def task_update(request, pk):
    from .models import Task
    from users.models import User

    task = Task.objects.get(pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Задача успешно обновлена!")
            return redirect("task_list")
    else:
        form = TaskForm(instance=task)

    # Получаем всех пользователей для выпадающего списка
    users = User.objects.all()

    return render(
        request,
        "tasks/task_form.html",
        {
            "form": form,
            "title": "Редактировать задачу",
            "users": users,  # Передаем пользователей в шаблон
        },
    )


def home(request):
    from .models import Task

    if request.user.is_authenticated:
        total_tasks = Task.objects.filter(executor=request.user).count()
        in_progress_tasks = Task.objects.filter(
            executor=request.user, status="in_progress"
        ).count()
        completed_tasks = Task.objects.filter(
            executor=request.user, status="completed"
        ).count()

        return render(
            request,
            "home.html",
            {
                "total_tasks": total_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completed_tasks": completed_tasks,
            },
        )
    else:
        return render(request, "home.html")
