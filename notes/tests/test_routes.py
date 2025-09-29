from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus
from notes.models import Note

# news/tests/test_routes.py
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestRoutes(TestCase):

    def test_home_page(self):
        urls = (
            'notes:home',
            'users:login',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


class TestPagesAvailabilityForDifferentUsers(TestCase):

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.author = get_user_model().objects.create_user(
            username='author', password='password'
        )
        self.other_user = get_user_model().objects.create_user(
            username='other', password='password'
        )
        self.note = Note.objects.create(
            title='Test Note',
            text='Test text',
            author=self.author,
            slug='test-note',
        )

    def test_pages_availability_for_different_users(self):
        test_cases = [
            (self.other_user, HTTPStatus.NOT_FOUND),
            (self.author, HTTPStatus.OK),
        ]

        url_names = ('notes:detail', 'notes:edit', 'notes:delete')

        for user, expected_status in test_cases:
            for url_name in url_names:
                with self.subTest(
                    user=user.username,
                    url_name=url_name,
                    expected_status=expected_status,
                ):
                    self.client.force_login(user)
                    url = reverse(url_name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, expected_status)


class TestRedirects(TestCase):

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.client = Client()  # Анонимный клиент
        self.author = User.objects.create_user(
            username='test_author', password='password'
        )
        self.note = Note.objects.create(
            title='Test Note',
            text='Test text',
            author=self.author,
            slug='test-note',
        )

    def test_anonymous_user_redirects_to_login(self):
        """Тестируем редиректы анонимного пользователя на страницу логина."""
        test_cases = [
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        ]

        login_url = reverse('users:login')

        for name, args in test_cases:
            with self.subTest(name=name, args=args):
                if args is not None:
                    url = reverse(name, args=args)
                else:
                    url = reverse(name)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    expected_url,
                    status_code=302,
                    msg_prefix=f"Редирект для {name} работает неправильно",
                )
