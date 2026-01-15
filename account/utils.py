import random
import string
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.hashers import make_password


def generate_verification_code(length=6):
    """
    Génère un code numérique de 6 chiffres par défaut.
    On peut facilement passer à alphanumérique si besoin.
    """
    return ''.join(random.choices(string.digits, k=length))


def generate_and_send_email_code(user, code_length=6, validity_minutes=10):
    """
    Génère un code de vérification, le hashe, l'enregistre sur l'utilisateur
    et envoie le code par email.
    
    Args:
        user: instance de User
        code_length: longueur du code (défaut 6)
        validity_minutes: durée de validité en minutes (défaut 10)
    
    Returns:
        str: le code en clair (uniquement pour les tests ou logs internes – ne jamais renvoyer au client)
    """
    # Génération du code
    code = generate_verification_code(code_length)

    # Hashage sécurisé (comme un mot de passe)
    user.email_code_hash = make_password(code)

    # Horodatage création + expiration
    now = timezone.now()
    user.email_code_created_at = now
    user.email_code_expires_at = now + timedelta(minutes=validity_minutes)  # ← champ à ajouter dans le modèle si absent

    # Réinitialisation des tentatives
    user.email_code_attempts = 0

    user.save(
        update_fields=[
            'email_code_hash',
            'email_code_created_at',
            'email_code_expires_at',
            'email_code_attempts'
        ]
    )

    # Envoi de l'email
    subject = "Votre code de vérification - Immobilier"
    message = (
        f"Bonjour {user.full_name},\n\n"
        f"Votre code de vérification est : **{code}**\n\n"
        f"Ce code est valable {validity_minutes} minutes.\n"
        f"Ne le partagez avec personne.\n\n"
        f"Cordialement,\nL'équipe Immobilier"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,  # ← recommandé au lieu de hardcoder
            recipient_list=[user.email],
            fail_silently=False,                    # ← pour voir les erreurs en développement
        )
    except Exception as e:
        # En production, logger l'erreur plutôt que planter
        # Pour le développement, on peut laisser remonter
        raise Exception(f"Échec envoi email → {str(e)}")

    # Pour debug / tests uniquement (à supprimer ou logger en prod)
    # print(f"Code envoyé à {user.email} : {code}")

    return code  # uniquement pour tests ou debug – ne jamais exposer