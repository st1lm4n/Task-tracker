from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .filters import TaskFilter
from .forms import UserRegistrationForm, UserProfileForm
from .models import Task
from .models import User
from .permissions import IsAuthorOrExecutorOrAdmin
from .serializers import TaskSerializer
from .serializers import UserRegistrationSerializer, UserProfileSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthorOrExecutorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_queryset(self):
        # Базовая оптимизация: prefetch_related для FK
        queryset = Task.objects.select_related('executor', 'author').all()
        # Если пользователь не админ, показываем только связанные с ним задачи
        if self.request.user.role not in ['admin', 'manager']:
            queryset = queryset.filter(executor=self.request.user)
        return queryset

    def perform_create(self, serializer):
        # Автор задачи проставляется автоматически в сериализаторе
        serializer.save()


# HTML Views
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('task_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})


def home(request):
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

# API Views
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserProfileSerializer

