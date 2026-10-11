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
