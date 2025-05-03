# apps/core/models/account.py
from django.db import models
import uuid
import json
import os
from django.conf import settings
from ..utils import format_accounting_name, format_accounting_code

class AccountType(models.TextChoices):
    ASSET = 'ASSET', 'Actif'
    LIABILITY = 'LIABILITY', 'Passif'
    EQUITY = 'EQUITY', 'Capitaux propres'
    REVENUE = 'REVENUE', 'Produit'
    EXPENSE = 'EXPENSE', 'Charge'

class AccountClass(models.Model):
    """Classe de compte (1 à 9 selon le plan comptable OHADA)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(null=True, blank=True)  # ID du tenant pour isolation
    
    number = models.PositiveSmallIntegerField()  # 1 à 9
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Classe de compte"
        verbose_name_plural = "Classes de comptes"
        ordering = ['number']
        unique_together = [['tenant_id', 'number']]
    
    def __str__(self):
        return f"Classe {self.number} - {self.name}"

class AccountCategory(models.Model):
    """Catégorie de compte (ex: 10, 11, 12... dans le plan OHADA)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(null=True, blank=True)  # ID du tenant pour isolation
    
    account_class = models.ForeignKey(AccountClass, on_delete=models.CASCADE, related_name='categories')
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Catégorie de compte"
        verbose_name_plural = "Catégories de comptes"
        ordering = ['code']
        unique_together = [['tenant_id', 'code']]
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Account(models.Model):
    """Compte du plan comptable OHADA"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(null=True, blank=True)  # ID du tenant pour isolation
    
    code = models.CharField(max_length=120)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    account_class = models.ForeignKey(AccountClass, on_delete=models.PROTECT, related_name='accounts')
    category = models.ForeignKey(AccountCategory, on_delete=models.PROTECT, related_name='accounts', null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    
    level = models.PositiveSmallIntegerField(default=0, help_text="Niveau hiérarchique du compte")
    type = models.CharField(max_length=20, choices=AccountType.choices)
    
    is_active = models.BooleanField(default=True)
    is_reconcilable = models.BooleanField(default=True, help_text="Indique si le compte peut être rapproché")
    is_tax_relevant = models.BooleanField(default=False, help_text="Indique si le compte est pertinent pour la TVA")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Compte"
        verbose_name_plural = "Comptes"
        ordering = ['code']
        unique_together = [['tenant_id', 'code']]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def save(self, *args, **kwargs):
        if self.name:
            self.name = format_accounting_name(self.name)
        if self.code:
            self.code = format_accounting_code(self.code)
        super().save(*args, **kwargs)
    
    def get_balance(self, start_date=None, end_date=None):
        """Calcule le solde du compte pour une période donnée"""
        from .transaction import TransactionLine
        
        query = TransactionLine.objects.filter(
            account=self,
            transaction__tenant_id=self.tenant_id
        )
        
        if start_date:
            query = query.filter(transaction__date__gte=start_date)
        
        if end_date:
            query = query.filter(transaction__date__lte=end_date)
        
        # Calculer le solde (débit - crédit)
        debit_sum = query.aggregate(models.Sum('debit'))['debit__sum'] or 0
        credit_sum = query.aggregate(models.Sum('credit'))['credit__sum'] or 0
        
        # Le sens du solde dépend du type de compte
        if self.type in [AccountType.ASSET, AccountType.EXPENSE]:
            return debit_sum - credit_sum
        else:
            return credit_sum - debit_sum

    @classmethod
    def create_default_accounts_ohada(cls, tenant_id):
        """Crée le plan comptable OHADA par défaut pour un tenant"""
        # Chemin vers le fichier JSON du plan comptable OHADA
        json_file_path = os.path.join(settings.BASE_DIR, 'data', 'plan_comptable_ohada.json')
        
        # Si le fichier n'est pas trouvé à cet emplacement, essayer un chemin alternatif
        if not os.path.exists(json_file_path):
            # Chemin alternatif relatif au dossier courant
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_file_path = os.path.join(current_dir, '..', '..', '..', 'data', 'plan_comptable_ohada.json')
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                plan_comptable = json.load(file)
        except FileNotFoundError:
            raise Exception(f"Le fichier du plan comptable OHADA n'a pas été trouvé à l'emplacement: {json_file_path}")
    
        # Dictionnaire pour stocker les références aux comptes créés
        account_refs = {}
        
        # Création des classes de comptes et leurs catégories
        for class_key, class_data in plan_comptable.items():
            # Extraire le numéro de classe (1 à 9)
            class_number = int(class_key.split()[0])
            class_name = class_key.split(' - ')[1] if ' - ' in class_key else class_key
            
            # Créer la classe de compte
            account_class = AccountClass.objects.create(
                tenant_id=tenant_id,
                number=class_number,
                name=class_name
            )
            
            # Déterminer le type de compte en fonction de la classe
            account_type = cls._get_account_type_for_class(class_number)
            
            # Parcourir les catégories de la classe
            for category_key, category_data in class_data.items():
                if isinstance(category_data, dict):
                    # C'est une catégorie avec des sous-comptes
                    category_code = category_key.split()[0] if ' ' in category_key else category_key
                    category_name = ' '.join(category_key.split()[1:]) if ' ' in category_key else category_key
                    
                    # Créer la catégorie
                    category = AccountCategory.objects.create(
                        tenant_id=tenant_id,
                        account_class=account_class,
                        code=category_code,
                        name=category_name
                    )
                    
                    # Créer le compte principal pour cette catégorie
                    parent_account = cls.objects.create(
                        tenant_id=tenant_id,
                        code=category_code,
                        name=category_name,
                        account_class=account_class,
                        category=category,
                        type=account_type,
                        level=1
                    )
                    
                    account_refs[category_code] = parent_account
                    
                    # Parcourir récursivement les sous-comptes
                    cls._create_sub_accounts(
                        tenant_id=tenant_id,
                        parent_account=parent_account,
                        account_class=account_class,
                        category=category,
                        data=category_data,
                        account_type=account_type,
                        level=2,
                        account_refs=account_refs
                    )
                else:
                    # C'est un compte simple sans sous-comptes
                    account_code = category_key
                    account_name = category_data
                    
                    # Créer le compte
                    account = cls.objects.create(
                        tenant_id=tenant_id,
                        code=account_code,
                        name=account_name,
                        account_class=account_class,
                        type=account_type,
                        level=1
                    )
                    
                    account_refs[account_code] = account
        
        return account_refs

    @classmethod
    def _create_sub_accounts(cls, tenant_id, parent_account, account_class, category, data, account_type, level, account_refs):
        """Crée récursivement les sous-comptes"""
        for code, value in data.items():
            if isinstance(value, dict):
                # C'est un sous-compte avec des sous-sous-comptes
                sub_account = cls.objects.create(
                    tenant_id=tenant_id,
                    code=code,
                    name=code if isinstance(code, str) and ' ' in code else code,
                    account_class=account_class,
                    category=category,
                    parent=parent_account,
                    type=account_type,
                    level=level
                )
                
                account_refs[code] = sub_account
                
                # Création récursive des sous-sous-comptes
                cls._create_sub_accounts(
                    tenant_id=tenant_id,
                    parent_account=sub_account,
                    account_class=account_class,
                    category=category,
                    data=value,
                    account_type=account_type,
                    level=level+1,
                    account_refs=account_refs
                )
            else:
                # C'est un compte terminal
                sub_account = cls.objects.create(
                    tenant_id=tenant_id,
                    code=code,
                    name=value,
                    account_class=account_class,
                    category=category,
                    parent=parent_account,
                    type=account_type,
                    level=level
                )
                
                account_refs[code] = sub_account
    
    @staticmethod
    def _get_account_type_for_class(class_number):
        """Détermine le type de compte en fonction de la classe"""
        if class_number in [1, 5]:
            return AccountType.EQUITY
        elif class_number == 2:
            return AccountType.ASSET
        elif class_number in [3, 6]:
            return AccountType.EXPENSE
        elif class_number in [4, 7]:
            return AccountType.LIABILITY
        elif class_number == 8:
            return AccountType.REVENUE
        else:
            return AccountType.ASSET  # Par défaut