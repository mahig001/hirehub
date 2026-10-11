from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Registration & Login
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Email verification
    path('verify/<str:token>/', views.VerifyEmailView.as_view(), name='verify_email'),
    
    # Profile management
    path('profile/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/resume/upload/', views.ResumeUploadView.as_view(), name='resume_upload'),
    path('profile/resume/download/<int:user_id>/', views.ResumeDownloadView.as_view(), name='resume_download'),
    path('delete/', views.DeleteAccountView.as_view(), name='delete_account'),
    
    # Education CRUD
    path('education/add/', views.EducationCreateView.as_view(), name='education_create'),
    path('education/<int:pk>/edit/', views.EducationUpdateView.as_view(), name='education_update'),
    path('education/<int:pk>/delete/', views.EducationDeleteView.as_view(), name='education_delete'),
    
    # Experience CRUD
    path('experience/add/', views.ExperienceCreateView.as_view(), name='experience_create'),
    path('experience/<int:pk>/edit/', views.ExperienceUpdateView.as_view(), name='experience_update'),
    path('experience/<int:pk>/delete/', views.ExperienceDeleteView.as_view(), name='experience_delete'),
    
    # Saved jobs
    path('saved-jobs/', views.SavedJobsListView.as_view(), name='saved_jobs'),
    path('jobs/<int:pk>/toggle-save/', views.toggle_saved_job, name='toggle_saved_job'),
    
    # Password reset
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Password change
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
]
