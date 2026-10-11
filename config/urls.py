"""
URL configuration for HireHub project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('django-admin/', admin.site.urls),
    
    # Core app
    path('', include('core.urls')),
    
    # Accounts app
    path('accounts/', include('accounts.urls')),
    
    # Companies app
    path('companies/', include('companies.urls')),
    
    # Jobs app
    path('jobs/', include('jobs.urls')),
    
    # Applications app
    path('applications/', include('applications.urls')),
    
    # Notifications app
    path('notifications/', include('notifications.urls')),
    
    # Dashboard app
    path('employee/', include('dashboard.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
