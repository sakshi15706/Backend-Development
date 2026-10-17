from django.test import TestCase
from django.urls import reverse
from .models import Task


class TaskCrudTests(TestCase):

    def test_create_task(self):
        response = self.client.post(reverse('add_task'), {'title': 'Learn Django'})
        self.assertRedirects(response, reverse('task_list'))
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.first().title, 'Learn Django')

    def test_empty_title_not_saved(self):
        self.client.post(reverse('add_task'), {'title': ''})
        self.assertEqual(Task.objects.count(), 0)

    def test_read_task_list(self):
        Task.objects.create(title='Write report')
        response = self.client.get(reverse('task_list'))
        self.assertContains(response, 'Write report')

    def test_empty_list_message(self):
        response = self.client.get(reverse('task_list'))
        self.assertContains(response, 'No tasks yet.')

    def test_toggle_task(self):
        task = Task.objects.create(title='Toggle me')
        self.client.get(reverse('toggle_task', args=[task.id]))
        task.refresh_from_db()
        self.assertTrue(task.completed)
        self.client.get(reverse('toggle_task', args=[task.id]))
        task.refresh_from_db()
        self.assertFalse(task.completed)

    def test_delete_task(self):
        task = Task.objects.create(title='Delete me')
        self.client.get(reverse('delete_task', args=[task.id]))
        self.assertEqual(Task.objects.count(), 0)
