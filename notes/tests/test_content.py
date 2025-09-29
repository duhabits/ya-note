from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class NoteContentTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создаем данные, которые не будут изменяться в тестах"""
        super().setUpTestData()
        # Создаем двух пользователей
        cls.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='password123',
        )
        cls.other_user = User.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='password123',
        )

        # Создаем заметку от автора
        cls.note = Note.objects.create(
            title='Test Note',
            text='Test text',
            slug='test-slug',
            author=cls.author,
        )

    def setUp(self):
        """Настраиваем данные перед каждым тестом"""
        # Создаем клиенты для разных пользователей
        self.author_client = Client()
        self.not_author_client = Client()

        # Логиним пользователей в соответствующих клиентах
        self.author_client.force_login(self.author)
        self.not_author_client.force_login(self.other_user)

    def test_author_sees_own_notes_in_list(self):
        """Автор видит свою заметку в списке"""
        url = reverse('notes:list')
        response = self.author_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_other_user_does_not_see_author_notes_in_list(self):
        """Другой пользователь не видит чужие заметки в списке"""
        url = reverse('notes:list')
        response = self.not_author_client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_add_page_contains_form(self):
        """Страница создания заметки содержит форму"""
        url = reverse('notes:add')
        response = self.author_client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_contains_form(self):
        """Страница редактирования заметки содержит форму"""
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
