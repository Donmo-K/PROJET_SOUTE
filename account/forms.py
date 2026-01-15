from django import forms
from django.core.exceptions import ValidationError
from .models import User, SellerProfile


# ────────────────────────────────────────────────
# Inscription utilisateur
# ────────────────────────────────────────────────
class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}),
        label="Mot de passe"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmer le mot de passe'}),
        label="Confirmation"
    )

    class Meta:
        model = User
        fields = ['email', 'full_name', 'role']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'exemple@domaine.com'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Nom complet'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("password_confirm"):
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


# ────────────────────────────────────────────────
# Dossier vendeur (après inscription)
# ────────────────────────────────────────────────
class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = [
            'phone_number', 'city',
            'identity_type', 'identity_number', 'identity_document',
            'ownership_type', 'ownership_document',
        ]
        labels = {
            'phone_number': 'Téléphone',
            'city': 'Ville',
            'identity_type': 'Type de pièce',
            'identity_number': 'Numéro pièce',
            'identity_document': 'Pièce d’identité (CNI/passeport)',
            'ownership_type': 'Type de propriété',
            'ownership_document': 'Preuve de propriété',
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': '+237 6XX XXX XXX'}),
            'city': forms.TextInput(attrs={'placeholder': 'Bafoussam, Douala...'}),
            'identity_document': forms.FileInput(attrs={'accept': 'image/*,application/pdf'}),
            'ownership_document': forms.FileInput(attrs={'accept': 'image/*,application/pdf'}),
        }

    def clean_identity_document(self):
        f = self.cleaned_data.get('identity_document')
        if f and f.size > 5*1024*1024:
            raise ValidationError("Fichier trop volumineux (max 5 Mo)")
        return f

    def clean_ownership_document(self):
        f = self.cleaned_data.get('ownership_document')
        if f and f.size > 10*1024*1024:
            raise ValidationError("Fichier trop volumineux (max 10 Mo)")
        return f