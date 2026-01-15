from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class CreateAnnonceView(LoginRequiredMixin, View):
    login_url = '/account/login/'

    def dispatch(self, request, *args, **kwargs):

        # 1️⃣ Pas propriétaire → interdit
        if request.user.role != 'proprietaire':
            return redirect('/annonces/')

        # 2️⃣ Propriétaire non approuvé par admin
        if not request.user.is_approved:
            return redirect('/seller/pending/')

        # 3️⃣ Profil vendeur non vérifié
        if not request.user.seller_profile.is_verified:
            return redirect('/seller/pending/')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("Formulaire de publication d’annonce")
