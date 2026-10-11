from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from companies.models import Company
from jobs.models import Category, Skill, Job


class Command(BaseCommand):
    help = 'Seed data for Phase 2: Categories, Skills, Companies, and Jobs'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Phase 2 data...')

        # Create categories
        categories_data = [
            'Technology',
            'Healthcare',
            'Finance',
        ]
        categories = {}
        for cat_name in categories_data:
            category, created = Category.objects.get_or_create(name=cat_name)
            categories[cat_name] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {cat_name}'))

        # Create skills
        skills_data = [
            'Python', 'Django', 'React', 'JavaScript', 'SQL',
            'AWS', 'Docker', 'Git', 'REST APIs', 'PostgreSQL'
        ]
        skills = {}
        for skill_name in skills_data:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            skills[skill_name] = skill
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created skill: {skill_name}'))

        # Create employee users for companies
        employee1, created = User.objects.get_or_create(
            email='recruiter1@techcorp.com',
            defaults={
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'role': User.EMPLOYEE,
                'is_active': True,
                'is_email_verified': True,
            }
        )
        if created:
            employee1.set_password('password123')
            employee1.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {employee1.email}'))

        employee2, created = User.objects.get_or_create(
            email='recruiter2@healthplus.com',
            defaults={
                'first_name': 'Bob',
                'last_name': 'Smith',
                'role': User.EMPLOYEE,
                'is_active': True,
                'is_email_verified': True,
            }
        )
        if created:
            employee2.set_password('password123')
            employee2.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {employee2.email}'))

        # Create companies
        company1, created = Company.objects.get_or_create(
            owner=employee1,
            defaults={
                'name': 'TechCorp Solutions',
                'industry': 'technology',
                'size': '201-500',
                'location': 'San Francisco, CA',
                'about': 'TechCorp Solutions is a leading software development company specializing in cloud-based enterprise solutions. We help businesses transform digitally with cutting-edge technology.',
                'website': 'https://techcorp.example.com',
                'status': Company.VERIFIED,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created company: {company1.name}'))

        company2, created = Company.objects.get_or_create(
            owner=employee2,
            defaults={
                'name': 'HealthPlus Medical',
                'industry': 'healthcare',
                'size': '51-200',
                'location': 'New York, NY',
                'about': 'HealthPlus Medical is committed to improving healthcare through innovative technology solutions and compassionate care.',
                'website': 'https://healthplus.example.com',
                'status': Company.PENDING,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created company: {company2.name}'))

        # Create jobs
        jobs_data = [
            {
                'company': company1,
                'title': 'Senior Python Developer',
                'description': 'We are looking for an experienced Python developer to join our backend team. You will work on building scalable microservices and APIs using Django and FastAPI.\n\nResponsibilities:\n- Design and develop RESTful APIs\n- Write clean, maintainable code\n- Collaborate with frontend developers\n- Optimize application performance\n\nRequirements:\n- 5+ years of Python experience\n- Strong knowledge of Django\n- Experience with PostgreSQL\n- Familiarity with AWS services',
                'category': categories['Technology'],
                'skills': ['Python', 'Django', 'PostgreSQL', 'AWS', 'REST APIs'],
                'location': 'San Francisco, CA',
                'job_type': Job.FULL_TIME,
                'salary_min': 120000,
                'salary_max': 160000,
                'is_active': True,
                'is_approved': True,
            },
            {
                'company': company1,
                'title': 'Frontend React Developer',
                'description': 'Join our frontend team to build beautiful, responsive web applications using React and modern JavaScript frameworks.\n\nResponsibilities:\n- Develop user interfaces using React\n- Implement responsive designs\n- Integrate with backend APIs\n- Write unit tests\n\nRequirements:\n- 3+ years of React experience\n- Strong JavaScript/TypeScript skills\n- Knowledge of HTML5/CSS3\n- Experience with Git',
                'category': categories['Technology'],
                'skills': ['React', 'JavaScript', 'Git', 'REST APIs'],
                'location': 'Remote',
                'job_type': Job.FULL_TIME,
                'salary_min': 90000,
                'salary_max': 130000,
                'is_active': True,
                'is_approved': True,
            },
            {
                'company': company1,
                'title': 'DevOps Engineer',
                'description': 'We need a skilled DevOps engineer to manage our cloud infrastructure and CI/CD pipelines.\n\nResponsibilities:\n- Maintain AWS infrastructure\n- Build and improve CI/CD pipelines\n- Monitor system performance\n- Automate deployment processes\n\nRequirements:\n- Experience with AWS\n- Strong Docker/Kubernetes knowledge\n- Familiarity with Terraform\n- Scripting skills (Python/Bash)',
                'category': categories['Technology'],
                'skills': ['AWS', 'Docker', 'Python', 'Git'],
                'location': 'San Francisco, CA',
                'job_type': Job.FULL_TIME,
                'salary_min': 110000,
                'salary_max': 150000,
                'is_active': True,
                'is_approved': True,
            },
            {
                'company': company2,
                'title': 'Healthcare IT Specialist',
                'description': 'HealthPlus Medical is seeking an IT specialist with healthcare industry experience to support our clinical systems.\n\nResponsibilities:\n- Support electronic health record systems\n- Troubleshoot technical issues\n- Train staff on new systems\n- Ensure HIPAA compliance\n\nRequirements:\n- Healthcare IT experience\n- Knowledge of EHR systems\n- Strong communication skills\n- Understanding of HIPAA regulations',
                'category': categories['Healthcare'],
                'skills': ['SQL', 'Python'],
                'location': 'New York, NY',
                'job_type': Job.FULL_TIME,
                'salary_min': 65000,
                'salary_max': 85000,
                'is_active': True,
                'is_approved': False,
            },
            {
                'company': company1,
                'title': 'Software Engineering Intern',
                'description': 'Summer internship opportunity for computer science students. Work on real projects with our development team.\n\nResponsibilities:\n- Contribute to ongoing projects\n- Learn from senior developers\n- Participate in code reviews\n- Write documentation\n\nRequirements:\n- Currently pursuing CS degree\n- Basic programming knowledge\n- Eagerness to learn\n- Good problem-solving skills',
                'category': categories['Technology'],
                'skills': ['Python', 'JavaScript', 'Git'],
                'location': 'San Francisco, CA',
                'job_type': Job.INTERNSHIP,
                'salary_min': 25,
                'salary_max': 35,
                'is_active': True,
                'is_approved': True,
                'deadline': timezone.now().date() + timedelta(days=30),
            },
        ]

        for job_data in jobs_data:
            skill_names = job_data.pop('skills')
            job, created = Job.objects.get_or_create(
                company=job_data['company'],
                title=job_data['title'],
                defaults=job_data
            )
            if created:
                # Add skills
                for skill_name in skill_names:
                    job.skills.add(skills[skill_name])
                self.stdout.write(self.style.SUCCESS(f'Created job: {job.title}'))

        self.stdout.write(self.style.SUCCESS('\nPhase 2 data seeding completed!'))
        self.stdout.write(self.style.SUCCESS(f'Categories: {Category.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Skills: {Skill.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Companies: {Company.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Jobs: {Job.objects.count()}'))
