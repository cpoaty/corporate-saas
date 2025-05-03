"""
Configuration de l'interface d'administration pour les tiers
"""
from django.contrib import admin
from ..models.tiers import Tiers

@admin.register(Tiers)
class TiersAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour les tiers"""
    list_display = ('code', 'name', 'type', 'format_account', 'is_active', 'tenant_id')
    list_filter = ('type', 'is_active')
    search_fields = ('code', 'name', 'email', 'tax_id')
    readonly_fields = ('id', 'created_at', 'updated_at')

    def format_account(self, obj):
        if obj.account:
            account_str = str(obj.account)
            if " - " in account_str:
                return account_str.split(" - ")[0]
            return account_str
        return "-"
    format_account.short_description = "Account"  # Titre de la colonne

    # Modifier le message d'aide pour le champ code
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['code'].help_text = (
            "Le code doit commencer par le préfixe du compte collectif "
            "(401 pour fournisseurs, 411 pour clients, 422 pour personnel) "
            "suivi des trois premières lettres du nom. Exemple: 401ABC pour 'ABC Transport'."
        )
        return form
    
    fieldsets = (
        (None, {
            'fields': ('id', 'tenant_id', 'code', 'name', 'type', 'account')
        }),
        ('Informations de contact', {
            'fields': ('address', 'email', 'phone', 'tax_id')
        }),
        ('Paramètres', {
            'fields': ('is_active', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    class Media:
        js = ('/static/js/tiers_admin.js',)  # Chemin absolu