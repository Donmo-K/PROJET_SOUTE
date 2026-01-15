from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import User, SellerProfile


# ────────────────────────────────────────────────
# Inline pour afficher le profil vendeur dans UserAdmin
# ────────────────────────────────────────────────
class SellerProfileInline(admin.StackedInline):
    model = SellerProfile
    can_delete = False
    verbose_name_plural = 'Profil vendeur'
    fields = (
        'phone_number', 'city',
        'identity_type', 'identity_number', 'identity_document',
        'ownership_type', 'ownership_document',
        'is_verified', 'verification_note', 'verified_at',
    )
    readonly_fields = ('created_at', 'verified_at')


# ────────────────────────────────────────────────
# Admin pour User (avec l’inline ci-dessus)
# ────────────────────────────────────────────────
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (SellerProfileInline,)  # ← maintenant c’est défini

    ordering = ('email',)
    list_display = (
        'email', 'full_name', 'role', 'is_approved',
        'email_verified', 'is_active', 'is_staff', 'is_superuser',
    )
    search_fields = ('email', 'full_name')
    list_filter = ('role', 'is_approved', 'email_verified', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('full_name', 'role')}),
        ('Validation vendeur', {'fields': ('is_approved',)}),
        ('Vérification email', {'fields': ('email_verified',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login',)}),
    )
    readonly_fields = ('last_login',)


# ────────────────────────────────────────────────
# Admin pour SellerProfile (avec actions)
# ────────────────────────────────────────────────
@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user_link', 'phone_number', 'city',
        'is_verified_colored', 'created_at'
    )
    list_filter = ('is_verified', 'identity_type', 'ownership_type', 'city')
    search_fields = ('user__email', 'phone_number', 'city')
    readonly_fields = ('created_at', 'verified_at')

    fieldsets = (
        ('Utilisateur', {'fields': ('user',)}),
        ('Coordonnées', {'fields': ('phone_number', 'city')}),
        ('Identité', {'fields': ('identity_type', 'identity_number', 'identity_document')}),
        ('Propriété', {'fields': ('ownership_type', 'ownership_document')}),
        ('Validation Admin', {'fields': ('is_verified', 'verification_note', 'verified_at')}),
        ('Dates', {'fields': ('created_at',)}),
    )

    actions = ['approve_seller', 'reject_seller']

    @admin.action(description="✅ Valider le(s) vendeur(s)")
    def approve_seller(self, request, queryset):
        for profile in queryset:
            profile.approve()
        self.message_user(request, f"{queryset.count()} vendeur(s) validé(s).")

    @admin.action(description="❌ Refuser le(s) vendeur(s)")
    def reject_seller(self, request, queryset):
        for profile in queryset:
            profile.reject("Refusé par l’administrateur")
        self.message_user(request, f"{queryset.count()} vendeur(s) refusé(s).")

    # Méthodes pour affichage joli
    def user_link(self, obj):
        url = reverse("admin:accounts_user_change", args=(obj.user.id,))
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = "Email"

    def is_verified_colored(self, obj):
        if obj.is_verified:
            return format_html('<span style="color:green">✓ Validé</span>')
        elif obj.verification_note:
            return format_html('<span style="color:red">✗ Refusé</span>')
        else:
            return format_html('<span style="color:orange">⌛ En attente</span>')
    is_verified_colored.short_description = "Statut"