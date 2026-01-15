from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import UserManager
from django.conf import settings
from django.utils import timezone


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('acheteur', 'Acheteur'),
        ('proprietaire', 'Propriétaire'),
        ('admin', 'Administrateur'),           # ← ajouté
    )

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)        # validation vendeur
    email_verified = models.BooleanField(default=False)

    # Code email
    email_code_hash = models.CharField(max_length=128, null=True, blank=True)
    email_code_created_at = models.DateTimeField(null=True, blank=True)
    email_code_expires_at = models.DateTimeField(null=True, blank=True)     # ← ajouté
    email_code_attempts = models.PositiveIntegerField(default=0)
    email_code_last_sent = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'role']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class SellerProfile(models.Model):
    # ────────────────────────────────────────────────
    # Constantes CHOICES (à mettre AVANT les champs qui les utilisent)
    # ────────────────────────────────────────────────
    IDENTITY_CHOICES = (
        ('cni', 'Carte Nationale d’Identité'),
        ('passport', 'Passeport'),
        ('driver_license', 'Permis de conduire'),  # optionnel, tu peux ajouter
    )

    OWNERSHIP_CHOICES = (
        ('owner', 'Propriétaire direct'),
        ('mandate', 'Mandataire'),
        ('other', 'Autre'),
    )

    # Maintenant tu peux utiliser ces constantes
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_profile'
    )

    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100)

    identity_type = models.CharField(
        max_length=20,
        choices=IDENTITY_CHOICES,
        default='cni',               # ← c’est une bonne idée d’ajouter un default
    )
    
    identity_number = models.CharField(max_length=100)
    identity_document = models.FileField(upload_to='identity_docs/')

    ownership_type = models.CharField(
        max_length=20,
        choices=OWNERSHIP_CHOICES,
        default='owner',
    )
    ownership_document = models.FileField(upload_to='ownership_docs/')

    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dossier vendeur - {self.user.email}"