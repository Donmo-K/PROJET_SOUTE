from django.http import HttpResponse
from django.views import View
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin


class AnnoncesView(View):
    def get(self, request):
        return HttpResponse("Page des annonces (Acheteur)")


class SellerPendingView(View):
    def get(self, request):
        return HttpResponse("Votre compte vendeur est en attente de validation")


class AdminDashboardView(LoginRequiredMixin, View):
    login_url = '/account/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('/annonces/')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("Dashboard Admin")
