from django.test import TestCase
from django.urls import reverse
from notes.models import Note


class NoteCreationTest(TestCase):
    def setUp(self):
        # Здесь нужно создать пользователя и авторизовать клиент
        self.author = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        # Тестовые данные
        self.form_data = {
            'title': 'Test Note',
            'text': 'This is a test note',
            'slug': 'test-note',
        }

    def test_user_can_create_note(self):
        url = reverse('notes:add')

        # POST-запрос с тестовыми данными
        response = self.client.post(url, data=self.form_data)

        # Проверка редиректа
        self.assertRedirects(response, reverse('notes:success'))

        # Проверка количества заметок в БД
        self.assertEqual(Note.objects.count(), 1)

        # Получение созданной заметки и проверка её атрибутов
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)
