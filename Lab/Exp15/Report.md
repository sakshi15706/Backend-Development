# Experiment 15: Django To-Do Application

**A To-Do Application using Django and SQLite**

*Backend Development Lab: Experiment 15 Report*

Student: ______________ | Roll No.: ______________ | GitHub (optional): ______________

## 1. Objective

To install, set up and build a simple To-Do application using the Django web framework and the SQLite database. By the end of the experiment the student understands Django's project structure, the role of each generated file, the purpose of the key `manage.py` subcommands, and how to implement basic CRUD (Create, Read, Update, Delete) functionality.

## 2. Prerequisites

- Python 3.x installed (check with `python --version`).
- Basic familiarity with the command line / terminal.
- A text editor or IDE (VS Code).

## 3. Theory: What is Django?

Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. It follows the **MVT (Model-View-Template)** architectural pattern:

| Part | Role | File in this project |
|---|---|---|
| **Model** | Defines the data structure (database schema) | `todo/models.py` |
| **View** | Handles HTTP requests and business logic | `todo/views.py` |
| **Template** | Renders the HTML presentation layer | `todo/templates/todo/*.html` |

Django also provides a built-in ORM (Object-Relational Mapper), an authentication system, an admin panel and URL routing. The **ORM** lets Python classes represent database tables, so no raw SQL is needed.

## 4. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Language | Python 3 | Application code |
| Framework | Django | Routing, ORM, templates, admin |
| Database | SQLite (`db.sqlite3`) | Permanent storage, created automatically |
| Isolation | Virtual environment (`venv`) | Keeps project packages separate from system Python |
| Tools | VS Code, browser | Writing code, testing |

## 5. Installation and Setup

**Step 1: Create a virtual environment.** A virtual environment isolates the project's dependencies from the system Python.

```
mkdir django_todo_app
cd django_todo_app
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
```

**Step 2: Install Django and verify.**

```
pip install django
python -m django --version
```

**Step 3: Create the Django project.**

```
django-admin startproject todo_project .
```

The `.` at the end creates the project in the current directory. Without it, Django creates an extra nested folder.

*Output:* *(screenshot of the Django version and the `startproject` result)*

## 6. Understanding the Project Structure

After `startproject`, the directory looks like this:

```
django_todo_app/
├── manage.py
└── todo_project/
    ├── __init__.py
    ├── asgi.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

| File | Purpose |
|---|---|
| `manage.py` | Command-line utility for administrative tasks |
| `__init__.py` | Empty file that tells Python this directory is a package |
| `settings.py` | Main configuration: database, installed apps, middleware, templates |
| `urls.py` | The project's "table of contents"; routes URLs to views |
| `wsgi.py` | Entry point for WSGI-compatible web servers (production) |
| `asgi.py` | Entry point for ASGI-compatible web servers (async support) |

`wsgi.py` and `asgi.py` should not be modified unless required.

## 7. Understanding `manage.py` and Its Subcommands

`manage.py` is created automatically in every Django project. It sets the `DJANGO_SETTINGS_MODULE` environment variable and passes commands to `django-admin`. General syntax: `python manage.py <command> [options]`.

| Subcommand | Purpose |
|---|---|
| `startapp` | Creates a new Django app inside the project |
| `makemigrations` | Generates migration files from changes in `models.py` |
| `migrate` | Applies migrations to the database (creates or updates tables) |
| `runserver` | Starts the development server |
| `createsuperuser` | Creates an admin user for the admin panel |
| `shell` | Opens an interactive Python shell with Django loaded |
| `dbshell` | Opens the database command-line client |
| `check` | Validates the project for common problems |
| `showmigrations` | Lists all migrations and their status |
| `sqlmigrate` | Shows the SQL for a specific migration |
| `collectstatic` | Gathers static files into one directory |
| `dumpdata` / `loaddata` | Exports database data as JSON / loads it from a JSON fixture |

## 8. Building the To-Do Application

### Step 1: Create the app

```
python manage.py startapp todo
```

This creates the `todo/` folder with `migrations/`, `__init__.py`, `admin.py`, `apps.py`, `models.py`, `tests.py` and `views.py`.

| File | Purpose |
|---|---|
| `models.py` | Defines database models (tables) as Python classes |
| `views.py` | Handles HTTP requests and returns responses |
| `admin.py` | Registers models with Django's admin interface |
| `apps.py` | App-specific configuration |
| `tests.py` | Unit tests |
| `migrations/` | Stores database migration files |

### Step 2: Register the app in `todo_project/settings.py`

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'todo',   # Add this line
]
```

