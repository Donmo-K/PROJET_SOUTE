from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, role, password=None, **extra_fields):
        """
        Crée et sauvegarde un utilisateur avec l'email, le nom complet et le rôle.
        """
        if not email:
            raise ValueError(_("L'email est obligatoire"))

        email = self.normalize_email(email)

        # Validation optionnelle du rôle
        valid_roles = dict(self.model.ROLE_CHOICES).keys()
        if role not in valid_roles:
            raise ValueError(_(f"Rôle invalide. Valeurs possibles : {', '.join(valid_roles)}"))

        user = self.model(
            email=email,
            full_name=full_name,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        """
        Crée et sauvegarde un superutilisateur (admin).
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('email_verified', True)  # souvent on considère l'admin comme vérifié

        # Forcer le rôle admin pour les superusers
        if extra_fields.get('role') and extra_fields['role'] != 'admin':
            raise ValueError(_("Le superuser doit avoir le rôle 'admin'"))
        
        extra_fields['role'] = 'admin'

        return self.create_user(
            email=email,
            full_name=full_name,
            role='admin',
            password=password,
            **extra_fields
        )