# account/urls.py

from django.urls import path
from .views import (
    RegisterView,           
    LoginView,
    LogoutView,
    RedirectAfterLoginView,
    VerifyEmailView,
    ResendCodeView,
    SellerProfileCreateView,
)

app_name = 'account'  # très important pour les reverse('account:xxx')

urlpatterns = [
    # AUTHENTIFICATION
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # REDIRECTION INTELLIGENTE APRÈS CONNEXION
    path('redirect-after-login/', RedirectAfterLoginView.as_view(), name='redirect-after-login'),

    # VÉRIFICATION EMAIL
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-code/', ResendCodeView.as_view(), name='resend-code'),

    # PROFIL VENDEUR (soumission dossier)
    path('seller/profile/create/', SellerProfileCreateView.as_view(), name='seller-profile-create'),
]