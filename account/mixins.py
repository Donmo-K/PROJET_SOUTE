from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy

class SellerApprovedRequiredMixin(AccessMixin):
    """
    Mixin qui restreint l'accès aux vendeurs validés par l'admin.
    Ordre des vérifications : auth → rôle → email vérifié → profil approuvé.
    """
    login_url = reverse_lazy('account:login')  # ← change selon ton namespace
    permission_denied_message = "Accès refusé : droits insuffisants."

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # 1. Non connecté
        if not user.is_authenticated:
            return self.handle_no_permission()

        # 2. Pas propriétaire
        if user.role != 'proprietaire':
            messages.error(request, "Accès réservé aux vendeurs/propriétaires.")
            return redirect('annonces:list')  # ou 'home'

        # 3. Email non vérifié (sauf si déjà sur la page de vérif)
        if not user.email_verified and request.resolver_match.url_name != 'verify-email':
            messages.warning(request, "Veuillez vérifier votre adresse email pour continuer.")
            return redirect('account:verify-email')

        # 4. Vendeur non approuvé (sauf si déjà sur la page pending)
        if not user.is_approved and request.resolver_match.url_name != 'seller-pending':
            messages.warning(
                request,
                "Votre dossier vendeur est en cours de validation par notre équipe."
            )
            return redirect('seller:pending')

        return super().dispatch(request, *args, **kwargs)