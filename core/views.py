from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Home page view."""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Will add statistics and featured jobs later
        return context


class AboutView(TemplateView):
    """About page view."""
    template_name = 'core/about.html'


class ContactView(TemplateView):
    """Contact page view."""
    template_name = 'core/contact.html'


class FAQView(TemplateView):
    """FAQ page view."""
    template_name = 'core/faq.html'


class PrivacyPolicyView(TemplateView):
    """Privacy policy page view."""
    template_name = 'core/privacy_policy.html'


class TermsOfServiceView(TemplateView):
    """Terms of service page view."""
    template_name = 'core/terms_of_service.html'
