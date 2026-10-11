from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms_of_service'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]