### Step 3: Define the model (`todo/models.py`)

```python
from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
```

This creates a `Task` table with three fields (plus an automatic `id`): `title`, `completed` and `created_at`.

### Step 4: Create and apply migrations

```
python manage.py makemigrations todo
python manage.py migrate
```

`makemigrations` writes a migration file describing the `Task` model. `migrate` creates the actual table in SQLite.

*Output:* *(screenshot of both commands)*

### Step 5: Create a superuser

```
python manage.py createsuperuser
```

Enter a username, email and password when prompted.

### Step 6: Register the model in admin (`todo/admin.py`)

```python
from django.contrib import admin
from .models import Task

admin.site.register(Task)
```

Tasks can now be managed at `http://127.0.0.1:8000/admin/`.

*Output:* *(screenshot of the admin panel with the Task model)*

### Step 7: Create the views (`todo/views.py`)

```python
from django.shortcuts import render, redirect
from .models import Task

def task_list(request):
    tasks = Task.objects.all().order_by('-created_at')
    return render(request, 'todo/task_list.html', {'tasks': tasks})

def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            Task.objects.create(title=title)
        return redirect('task_list')
    return render(request, 'todo/add_task.html')

def toggle_task(request, task_id):
    task = Task.objects.get(id=task_id)
    task.completed = not task.completed
    task.save()
    return redirect('task_list')

def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    task.delete()
    return redirect('task_list')
```

### Step 8: Create the URLs

`todo/urls.py` (new file):

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('add/', views.add_task, name='add_task'),
    path('toggle/<int:task_id>/', views.toggle_task, name='toggle_task'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
]
```

`todo_project/urls.py` (updated to include the app URLs):

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('todo.urls')),
]
```

### Step 9: Create the templates

Create the folder `todo/templates/todo/` with two files: `task_list.html` (shows all tasks with Toggle and Delete links and an "Add New Task" link) and `add_task.html` (a form with `{% csrf_token %}`, a title input and a submit button). Full code is in the project files.

### Step 10: Run the server

```
python manage.py runserver
```

Open `http://127.0.0.1:8000/` to see the application.

*Output:* *(screenshots of the task list page, the add task page, and a completed task shown with strike-through)*

## 9. Working of the Application

### 9.1 URL Routes

| Method | URL | View | Purpose |
|---|---|---|---|
| GET | `/` | `task_list` | Reads all tasks, newest first, and shows them |
| GET | `/add/` | `add_task` | Shows the add-task form |
| POST | `/add/` | `add_task` | Saves a new task, then redirects to the list |
| GET | `/toggle/<id>/` | `toggle_task` | Flips `completed` between True and False |
| GET | `/delete/<id>/` | `delete_task` | Deletes the task |
| GET | `/admin/` | Django admin | Manage tasks through the admin panel |

### 9.2 Request Flow (MVT)

```
Browser --> todo_project/urls.py --> todo/urls.py --> view function (views.py)
                                                          |
                                                          v
                                               Model / ORM (models.py) <--> db.sqlite3
                                                          |
                                                          v
                                            Template (task_list.html) --> HTML --> Browser
```

### 9.3 How each CRUD operation works

| Operation | How it works |
|---|---|
| **Create** | The form in `add_task.html` sends a POST request. The view reads `title` and calls `Task.objects.create(title=title)`, then redirects to the list. |
| **Read** | `task_list` runs `Task.objects.all().order_by('-created_at')` and passes the tasks to the template, which loops over them with `{% for %}`. If there are none, `{% empty %}` shows "No tasks yet." |
| **Update** | `toggle_task` loads the task by id, flips `completed` and calls `save()`. The template shows completed tasks with strike-through (`<s>`). |
| **Delete** | `delete_task` loads the task by id and calls `delete()`. |

