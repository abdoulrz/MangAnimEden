from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class CoreViewsTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            nickname='testuser',
            password='testpassword'
        )

    def test_home_page_status_code_authenticated(self):
        self.client.login(email='testuser@example.com', password='testpassword')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_redirect_anonymous(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)

