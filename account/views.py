from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import check_password

from .forms import RegisterForm, SellerProfileForm
from .models import SellerProfile
from .utils import generate_and_send_email_code

User = get_user_model()

# =====================================================================
# INSCRIPTION
# =====================================================================
@never_cache
class RegisterView(View):  # ← corrigé : RegisterViewTest → RegisterView (ton nom original)
    template_name = 'account/register.html'

    def get(self, request):
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            generate_and_send_email_code(user)
            login(request, user)  # OK, pas besoin de forcer le backend
            messages.success(request, "Inscription réussie ! Vérifiez votre email.")
            return redirect('account:verify-email')
        messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
        return render(request, self.template_name, {'form': form})

# =====================================================================
# CONNEXION
# =====================================================================
@never_cache
class LoginView(View):
    template_name = 'account/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return render(request, self.template_name)

        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "Connexion réussie.")
                return redirect('account:redirect-after-login')
            else:
                messages.error(request, "Votre compte est désactivé.")
        else:
            messages.error(request, "Email ou mot de passe incorrect.")
        return render(request, self.template_name)

# =====================================================================
# DÉCONNEXION
# =====================================================================
class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "Vous avez été déconnecté.")
        return redirect('account:login')

# =====================================================================
# REDIRECTION INTELLIGENTE APRÈS CONNEXION
# =====================================================================
class RedirectAfterLoginView(LoginRequiredMixin, View):
    login_url = reverse_lazy('account:login')

    def get(self, request):
        user = request.user
        if not user.email_verified:
            messages.warning(request, "Veuillez vérifier votre adresse email.")
            return redirect('account:verify-email')
        if user.is_superuser:
            return redirect('admin:index')
        if user.role == 'proprietaire':
            if not user.is_approved:
                messages.info(request, "Votre dossier vendeur est en cours de validation.")
                return redirect('account:seller-pending')  # ← OK avec namespace account
            return redirect('account:seller-dashboard')  # ← à définir plus tard
        # Par défaut acheteur
        return redirect('annonces:liste')  # ← adapte selon tes URLs

# =====================================================================
# CRÉATION / SOUMISSION DU DOSSIER VENDEUR
# =====================================================================
class SellerProfileCreateView(LoginRequiredMixin, View):
    login_url = reverse_lazy('account:login')
    template_name = 'account/seller_profile_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'proprietaire':
            messages.error(request, "Cette section est réservée aux propriétaires.")
            return redirect('annonces:liste')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        if hasattr(request.user, 'seller_profile'):
            messages.info(request, "Vous avez déjà soumis votre dossier vendeur.")
            return redirect('account:seller-pending')
        form = SellerProfileForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SellerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Votre dossier a été soumis avec succès. En attente de validation.")
            return redirect('account:seller-pending')
        messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
        return render(request, self.template_name, {'form': form})

# =====================================================================
# VÉRIFICATION EMAIL (CODE)
# =====================================================================
class VerifyEmailView(LoginRequiredMixin, View):
    login_url = reverse_lazy('account:login')
    template_name = 'account/verify_email.html'

    def get(self, request):
        if request.user.email_verified:
            messages.info(request, "Votre email est déjà vérifié.")
            return redirect('account:redirect-after-login')
        return render(request, self.template_name)

    def post(self, request):
        user = request.user
        code = request.POST.get('code', '').strip()
        if not code:
            messages.error(request, "Veuillez entrer le code reçu.")
            return render(request, self.template_name)
        if not user.email_code_hash or not user.email_code_created_at:
            messages.error(request, "Aucun code actif. Demandez-en un nouveau.")
            return redirect('account:resend-code')
        # Expiration
        if timezone.now() > user.email_code_created_at + timedelta(minutes=10):
            messages.error(request, "Ce code a expiré.")
            return redirect('account:resend-code')
        # Vérification sécurisée
        if check_password(code, user.email_code_hash):
            user.email_verified = True
            user.email_code_hash = None
            user.email_code_created_at = None
            user.email_code_attempts = 0
            user.save(update_fields=[
                'email_verified', 'email_code_hash',
                'email_code_created_at', 'email_code_attempts'
            ])
            messages.success(request, "Votre email a été vérifié avec succès !")
            return redirect('account:redirect-after-login')
        else:
            user.email_code_attempts = (user.email_code_attempts or 0) + 1
            user.save(update_fields=['email_code_attempts'])
            if user.email_code_attempts >= 5:
                messages.error(request, "Trop de tentatives. Veuillez demander un nouveau code.")
                return redirect('account:resend-code')
            messages.error(request, f"Code incorrect ({user.email_code_attempts}/5 tentatives).")
            return render(request, self.template_name)

# =====================================================================
# RENVOI DU CODE DE VÉRIFICATION
# =====================================================================
class ResendCodeView(LoginRequiredMixin, View):
    login_url = reverse_lazy('account:login')

    def get(self, request):
        user = request.user
        if user.email_verified:
            messages.info(request, "Votre email est déjà vérifié.")
            return redirect('account:redirect-after-login')
        generate_and_send_email_code(user)
        messages.success(request, "Un nouveau code vous a été envoyé par email.")
        return redirect('account:verify-email')