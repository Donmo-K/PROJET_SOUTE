from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from account.models import SellerProfile

User = get_user_model()


class VendeurDashboardView(LoginRequiredMixin, TemplateView):
    """
    Tableau de bord du vendeur (propriétaire).
    Accessible uniquement aux utilisateurs avec rôle 'proprietaire'.
    """
    template_name = 'dashboard/vendeur.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        
        if request.user.role != 'proprietaire':
            return HttpResponseForbidden("Accès réservé aux vendeurs.")
        
        # Option : bloquer si non approuvé (plus strict)
        if not request.user.is_approved:
            return HttpResponseForbidden("Votre compte vendeur n’est pas encore validé.")
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        seller_profile = getattr(user, 'seller_profile', None)

        context.update({
            'user': user,
            'seller_profile': seller_profile,
            'is_verified_seller': seller_profile.is_verified if seller_profile else False,
            # À compléter plus tard : annonces publiées, demandes de contact, etc.
            # 'mes_annonces': Annonce.objects.filter(vendeur=user),
            # 'demandes_contact': ContactRequest.objects.filter(annonce__vendeur=user),
        })
        return context


class AcheteurDashboardView(LoginRequiredMixin, TemplateView):
    """
    Tableau de bord de l'acheteur.
    Accessible uniquement aux utilisateurs avec rôle 'acheteur'.
    """
    template_name = 'dashboard/acheteur.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'acheteur':
            return HttpResponseForbidden("Accès réservé aux acheteurs.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            'user': user,
            # À compléter : favoris, annonces vues, demandes de contact envoyées, etc.
            # 'favoris': Favori.objects.filter(user=user),
        })
        return context


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Tableau de bord administrateur.
    Accessible uniquement aux staff / superusers.
    """
    template_name = 'dashboard/admin.html'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        return HttpResponseForbidden("Accès réservé aux administrateurs.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistiques globales
        total_users = User.objects.count()
        acheteurs = User.objects.filter(role='acheteur').count()
        vendeurs = User.objects.filter(role='proprietaire').count()
        vendeurs_valides = User.objects.filter(role='proprietaire', is_approved=True).count()
        vendeurs_en_attente = User.objects.filter(role='proprietaire', is_approved=False).count()
        total_dossiers = SellerProfile.objects.count()

        context.update({
            'total_users': total_users,
            'acheteurs': acheteurs,
            'vendeurs': vendeurs,
            'vendeurs_valides': vendeurs_valides,
            'vendeurs_en_attente': vendeurs_en_attente,
            'total_dossiers': total_dossiers,
            'pourcentage_vendeurs_valides': round((vendeurs_valides / vendeurs * 100) if vendeurs else 0, 1),
            # À compléter plus tard :
            # 'annonces_total': Annonce.objects.count(),
            # 'annonces_publiees': Annonce.objects.filter(est_publiee=True).count(),
            # 'demandes_contact': ContactRequest.objects.count(),
        })
        return context