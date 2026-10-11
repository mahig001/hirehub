from django.test import TestCase
from django.urls import reverse
from core.models import ContactMessage


class ContactViewTests(TestCase):
    """Tests for ContactView."""
    
    def setUp(self):
        """Set up test data."""
        self.url = reverse('core:contact')
    
    def test_get_displays_form(self):
        """Test that GET request displays the contact form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/contact.html')
    
    def test_creates_contact_message(self):
        """Test that submitting the form creates a contact message."""
        # Verify no messages exist
        self.assertEqual(ContactMessage.objects.count(), 0)
        
        # Submit form
        response = self.client.post(self.url, {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message content'
        })
        
        # Verify message was created
        self.assertEqual(ContactMessage.objects.count(), 1)
        message = ContactMessage.objects.first()
        self.assertEqual(message.name, 'Test User')
        self.assertEqual(message.email, 'test@example.com')
        self.assertEqual(message.subject, 'Test Subject')
        self.assertEqual(message.message, 'Test message content')
        self.assertFalse(message.is_read)
        
        # Verify redirect
        self.assertEqual(response.status_code, 302)


class RobotsTxtViewTests(TestCase):
    """Tests for robots.txt view."""
    
    def test_robots_txt_returns_text_plain(self):
        """Test that robots.txt view returns text/plain content."""
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertIn('User-agent: *', response.content.decode())


class ErrorPageTests(TestCase):
    """Tests for custom error pages."""
    
    def test_404_page_renders(self):
        """Test that 404 error page can be rendered."""
        from core.views import handler404
        from django.http import HttpRequest
        
        request = HttpRequest()
        response = handler404(request)
        self.assertEqual(response.status_code, 404)


class SitemapTests(TestCase):
    """Tests for sitemap."""
    
    def test_sitemap_returns_xml(self):
        """Test that sitemap URL returns XML."""
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')

