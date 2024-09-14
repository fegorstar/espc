from django.urls import path
from . import views


urlpatterns = [

    # User Profile Management URLs
    path('profile/update/', views.ProfileUpdateAPIView.as_view(),
         name='profile-update'),
    path('profile/details/', views.ProfileDetailAPIView.as_view(),
         name='profile-detail'),
    path('email/change/', views.EmailChangeAPIView.as_view(), name='email_change'),
    path('password/change/', views.PasswordChangeAPIView.as_view(),
         name='password_change'),
    path('deactivate/<int:user_id>/',
         views.DeactivateAccountAPIView.as_view(), name='deactivate_account'),

]
