from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Post
from django.contrib.auth.models import User


# Create your tests here.
class BlogTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='username',
            email='test@gmail.com',
            password='password'
        )

        self.post = Post.objects.create(
            title='A good title',
            body='Nice body',
            author=self.user
        )

    def test_string_representation(self):
        post = Post(title='A simple title')
        self.assertEqual(str(post), post.title)

    def test_post_content(self):
        self.assertEqual(f'{self.post.title}', 'A good title')
        self.assertEqual(f'{self.post.author}', 'username')
        self.assertEqual(f'{self.post.body}', 'Nice body')

    def test_post_list_view(self):
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_list.html')

    def test_post_detail_views(self):
        response = self.client.get('/1/')
        no_response = self.client.get('/100000/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, 'A good title')
        self.assertTemplateUsed(response, 'post_detail.html')


class BaseTest(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.user = {
            'email':'testemail@gmail.com',
            'username':'username',
            'password':'password',
            'password2':'password'
        }

class RegisterTest(BaseTest):
   def test_can_view_page_correctly(self):
       response = self.client.get(self.register_url)
       self.assertEqual(response.status_code, 200)
       self.assertTemplateUsed(response, 'reg.html')

   def test_can_register_user(self):
        response = self.client.post(self.register_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 200)

   def test_cant_register_user_with_taken_email(self):
        self.client.post(self.register_url, self.user, format='text/html')
        response = self.client.post(self.register_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 200)

class LoginTest(BaseTest):
    def test_can_access_page(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_login_success(self):
        self.client.post(self.register_url, self.user, format='text/html')
        user = User.objects.filter(email=self.user['email']).first()
        response = self.client.post(self.login_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 200)
    
    def test_cantlogin_with_unverified_email(self):
        self.client.post(self.register_url, self.user, format='text/html')
        response = self.client.post(self.login_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 200)

class LogoutTest(BaseTest):
    def test_logout(self):
        self.client.login(username='username', password="password")
        response = self.client.get('/admin/login')
        self.assertEquals(response.status_code, 302)
        self.client.logout()
        response = self.client.get('/admin/')
        self.assertEquals(response.status_code, 302)