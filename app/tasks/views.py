from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from django.contrib import messages
from .filters import TaskFilter
from .forms import TaskForm
from .models import Task
from .permissions import IsAuthorOrExecutorOrAdmin
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthorOrExecutorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_queryset(self):
        queryset = Task.objects.select_related('executor', 'author').all()
        if self.request.user.role not in ['admin', 'manager']:
            queryset = queryset.filter(executor=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save()


@login_required
def task_list(request):
    tasks = Task.objects.filter(executor=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required
def task_detail(request, pk):
    from .models import Task
    task = Task.objects.get(pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required
def task_create(request):
    from users.models import User

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.author = request.user
            task.save()
            messages.success(request, 'Задача успешно создана!')
            return redirect('task_list')
    else:
        form = TaskForm()

    # Получаем всех пользователей для выпадающего списка
    users = User.objects.all()

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'title': 'Создать задачу',
        'users': users  # Передаем пользователей в шаблон
    })


@login_required
def task_update(request, pk):
    from .models import Task
    from users.models import User

    task = Task.objects.get(pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задача успешно обновлена!')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)

    # Получаем всех пользователей для выпадающего списка
    users = User.objects.all()

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'title': 'Редактировать задачу',
        'users': users  # Передаем пользователей в шаблон
    })


def home(request):
    from .models import Task

    if request.user.is_authenticated:
        total_tasks = Task.objects.filter(executor=request.user).count()
        in_progress_tasks = Task.objects.filter(executor=request.user, status='in_progress').count()
        completed_tasks = Task.objects.filter(executor=request.user, status='completed').count()

        return render(request, 'home.html', {
            'total_tasks': total_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completed_tasks': completed_tasks
        })
    else:
        return render(request, 'home.html')