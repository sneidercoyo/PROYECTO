from django.test import TestCase, Client, override_settings
from django.urls import reverse


@override_settings(DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}})
class PaginasPublicasTests(TestCase):
    """Pruebas de páginas públicas que no requieren base de datos."""

    def setUp(self):
        self.client = Client()

    def test_home_carga(self):
        """La página de inicio carga correctamente."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_tienda_carga(self):
        """La página de tienda carga correctamente."""
        response = self.client.get(reverse('shop'))
        self.assertEqual(response.status_code, 200)

    def test_contacto_carga(self):
        """La página de contacto carga correctamente."""
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    def test_login_carga(self):
        """La página de login carga correctamente."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_registro_carga(self):
        """La página de registro carga correctamente."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_nosotros_carga(self):
        """La página de nosotros carga correctamente."""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_artesanos_carga(self):
        """La página de artesanos carga correctamente."""
        response = self.client.get(reverse('artisans'))
        self.assertEqual(response.status_code, 200)


@override_settings(DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}})
class FormTests(TestCase):
    """Pruebas de formularios."""

    def setUp(self):
        self.client = Client()

    def test_login_form_validation(self):
        """Login con email inválido muestra error."""
        response = self.client.post(reverse('login'), {
            'email': 'no-es-email',
            'password': '123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Correo electr')

    def test_registro_password_mismatch(self):
        """Registro con contraseñas diferentes muestra error."""
        response = self.client.post(reverse('register'), {
            'name': 'Test',
            'email': 'test@test.com',
            'password': 'abc123',
            'password_confirm': 'xyz789'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'no coinciden')

    def test_contacto_form(self):
        """Formulario de contacto con datos válidos."""
        response = self.client.post(reverse('contact'), {
            'name': 'Juan Pérez',
            'email': 'juan@test.com',
            'phone': '3101234567',
            'message': 'Mensaje de prueba'
        })
        self.assertEqual(response.status_code, 302)
