from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, busy_employees

router = DefaultRouter()
router.register(r"", TaskViewSet, basename="task")

urlpatterns = [
    path("busy-employees/", busy_employees, name="busy_employees"),
]

urlpatterns += router.urls