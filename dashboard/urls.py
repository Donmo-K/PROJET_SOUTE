from django.urls import path
from .views import VendeurDashboardView
from .views import AcheteurDashboardView
from .views import AdminDashboardView



urlpatterns = [
    path('vendeur/', VendeurDashboardView.as_view(), name='vendeur_dashboard'),

     path('acheteur/', AcheteurDashboardView.as_view(), name='acheteur_dashboard'),

      path('admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
]
