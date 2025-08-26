from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
        # Обработка эндпоинта .../api/users/me/
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


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

    # Добавляем статистику для отображения в профиле
    total_tasks = Task.objects.filter(executor=request.user).count()
    in_progress_tasks = Task.objects.filter(executor=request.user, status='in_progress').count()
    completed_tasks = Task.objects.filter(executor=request.user, status='completed').count()

    return render(request, 'users/profile.html', {
        'form': form,
        'total_tasks': total_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks
    })
