# Task Tracker

Система для отслеживания задач сотрудников с возможностью назначения, контроля выполнения и анализа загруженности.

## Функциональность

- Управление сотрудниками (CRUD операции)
- Управление задачами (CRUD операции)
- Иерархия задач (родительские и дочерние задачи)
- Назначение исполнителей задач
- Отслеживание статусов задач
- Специальные отчеты:
  - Занятые сотрудники (список сотрудников по загруженности)
  - Важные задачи (задачи, от которых зависят другие)

## Технологии

- Python 3.11
- Django 4.2.7
- Django REST Framework
- PostgreSQL
- Docker
- Nginx

## Установка и запуск

### Требования

- Docker
- Docker Compose

### Запуск

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd task-tracker
```

2. Создайте файл `.env` на основе `.env_example`:
```bash
cp .env_example .env
```

3. Запустите приложение:
```bash
docker-compose up --build
```

4. Приложение будет доступно по адресу: http://localhost

5. Для создания суперпользователя:
```bash
docker-compose exec app python manage.py createsuperuser
```

## API Endpoints

### Аутентификация

- `POST /api/auth/token/` - Получение JWT токена
- `POST /api/auth/token/refresh/` - Обновление JWT токена

### Пользователи

- `GET /api/users/` - Список пользователей (только для админов)

- `POST /api/users/` - Создание пользователя (только для админов)

- `GET /api/users/{id}/` - Информация о пользователе

- `PUT /api/users/{id}/` - Обновление пользователя

- `DELETE /api/users/{id}/` - Удаление пользователя (только для админов)

- `GET /api/users/me/` - Информация о текущем пользователе

### Задачи

- `GET /api/tasks/` - Список задач

- `POST /api/tasks/` - Создание задачи

- `GET /api/tasks/{id}/` - Информация о задаче

- `PUT /api/tasks/{id}/` - Обновление задачи

- `DELETE /api/tasks/{id}/` - Удаление задачи

- `GET /api/tasks/busy-employees/` - Занятые сотрудники (отсортированные по загруженности)

- `GET /api/tasks/important/` - Важные задачи (с рекомендациями по назначению)

### Документация API

- `GET /api/schema/` - Схема API

- `GET /api/docs/` - Интерактивная документация (Swagger)

## Модели данных

### Пользователь (User)

- username: Имя пользователя

- email: Email

- first_name: Имя

- last_name: Фамилия

- role: Роль (employee, manager, admin)

## Задача (Task)

- title: Название задачи

- description: Описание

- created_at: Дата создания

- updated_at: Дата обновления

- due_date: Срок выполнения

- status: Статус (new, in_progress, review, completed)

- priority: Приоритет (low, medium, high)

- executor: Исполнитель (ссылка на User)

- author: Автор (ссылка на User)

- parent_task: Родительская задача (ссылка на Task)

## Особенности реализации

### Специальные эндпоинты

#### Занятые сотрудники (/api/tasks/busy-employees/)

Возвращает список сотрудников, отсортированный по количеству активных задач (статусы: new, in_progress, review).

#### Важные задачи (/api/tasks/important/)

Находит задачи, которые:

1. Не взяты в работу (status = new)

2. Имеют подзадачи, которые в работе (status = in_progress)

Для каждой такой задачи предоставляет рекомендации по назначению исполнителей:

- Исполнитель родительской задачи (если у него не больше чем на 2 задачи больше, чем у наименее загруженного)

- Наименее загруженные сотрудники

## Тестирование

### Запуск тестов:

```bash
docker-compose exec app python manage.py test
```
Покрытие тестами: >75%

## Разработка

### Структура проекта
```text
task-tracker/
├── app/                 # Django приложение
│   ├── task_tracker/   # Настройки проекта
│   ├── tasks/          # Приложение задач
│   ├── users/          # Приложение пользователей
│   ├── static/         # Статические файлы
│   ├── templates/      # HTML шаблоны
│   ├── Dockerfile      # Конфигурация Docker
│   └── manage.py       # Управление Django
├── nginx/              # Nginx конфигурация
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml  # Docker Compose
└── README.md           # Документация
```

## Миграции

### Создание миграций:

```bash
docker-compose exec app python manage.py makemigrations
```

Применение миграций:

```bash
docker-compose exec app python manage.py migrate
```