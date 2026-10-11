from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Company, Employee

User = get_user_model()


class CompanyModelTests(TestCase):
    """Tests for Company model."""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='testpass123',
            role=User.EMPLOYEE
        )
    
    def test_slug_generated_on_creation(self):
        """Test that slug is automatically generated from name."""
        company = Company.objects.create(
            owner=self.owner,
            name='Test Company Inc',
            industry='technology',
            size='11-50',
            location='San Francisco',
            about='Test company description'
        )
        self.assertEqual(company.slug, 'test-company-inc')
    
    def test_unique_slug_generation(self):
        """Test that unique slugs are generated for duplicate names."""
        company1 = Company.objects.create(
            owner=self.owner,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='San Francisco',
            about='First company'
        )
        
        owner2 = User.objects.create_user(
            email='owner2@test.com',
            password='testpass123',
            role=User.EMPLOYEE
        )
        
        company2 = Company.objects.create(
            owner=owner2,
            name='Test Company',
            industry='finance',
            size='51-200',
            location='New York',
            about='Second company'
        )
        
        self.assertEqual(company1.slug, 'test-company')
        self.assertEqual(company2.slug, 'test-company-1')
    
    def test_company_str_representation(self):
        """Test company string representation."""
        company = Company.objects.create(
            owner=self.owner,
            name='Acme Corp',
            industry='technology',
            size='11-50',
            location='San Francisco',
            about='Test'
        )
        self.assertEqual(str(company), 'Acme Corp')
    
    def test_can_post_jobs_verified(self):
        """Test that verified companies can post jobs."""
        company = Company.objects.create(
            owner=self.owner,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='San Francisco',
            about='Test',
            status=Company.VERIFIED
        )
        self.assertTrue(company.can_post_jobs())
    
    def test_can_post_jobs_pending(self):
        """Test that pending companies can post jobs."""
        company = Company.objects.create(
            owner=self.owner,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='San Francisco',
            about='Test',
            status=Company.PENDING
        )
        self.assertTrue(company.can_post_jobs())
    
    def test_cannot_post_jobs_suspended(self):
        """Test that suspended companies cannot post jobs."""
        company = Company.objects.create(
            owner=self.owner,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='San Francisco',
            about='Test',
            status=Company.SUSPENDED
        )
        self.assertFalse(company.can_post_jobs())


class EmployeeModelTests(TestCase):
    """Tests for Employee model."""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='testpass123',
            role=User.EMPLOYEE
        )
        self.company = Company.objects.create(
            owner=self.owner,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='San Francisco',
            about='Test'
        )
    
    def test_employee_creation(self):
        """Test employee creation and relationship."""
        employee_user = User.objects.create_user(
            email='employee@test.com',
            password='testpass123',
            role=User.EMPLOYEE
        )
        
        employee = Employee.objects.create(
            user=employee_user,
            company=self.company,
            position='HR Manager',
            is_primary=False
        )
        
        self.assertEqual(employee.company, self.company)
        self.assertEqual(employee.user, employee_user)
        self.assertEqual(employee.position, 'HR Manager')
        self.assertFalse(employee.is_primary)
    
    def test_employee_str_representation(self):
        """Test employee string representation."""
        employee_user = User.objects.create_user(
            email='employee@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role=User.EMPLOYEE
        )
        
        employee = Employee.objects.create(
            user=employee_user,
            company=self.company,
            position='Manager'
        )
        
        self.assertEqual(str(employee), f'John Doe at {self.company.name}')


class CompanyCreateViewTests(TestCase):
    """Tests for company creation view."""
    
    def setUp(self):
        self.client = Client()
        self.employee = User.objects.create_user(
            email='employee@test.com',
            password='testpass123',
            role=User.EMPLOYEE
        )
        self.job_seeker = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            role=User.USER
        )
        self.url = reverse('companies:create')
    
    def test_create_company_requires_employee_role(self):
        """Test that only EMPLOYEE role can create company."""
        self.client.force_login(self.job_seeker)
        response = self.client.get(self.url)
        # Should redirect or return 403
        self.assertIn(response.status_code, [302, 403])
    
    def test_create_company_success(self):
        """Test successful company creation."""
        self.client.force_login(self.employee)
        
        data = {
            'name': 'New Company',
            'industry': 'technology',
            'size': '11-50',
            'location': 'San Francisco',
            'about': 'A new technology company',
            'website': 'https://newcompany.com'
        }
        
        response = self.client.post(self.url, data)
        
        # Check company was created
        self.assertTrue(Company.objects.filter(name='New Company').exists())
        company = Company.objects.get(name='New Company')
        self.assertEqual(company.owner, self.employee)
        self.assertEqual(company.status, Company.PENDING)


class CompanyListViewTests(TestCase):
    """Tests for company list view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            role=User.USER
        )
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='testpass123',
            role=User.EMPLOYEE
        )
        self.company = Company.objects.create(
            owner=self.owner,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='San Francisco',
            about='Test',
            status=Company.VERIFIED
        )
        self.url = reverse('companies:list')
    
    def test_company_list_accessible_to_authenticated_users(self):
        """Test that authenticated users can access company list."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


# Create your tests here.

