from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User

from .models import Task


class TaskAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="test", role="admin"
        )
        self.manager = User.objects.create_user(
            username="manager", password="test", role="manager"
        )
        self.employee = User.objects.create_user(
            username="employee", password="test", role="employee"
        )
        self.employee2 = User.objects.create_user(
            username="employee2", password="test", role="employee"
        )

    def test_create_task_as_admin(self):
        self.client.force_login(self.admin)
        url = reverse("task-list")
        data = {"title": "Test Task", "executor": self.employee.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)

    def test_create_task_with_parent(self):
        self.client.force_login(self.admin)

        # Создаем родительскую задачу
        parent_task = Task.objects.create(
            title="Parent Task", executor=self.employee, author=self.admin
        )

        # Создаем подзадачу
        url = reverse("task-list")
        data = {
            "title": "Child Task",
            "executor": self.employee.id,
            "parent_task": parent_task.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

        # Проверяем, что подзадача связана с родительской
        child_task = Task.objects.get(title="Child Task")
        self.assertEqual(child_task.parent_task, parent_task)
        self.assertEqual(parent_task.subtasks.count(), 1)
        self.assertEqual(parent_task.subtasks.first(), child_task)

    def test_busy_employees_endpoint(self):
        self.client.force_login(self.admin)

        # Создаем задачи для сотрудников
        Task.objects.create(
            title="Task 1",
            executor=self.employee,
            author=self.admin,
            status="in_progress",
        )
        Task.objects.create(
            title="Task 2",
            executor=self.employee,
            author=self.admin,
            status="in_progress",
        )
        Task.objects.create(
            title="Task 3", executor=self.employee2, author=self.admin, status="new"
        )

        url = reverse("busy_employees")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что employee более загружен, чем employee2
        employees_data = response.data
        self.assertEqual(len(employees_data), 3)  # admin, employee, employee2

        # Находим employee в ответе
        employee_data = next(
            emp for emp in employees_data if emp["employee"]["username"] == "employee"
        )
        employee2_data = next(
            emp for emp in employees_data if emp["employee"]["username"] == "employee2"
        )

        self.assertEqual(employee_data["active_tasks_count"], 2)
        self.assertEqual(employee2_data["active_tasks_count"], 1)
        self.assertGreater(
            employee_data["active_tasks_count"], employee2_data["active_tasks_count"]
        )

    def test_important_tasks_endpoint(self):
        self.client.force_login(self.admin)

        # Создаем родительскую задачу (не в работе)
        parent_task = Task.objects.create(
            title="Parent Task", executor=self.employee, author=self.admin, status="new"
        )

        # Создаем подзадачу (в работе)
        child_task = Task.objects.create(
            title="Child Task",
            executor=self.employee,
            author=self.admin,
            status="in_progress",
            parent_task=parent_task,
        )

        url = reverse("task-important", kwargs={})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что родительская задача найдена как важная
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["task"]["title"], "Parent Task")

        # Проверяем, что есть рекомендации по исполнителям
        self.assertIn("suggested_assignees", response.data[0])
        self.assertGreater(len(response.data[0]["suggested_assignees"]), 0)


class TaskModelTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="test", role="admin"
        )
        self.employee = User.objects.create_user(
            username="employee", password="test", role="employee"
        )

    def test_task_has_subtasks_in_progress(self):
        # Создаем родительскую задачу
        parent_task = Task.objects.create(
            title="Parent Task", executor=self.employee, author=self.admin
        )

        # Создаем подзадачу не в работе
        Task.objects.create(
            title="Child Task 1",
            executor=self.employee,
            author=self.admin,
            parent_task=parent_task,
            status="new",
        )

        # Проверяем, что нет подзадач в работе
        self.assertFalse(parent_task.has_subtasks_in_progress)

        # Создаем подзадачу в работе
        Task.objects.create(
            title="Child Task 2",
            executor=self.employee,
            author=self.admin,
            parent_task=parent_task,
            status="in_progress",
        )

        # Проверяем, что есть подзадачи в работе
        self.assertTrue(parent_task.has_subtasks_in_progress)

    def test_active_subtasks_count(self):
        # Создаем родительскую задачу
        parent_task = Task.objects.create(
            title="Parent Task", executor=self.employee, author=self.admin
        )

        # Создаем подзадачи
        Task.objects.create(
            title="Child Task 1",
            executor=self.employee,
            author=self.admin,
            parent_task=parent_task,
            status="new",
        )
        Task.objects.create(
            title="Child Task 2",
            executor=self.employee,
            author=self.admin,
            parent_task=parent_task,
            status="in_progress",
        )
        Task.objects.create(
            title="Child Task 3",
            executor=self.employee,
            author=self.admin,
            parent_task=parent_task,
            status="completed",
        )

        # Проверяем количество активных подзадач (исключая завершенные)
        self.assertEqual(parent_task.active_subtasks_count, 2)
