from django.test import TestCase
from django.urls import reverse
from notes.models import Note
from django.contrib.auth import get_user_model
from notes.forms import WARNING
from http import HTTPStatus

User = get_user_model()


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


class NoteTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создаем данные, которые не будут изменяться в тестах"""
        super().setUpTestData()
        # Создаем двух пользователей
        cls.author = User.objects.create_user(
            username='author',
            password='password123',
        )
        cls.other_user = User.objects.create_user(
            username='other_user',
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
        self.author_client = self.client_class()
        self.not_author_client = self.client_class()

        # Логиним пользователей в соответствующих клиентах
        self.author_client.force_login(self.author)
        self.not_author_client.force_login(self.other_user)

        # Данные для формы
        self.form_data = {
            'title': 'New Note',
            'text': 'New note text',
            'slug': 'new-slug',
        }

        # Аргументы для URL с slug
        self.slug_for_args = (self.note.slug,)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        # Используем обычный клиент (не авторизованный)
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        # Проверяем, что произошла переадресация на страницу логина:
        self.assertRedirects(response, expected_url)
        # Считаем количество заметок в БД, ожидаем 0 заметок.
        self.assertEqual(Note.objects.count(), 1)  # Только существующая заметка

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        # Подменяем slug новой заметки на slug уже существующей записи:
        self.form_data['slug'] = self.note.slug
        # Пытаемся создать новую заметку:
        response = self.author_client.post(url, data=self.form_data)
        # Проверяем, что в ответе содержится ошибка формы для поля slug:
        self.assertFormError(
            response.context['form'], 'slug', errors=(self.note.slug + WARNING)
        )
        # Убеждаемся, что количество заметок в базе осталось равным 1:
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=self.slug_for_args)
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=self.slug_for_args)
        response = self.not_author_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)


def test_other_user_cant_edit_note(self):
    url = reverse('notes:edit', args=(self.note.slug,))
    response = self.not_author_client.post(url, self.form_data)
    # Проверяем, что страница не найдена:
    self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    # Получаем новый объект запросом из БД.
    note_from_db = Note.objects.get(id=self.note.id)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    self.assertEqual(self.note.title, note_from_db.title)
    self.assertEqual(self.note.text, note_from_db.text)
    self.assertEqual(self.note.slug, note_from_db.slug)


def test_author_can_edit_note(self):
    # Получаем адрес страницы редактирования заметки:
    url = reverse('notes:edit', args=(self.note.slug,))
    # В POST-запросе на адрес редактирования заметки
    # отправляем form_data - новые значения для полей заметки:
    response = self.author_client.post(url, self.form_data)
    # Проверяем редирект:
    self.assertRedirects(response, reverse('notes:success'))
    # Обновляем объект заметки note: получаем обновлённые данные из БД:
    self.note.refresh_from_db()
    # Проверяем, что атрибуты заметки соответствуют обновлённым:
    self.assertEqual(self.note.title, self.form_data['title'])
    self.assertEqual(self.note.text, self.form_data['text'])
    self.assertEqual(self.note.slug, self.form_data['slug'])