**Post/Redirect/Get.** After adding, toggling or deleting, the views redirect to the list page, so refreshing the browser does not repeat the action.

**CSRF protection.** The form contains `{% csrf_token %}`, which Django checks on every POST request to prevent cross-site request forgery.

**Persistence.** Tasks are stored in the SQLite file `db.sqlite3`, so they remain after the server is stopped and restarted.

## 10. Database Design

The `Task` model creates the table `todo_task`:

| Column | Django field | Notes |
|---|---|---|
| id | AutoField | Added automatically, primary key |
| title | CharField(max_length=200) | Task text |
| completed | BooleanField(default=False) | Done or not done |
| created_at | DateTimeField(auto_now_add=True) | Set automatically when the task is created |

The SQL that Django generates can be viewed with `python manage.py sqlmigrate todo 0001`.

*Output:* *(screenshot of `sqlmigrate` output)*

## 11. Testing the Application

| Test | Expected Result |
|---|---|
| Open `/` with no tasks | "No tasks yet." is shown |
| **Create:** click Add New Task, enter a title, submit | Redirected to the list; new task appears at the top |
| Submit with an empty title | Browser blocks it (`required`); nothing saved |
| **Read:** open `/` | All tasks are displayed, newest first |
| **Update:** click Toggle | Task is shown with strike-through; clicking again removes it |
| **Delete:** click Delete | Task is removed from the list |
| Stop and restart the server | Tasks are still present (stored in `db.sqlite3`) |
| Open `/admin/` and log in | Tasks can be viewed, added, edited and deleted |
| `python manage.py test` | `Ran 6 tests ... OK` |

*Output:* *(screenshots of the main tests and the test run)*

## 12. Summary of Commands Used

```
# Environment setup
python -m venv venv
venv\Scripts\activate
pip install django

# Project creation
django-admin startproject todo_project .

# App creation
python manage.py startapp todo

# Database
python manage.py makemigrations todo
python manage.py migrate

# Admin user
python manage.py createsuperuser

# Tests and development server
python manage.py test
python manage.py runserver
```

## 13. Common Errors and Troubleshooting

| Error | Solution |
|---|---|
| `No module named django` | Activate the virtual environment and run `pip install django` |
| `TemplateDoesNotExist` | Check the structure `todo/templates/todo/file.html` and that `'todo'` is in `INSTALLED_APPS` |
| `No such table: todo_task` | Run `python manage.py makemigrations todo`, then `python manage.py migrate` |
| Port already in use | Use another port: `python manage.py runserver 8080` |
| `CSRF verification failed` | Make sure `{% csrf_token %}` is inside every POST form |
| `venv\Scripts\activate` is blocked in PowerShell | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again |

*(Keep only the errors you actually faced and describe how you fixed them.)*

## 14. Limitations and Future Scope

Current limitations:

- Toggle and delete use plain links (GET requests), so they change data without a confirmation and are not the safest practice.
- `Task.objects.get()` raises an error if the id does not exist, instead of showing a 404 page.
- There is no user login, so all tasks are shared.
- Tasks cannot be edited (only toggled or deleted) and have no due date or priority.
- The pages use plain HTML without styling.

Possible improvements:

- Use `get_object_or_404()` and POST forms for toggle and delete.
- Add an edit view with a Django `ModelForm`.
- Add user authentication so each user sees only their own tasks.
- Add due dates, priorities, search and pagination.
- Style the pages with CSS or Bootstrap, and deploy with a production database such as PostgreSQL.

## 15. Conclusion

In this experiment, Django was installed in a virtual environment and a project was created using `django-admin startproject`. The purpose of each generated file and the key `manage.py` subcommands was studied. A `todo` app was created, a `Task` model was defined, and migrations were applied to create the SQLite table. Views, URLs and templates were built to give a working To-Do application with full CRUD operations, and the model was also registered in the admin panel. Django's built-in ORM and admin interface allow rapid development without writing raw SQL, and the same pattern of models, views, URLs and templates applies to any Django application built in the future.

## References

1. Django Documentation, https://docs.djangoproject.com/
2. Django Tutorial, Writing your first Django app, https://docs.djangoproject.com/en/stable/intro/tutorial01/
3. Python venv documentation, https://docs.python.org/3/library/venv.html
