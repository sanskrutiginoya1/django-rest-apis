from .views import RegisterView, LogoutAPIView, VerifyEmail, LoginAPIView, SetNewPasswordAPIView, VerifyEmail, \
    LoginAPIView, RequestPasswordResetEmail, userProfileData
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from django.urls import path


# below is the url pattern for the users app
urlpatterns = [
    #path('demo/', demo.as_view(), name='demo' ),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('email-verify/', VerifyEmail.as_view(), name='email-verify'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(), name="request-reset-email"),
    #path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-complete/<uidb64>/<token>/', SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
    path('userprofile/', userProfileData.as_view(), name='userprofile')
]
