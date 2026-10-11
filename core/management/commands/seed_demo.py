"""
Management command to seed demo data for HireHub.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from accounts.models import JobSeekerProfile, Education, Experience
from companies.models import Company
from jobs.models import Job, Category, Skill
from applications.models import Application

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with demo data for development and testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting database seeding...'))
        
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Application.objects.all().delete()
        Job.objects.all().delete()
        Company.objects.all().delete()
        Experience.objects.all().delete()
        Education.objects.all().delete()
        JobSeekerProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Category.objects.all().delete()
        Skill.objects.all().delete()
        
        # Create admin
        self.stdout.write('Creating admin user...')
        admin, created = User.objects.get_or_create(
            email='admin@hirehub.local',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'role': User.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_email_verified': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        
        # Create categories
        self.stdout.write('Creating categories...')
        categories_data = [
            'Software Development',
            'Data Science',
            'Design',
            'Marketing',
            'Sales',
            'Finance',
            'Human Resources',
            'Customer Support',
            'Product Management',
            'Operations',
        ]
        categories = {}
        for name in categories_data:
            category = Category.objects.create(name=name)
            categories[name] = category
        
        # Create skills
        self.stdout.write('Creating skills...')
        skills_data = [
            'Python', 'JavaScript', 'React', 'Django', 'Node.js',
            'SQL', 'PostgreSQL', 'MongoDB', 'AWS', 'Docker',
            'Kubernetes', 'Git', 'REST API', 'GraphQL', 'TypeScript',
            'Vue.js', 'Angular', 'Java', 'C++', 'Go',
            'Machine Learning', 'Data Analysis', 'Pandas', 'NumPy', 'TensorFlow',
            'UI/UX Design', 'Figma', 'Adobe XD', 'Photoshop', 'SEO'
        ]
        skills = {}
        for skill_name in skills_data:
            skill = Skill.objects.create(name=skill_name)
            skills[skill_name] = skill
        
        # Create recruiters and companies
        self.stdout.write('Creating recruiters and companies...')
        companies_data = [
            {
                'name': 'TechCorp Solutions',
                'email': 'recruiter1@techcorp.com',
                'industry': 'technology',
                'size': '201-500',
                'location': 'San Francisco, CA',
                'about': 'Leading technology company specializing in cloud solutions and AI.',
                'website': 'https://techcorp.example.com'
            },
            {
                'name': 'Digital Innovations Inc',
                'email': 'recruiter2@digitalinnovations.com',
                'industry': 'technology',
                'size': '51-200',
                'location': 'New York, NY',
                'about': 'Innovative startup building next-generation web applications.',
                'website': 'https://digitalinnovations.example.com'
            }
        ]
        
        companies_list = []
        for company_data in companies_data:
            recruiter = User.objects.create_user(
                email=company_data['email'],
                password='recruiter123',
                first_name='Recruiter',
                last_name=company_data['name'].split()[0],
                role=User.EMPLOYEE
            )
            company = Company.objects.create(
                owner=recruiter,
                name=company_data['name'],
                industry=company_data['industry'],
                size=company_data['size'],
                location=company_data['location'],
                about=company_data['about'],
                website=company_data['website'],
                status=Company.VERIFIED
            )
            companies_list.append(company)
        
        # Create job seekers
        self.stdout.write('Creating job seekers...')
        seekers_data = [
            {
                'email': 'seeker1@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'headline': 'Full Stack Developer',
                'bio': 'Passionate developer with 3 years of experience in web development.',
                'location': 'San Francisco, CA'
            },
            {
                'email': 'seeker2@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'headline': 'Data Scientist',
                'bio': 'Experienced data scientist specializing in machine learning.',
                'location': 'New York, NY'
            },
            {
                'email': 'seeker3@example.com',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'headline': 'UX Designer',
                'bio': 'Creative designer with a focus on user experience.',
                'location': 'Austin, TX'
            },
            {
                'email': 'seeker4@example.com',
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'headline': 'Product Manager',
                'bio': 'Strategic product manager with 5+ years of experience.',
                'location': 'Seattle, WA'
            },
            {
                'email': 'seeker5@example.com',
                'first_name': 'David',
                'last_name': 'Brown',
                'headline': 'Backend Developer',
                'bio': 'Python expert specializing in scalable backend systems.',
                'location': 'Boston, MA'
            }
        ]
        
        seekers = []
        for seeker_data in seekers_data:
            seeker = User.objects.create_user(
                email=seeker_data['email'],
                password='seeker123',
                first_name=seeker_data['first_name'],
                last_name=seeker_data['last_name'],
                role=User.USER
            )
            profile = seeker.job_seeker_profile
            profile.headline = seeker_data['headline']
            profile.bio = seeker_data['bio']
            profile.location = seeker_data['location']
            profile.save()
            
            # Add education
            Education.objects.create(
                user=seeker,
                degree='Bachelor of Science',
                field_of_study='Computer Science',
                institution='University of California',
                start_date=timezone.now().date() - timedelta(days=1460),
                end_date=timezone.now().date() - timedelta(days=365)
            )
            
            # Add experience
            Experience.objects.create(
                user=seeker,
                title=seeker_data['headline'],
                company_name='Previous Company Inc',
                location=seeker_data['location'],
                start_date=timezone.now().date() - timedelta(days=1095),
                is_current=True,
                description='Working on various projects and technologies.'
            )
            
            seekers.append(seeker)
        
        # Create jobs
        self.stdout.write('Creating jobs...')
        job_types = ['FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP']
        
        jobs_list = []
        for i in range(25):
            company = random.choice(companies_list)
            category = random.choice(list(categories.values()))
            
            job = Job.objects.create(
                company=company,
                title=f'{category.name} Position {i+1}',
                description=f'Exciting opportunity for a {category.name} professional.',
                category=category,
                job_type=random.choice(job_types),
                location=company.location,
                salary_min=60000 + (i * 5000),
                salary_max=90000 + (i * 5000),
                deadline=timezone.now().date() + timedelta(days=30),
                is_active=True,
                is_approved=True
            )
            
            # Add random skills
            job_skills = random.sample(list(skills.values()), k=random.randint(3, 6))
            job.skills.set(job_skills)
            jobs_list.append(job)
        
        # Create applications
        self.stdout.write('Creating applications...')
        application_statuses = [
            Application.PENDING,
            Application.REVIEWING,
            Application.SHORTLISTED,
            Application.REJECTED,
            Application.WITHDRAWN
        ]
        
        for seeker in seekers:
            # Each seeker applies to 3-5 random jobs
            jobs_to_apply = random.sample(jobs_list, k=random.randint(3, 5))
            for job in jobs_to_apply:
                Application.objects.create(
                    job=job,
                    applicant=seeker,
                    cover_letter=f'I am very interested in the {job.title} position at {job.company.name}. '
                                f'My skills and experience make me a great fit for this role.',
                    status=random.choice(application_statuses),
                    applied_at=timezone.now() - timedelta(days=random.randint(1, 30))
                )
        
        self.stdout.write(self.style.SUCCESS('\n✓ Database seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS('\nDemo Accounts Created:'))
        self.stdout.write(f'  Admin: admin@hirehub.local / admin123')
        self.stdout.write(f'  Recruiter 1: recruiter1@techcorp.com / recruiter123')
        self.stdout.write(f'  Recruiter 2: recruiter2@digitalinnovations.com / recruiter123')
        self.stdout.write(f'  Job Seeker 1: seeker1@example.com / seeker123')
        self.stdout.write(f'  Job Seeker 2: seeker2@example.com / seeker123')
        self.stdout.write(f'  Job Seeker 3: seeker3@example.com / seeker123')
        self.stdout.write(f'  Job Seeker 4: seeker4@example.com / seeker123')
        self.stdout.write(f'  Job Seeker 5: seeker5@example.com / seeker123')
        self.stdout.write(f'\nCreated:')
        self.stdout.write(f'  - 1 Admin')
        self.stdout.write(f'  - 2 Companies (verified)')
        self.stdout.write(f'  - 5 Job Seekers with profiles')
        self.stdout.write(f'  - 10 Categories')
        self.stdout.write(f'  - 30 Skills')
        self.stdout.write(f'  - 25 Jobs')
        self.stdout.write(f'  - ~{Application.objects.count()} Applications in various statuses')
