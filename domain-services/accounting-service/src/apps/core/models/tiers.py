"""
Modèle pour la gestion des tiers (clients, fournisseurs, etc.)
"""
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from .account import Account
from ..utils import format_accounting_name, format_accounting_code

class Tiers(models.Model):
    """
    Représente un tiers (client, fournisseur, employé, etc.) dans le système comptable.
    Les tiers sont associés aux comptes de la classe 4 du plan comptable OHADA.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(null=True, blank=True)  # ID du tenant pour isolation

    # Définir une constante pour la longueur du code
    CODE_LENGTH = 6  # Longueur souhaitée pour le code
    
    code = models.CharField(
        max_length=20, 
        help_text=f"Code unique du tiers (sera formaté en majuscules et complété jusqu'à {CODE_LENGTH} caractères)"
    )
    name = models.CharField(max_length=200, help_text="Nom ou raison sociale du tiers")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='tiers',
                               help_text="Compte comptable associé au tiers")
    
    # Type de tiers
    TYPE_CHOICES = [
        ('CUSTOMER', 'Client'),
        ('SUPPLIER', 'Fournisseur'),
        ('EMPLOYEE', 'Employé'),
        ('OTHER', 'Autre'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Informations supplémentaires
    address = models.TextField(blank=True, null=True, help_text="Adresse complète")
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True, help_text="Numéro d'identification fiscale")
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True, help_text="Notes et informations additionnelles")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tiers"
        verbose_name_plural = "Tiers"
        unique_together = [['tenant_id', 'code']]
        ordering = ['code', 'name']
        
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def clean(self):
        """Validation des données avant sauvegarde"""
        super().clean()
        
        # Vérifier que le compte est bien un compte de tiers (classe 4)
        if self.account and self.account.account_class.number != 4:
            raise ValidationError({
                'account': f"Le compte doit être un compte de tiers (classe 4), "
                          f"pas un compte de classe {self.account.account_class.number}"
            })
        
        # Vérifier le format du code
        if self.code:
            import re
            # Vérifier que le code commence par 401, 411 ou 422
            if not (self.code.startswith('401') or self.code.startswith('411') or self.code.startswith('422')):
                raise ValidationError({
                    'code': "Le code doit commencer par 401 (fournisseur), 411 (client) ou 422 (personnel)."
                })
            
            # Vérifier que le code a au moins 6 caractères (3 pour le préfixe + 3 lettres)
            if len(self.code) < 6:
                raise ValidationError({
                    'code': "Le code doit contenir au moins 6 caractères (préfixe + 3 lettres du nom)."
                })
            
            # Vérifier que les 3 derniers caractères sont des lettres
            name_part = self.code[3:6]
            if not name_part.isalpha():
                raise ValidationError({
                    'code': "Les positions 4-6 du code doivent être les trois premières lettres du nom."
                })
    
    def save(self, *args, **kwargs):
        """Surcharge de la méthode save pour formater le code et le nom"""
        # Appliquer le formatage avec les fonctions utilitaires
        if self.name:
            self.name = format_accounting_name(self.name)
        
        if self.code:
            account_prefix = self.account.code[:3] if self.account else None
            self.code = format_accounting_code(self.code, account_prefix, self.CODE_LENGTH)
        
        # Validation supplémentaire avant sauvegarde
        self.full_clean()
        
        super().save(*args, **kwargs)
        
    @classmethod
    def create_default_tiers(cls, tenant_id):
        """
        Crée des comptes de tiers par défaut pour un tenant.
        Les tiers par défaut incluent un client générique, un fournisseur générique et un employé générique.
        """
        # Récupérer les comptes clients et fournisseurs du plan comptable
        try:
            client_account = Account.objects.get(code='411', tenant_id=tenant_id)
            supplier_account = Account.objects.get(code='401', tenant_id=tenant_id)
            employee_account = Account.objects.get(code='421', tenant_id=tenant_id)
        except Account.DoesNotExist:
            # Essayer avec des codes plus génériques
            try:
                client_account = Account.objects.filter(code__startswith='41', tenant_id=tenant_id).first()
                supplier_account = Account.objects.filter(code__startswith='40', tenant_id=tenant_id).first()
                employee_account = Account.objects.filter(code__startswith='42', tenant_id=tenant_id).first()
                
                if not client_account or not supplier_account or not employee_account:
                    raise Exception("Les comptes de tiers standard n'ont pas été trouvés dans le plan comptable.")
            except Exception as e:
                raise Exception(f"Impossible de créer les tiers par défaut: {str(e)}")
        
        # Créer les tiers par défaut
        default_tiers = [
            {
                'code': 'CLIENT001',
                'name': 'Client générique',
                'type': 'CUSTOMER',
                'account': client_account,
                'notes': 'Compte client par défaut'
            },
            {
                'code': 'FOURN001',
                'name': 'Fournisseur générique',
                'type': 'SUPPLIER',
                'account': supplier_account,
                'notes': 'Compte fournisseur par défaut'
            },
            {
                'code': 'EMPL001',
                'name': 'Employé générique',
                'type': 'EMPLOYEE',
                'account': employee_account,
                'notes': 'Compte employé par défaut'
            },
        ]
        
        created_tiers = []
        for tiers_data in default_tiers:
            # Vérifier si le tiers existe déjà
            if not cls.objects.filter(code=tiers_data['code'], tenant_id=tenant_id).exists():
                tiers = cls.objects.create(
                    tenant_id=tenant_id,
                    **tiers_data
                )
                created_tiers.append(tiers)
        
        return created_tiers