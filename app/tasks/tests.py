from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User

from .models import Task


class TaskAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='test', role='admin')
        self.manager = User.objects.create_user(username='manager', password='test', role='manager')
        self.employee = User.objects.create_user(username='employee', password='test', role='employee')

    def test_create_task_as_admin(self):
        self.client.force_login(self.admin)
        url = reverse('task-list')
        data = {'title': 'Test Task', 'executor': self.employee.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
