from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .forms import UserRegistrationForm, UserProfileForm
from .models import User
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import UserRegistrationSerializer, UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserProfileSerializer

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


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
    from tasks.models import Task  # Импортируем здесь, чтобы избежать циклических импортов

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    total_tasks = Task.objects.filter(executor=request.user).count()
    in_progress_tasks = Task.objects.filter(executor=request.user, status='in_progress').count()
    completed_tasks = Task.objects.filter(executor=request.user, status='completed').count()

    return render(request, 'users/profile.html', {
        'form': form,
        'total_tasks': total_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks
    })