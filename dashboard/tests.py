from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from companies.models import Company
from core.models import AuditLog


class AdminDashboardViewTests(TestCase):
    """Tests for AdminDashboardView."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role=User.ADMIN
        )
        self.regular_user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            first_name='Regular',
            last_name='User',
            role=User.USER
        )
        self.url = reverse('dashboard:admin_dashboard')
    
    def test_admin_can_access(self):
        """Test that admin users can access the dashboard."""
        self.client.force_login(self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/admin_dashboard.html')
    
    def test_non_admin_cannot_access(self):
        """Test that non-admin users cannot access the dashboard."""
        self.client.force_login(self.regular_user)
        response = self.client.get(self.url)
        # Should redirect or return 403
        self.assertIn(response.status_code, [302, 403])


class UserToggleActiveViewTests(TestCase):
    """Tests for UserToggleActiveView."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role=User.ADMIN
        )
        self.target_user = User.objects.create_user(
            email='target@test.com',
            password='testpass123',
            first_name='Target',
            last_name='User',
            role=User.USER,
            is_active=True
        )
        self.url = reverse('dashboard:user_toggle_active', kwargs={'pk': self.target_user.pk})
    
    def test_creates_audit_log(self):
        """Test that toggling user status creates an audit log."""
        self.client.force_login(self.admin_user)
        
        # Verify no audit logs exist
        self.assertEqual(AuditLog.objects.count(), 0)
        
        # Toggle user active status
        response = self.client.post(self.url)
        
        # Verify audit log was created
        self.assertEqual(AuditLog.objects.count(), 1)
        audit_log = AuditLog.objects.first()
        self.assertEqual(audit_log.actor, self.admin_user)
        self.assertEqual(audit_log.action, 'USER_DEACTIVATED')
        self.assertEqual(audit_log.target_model, 'User')
        self.assertEqual(audit_log.target_id, self.target_user.pk)


class CompanyApprovalViewTests(TestCase):
    """Tests for CompanyApprovalView."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role=User.ADMIN
        )
        self.company_owner = User.objects.create_user(
            email='owner@test.com',
            password='testpass123',
            first_name='Owner',
            last_name='User',
            role=User.EMPLOYEE
        )
        self.company = Company.objects.create(
            owner=self.company_owner,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='Test City',
            about='Test about',
            status=Company.PENDING
        )
        self.url = reverse('dashboard:company_approve', kwargs={'pk': self.company.pk})
    
    def test_updates_company_status(self):
        """Test that approving a company updates its status."""
        self.client.force_login(self.admin_user)
        
        # Approve the company
        response = self.client.post(self.url)
        
        # Verify status was updated
        self.company.refresh_from_db()
        self.assertEqual(self.company.status, Company.VERIFIED)
        
        # Verify redirect
        self.assertEqual(response.status_code, 302)
