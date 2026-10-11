from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from .forms import ContactForm
from .models import ContactMessage


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


class ContactView(FormView):
    """Contact page view with form."""
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = '/contact/'
    
    def form_valid(self, form):
        # Save contact message
        ContactMessage.objects.create(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            subject=form.cleaned_data['subject'],
            message=form.cleaned_data['message']
        )
        messages.success(self.request, 'Your message has been sent successfully. We will get back to you soon.')
        return super().form_valid(form)


class FAQView(TemplateView):
    """FAQ page view."""
    template_name = 'core/faq.html'


class PrivacyPolicyView(TemplateView):
    """Privacy policy page view."""
    template_name = 'core/privacy_policy.html'


class TermsOfServiceView(TemplateView):
    """Terms of service page view."""
    template_name = 'core/terms_of_service.html'
