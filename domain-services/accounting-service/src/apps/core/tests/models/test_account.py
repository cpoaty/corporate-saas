from django.test import TestCase
from unittest.mock import patch, mock_open
import uuid
import json
import os
from datetime import date
from decimal import Decimal

from apps.core.models.account import AccountClass, AccountCategory, Account, AccountType
from apps.core.utils import format_accounting_name, format_accounting_code


class AccountTypeTestCase(TestCase):
    """Tests pour l'énumération AccountType"""

    def test_account_type_choices(self):
        """Vérifier que tous les types de compte attendus sont définis"""
        self.assertEqual(AccountType.ASSET, 'ASSET')
        self.assertEqual(AccountType.LIABILITY, 'LIABILITY')
        self.assertEqual(AccountType.EQUITY, 'EQUITY')
        self.assertEqual(AccountType.REVENUE, 'REVENUE')
        self.assertEqual(AccountType.EXPENSE, 'EXPENSE')


class AccountClassTestCase(TestCase):
    """Tests pour le modèle AccountClass"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.tenant_id = uuid.uuid4()
        self.account_class = AccountClass.objects.create(
            tenant_id=self.tenant_id,
            number=1,
            name="Comptes de capitaux",
            description="Capitaux, provisions, emprunts"
        )

    def test_account_class_creation(self):
        """Tester la création d'une classe de compte"""
        self.assertEqual(self.account_class.number, 1)
        self.assertEqual(self.account_class.name, "Comptes de capitaux")
        self.assertEqual(self.account_class.description, "Capitaux, provisions, emprunts")
        self.assertEqual(self.account_class.tenant_id, self.tenant_id)
        self.assertIsNotNone(self.account_class.created_at)
        self.assertIsNotNone(self.account_class.updated_at)

    def test_account_class_str(self):
        """Tester la représentation textuelle d'une classe de compte"""
        self.assertEqual(str(self.account_class), "Classe 1 - Comptes de capitaux")

    def test_unique_together_constraint(self):
        """Tester la contrainte d'unicité (tenant_id, number)"""
        # Tentative de création d'une classe avec le même tenant_id et number
        with self.assertRaises(Exception):
            AccountClass.objects.create(
                tenant_id=self.tenant_id,
                number=1,
                name="Duplicata"
            )
        
        # Création d'une classe avec le même number mais un tenant_id différent
        different_tenant = uuid.uuid4()
        duplicate_class = AccountClass.objects.create(
            tenant_id=different_tenant,
            number=1,
            name="Autre tenant"
        )
        self.assertIsNotNone(duplicate_class.id)


class AccountCategoryTestCase(TestCase):
    """Tests pour le modèle AccountCategory"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.tenant_id = uuid.uuid4()
        self.account_class = AccountClass.objects.create(
            tenant_id=self.tenant_id,
            number=1,
            name="Comptes de capitaux"
        )
        self.category = AccountCategory.objects.create(
            tenant_id=self.tenant_id,
            account_class=self.account_class,
            code="10",
            name="Capital et réserves"
        )

    def test_category_creation(self):
        """Tester la création d'une catégorie de compte"""
        self.assertEqual(self.category.code, "10")
        self.assertEqual(self.category.name, "Capital et réserves")
        self.assertEqual(self.category.tenant_id, self.tenant_id)
        self.assertEqual(self.category.account_class, self.account_class)
        self.assertIsNone(self.category.description)

    def test_category_str(self):
        """Tester la représentation textuelle d'une catégorie"""
        self.assertEqual(str(self.category), "10 - Capital et réserves")

    def test_unique_together_constraint(self):
        """Tester la contrainte d'unicité (tenant_id, code)"""
        # Tentative de création d'une catégorie avec le même tenant_id et code
        with self.assertRaises(Exception):
            AccountCategory.objects.create(
                tenant_id=self.tenant_id,
                account_class=self.account_class,
                code="10",
                name="Duplicata"
            )
        
        # Création d'une catégorie avec le même code mais un tenant_id différent
        different_tenant = uuid.uuid4()
        duplicate_category = AccountCategory.objects.create(
            tenant_id=different_tenant,
            account_class=self.account_class,
            code="10",
            name="Autre tenant"
        )
        self.assertIsNotNone(duplicate_category.id)


class AccountTestCase(TestCase):
    """Tests pour le modèle Account"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.tenant_id = uuid.uuid4()
        
        # Créer une classe de compte
        self.account_class = AccountClass.objects.create(
            tenant_id=self.tenant_id,
            number=2,
            name="Comptes d'actifs immobilisés"
        )
        
        # Créer une catégorie de compte
        self.category = AccountCategory.objects.create(
            tenant_id=self.tenant_id,
            account_class=self.account_class,
            code="21",
            name="Immobilisations corporelles"
        )
        
        # Créer un compte parent
        self.parent_account = Account.objects.create(
            tenant_id=self.tenant_id,
            code="21",
            name="Immobilisations corporelles",
            account_class=self.account_class,
            category=self.category,
            type=AccountType.ASSET,
            level=1
        )
        
        # Créer un compte enfant
        self.account = Account.objects.create(
            tenant_id=self.tenant_id,
            code="2131",
            name="Bâtiments industriels",
            account_class=self.account_class,
            category=self.category,
            parent=self.parent_account,
            type=AccountType.ASSET,
            level=2,
            is_reconcilable=True,
            is_tax_relevant=False
        )

    def test_account_creation(self):
        """Tester la création d'un compte"""
        self.assertEqual(self.account.code, "2131")
        self.assertEqual(self.account.name, "Bâtiments Industriels")  # Formaté par save()
        self.assertEqual(self.account.account_class, self.account_class)
        self.assertEqual(self.account.category, self.category)
        self.assertEqual(self.account.parent, self.parent_account)
        self.assertEqual(self.account.level, 2)
        self.assertEqual(self.account.type, AccountType.ASSET)
        self.assertTrue(self.account.is_active)
        self.assertTrue(self.account.is_reconcilable)
        self.assertFalse(self.account.is_tax_relevant)

    def test_account_str(self):
        """Tester la représentation textuelle d'un compte"""
        self.assertEqual(str(self.account), "2131 - Bâtiments Industriels")

    def test_unique_together_constraint(self):
        """Tester la contrainte d'unicité (tenant_id, code)"""
        # Tentative de création d'un compte avec le même tenant_id et code
        with self.assertRaises(Exception):
            Account.objects.create(
                tenant_id=self.tenant_id,
                code="2131",
                name="Duplicata",
                account_class=self.account_class,
                type=AccountType.ASSET
            )
        
        # Création d'un compte avec le même code mais un tenant_id différent
        different_tenant = uuid.uuid4()
        duplicate_account = Account.objects.create(
            tenant_id=different_tenant,
            code="2131",
            name="Autre tenant",
            account_class=self.account_class,
            type=AccountType.ASSET
        )
        self.assertIsNotNone(duplicate_account.id)

    def test_name_formatting(self):
        """Tester le formatage du nom lors de la sauvegarde"""
        account = Account.objects.create(
            tenant_id=self.tenant_id,
            code="2181",
            name="installations générales    ",  # Espaces superflus et casse incorrecte
            account_class=self.account_class,
            type=AccountType.ASSET
        )
        
        # Vérifier que le nom a été correctement formaté (title case, sans espaces superflus)
        self.assertEqual(account.name, "Installations Générales")

    def test_code_formatting(self):
        """Tester le formatage du code lors de la sauvegarde"""
        account = Account.objects.create(
            tenant_id=self.tenant_id,
            code="6123-ab",  # Caractères non alphanumériques et casse incorrecte
            name="Transports sur ventes",
            account_class=self.account_class,
            type=AccountType.EXPENSE
        )
        
        # Vérifier que le code a été correctement formaté (majuscules, sans caractères spéciaux)
        self.assertEqual(account.code, "6123AB")

    @patch('apps.core.models.account.TransactionLine.objects.filter')
    def test_get_balance_asset_account(self, mock_filter):
        """Tester le calcul du solde pour un compte d'actif"""
        # Configurer le mock pour simuler les transactions
        mock_query = mock_filter.return_value
        mock_query.filter.return_value = mock_query
        
        # Simuler les sommes de débit et crédit
        mock_query.aggregate.side_effect = [
            {'debit__sum': Decimal('1000.00')},  # Somme des débits
            {'credit__sum': Decimal('400.00')}   # Somme des crédits
        ]
        
        # Calculer le solde (pour un compte d'actif: débit - crédit)
        balance = self.account.get_balance(
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )
        
        # Vérifier le résultat
        self.assertEqual(balance, Decimal('600.00'))  # 1000 - 400 = 600
        
        # Vérifier que les bonnes requêtes ont été faites
        mock_filter.assert_called_once_with(
            account=self.account,
            transaction__tenant_id=self.tenant_id
        )
        
        # Vérifier que les filtres de date ont été appliqués
        mock_query.filter.assert_any_call(transaction__date__gte=date(2023, 1, 1))
        mock_query.filter.assert_any_call(transaction__date__lte=date(2023, 12, 31))

    @patch('apps.core.models.account.TransactionLine.objects.filter')
    def test_get_balance_liability_account(self, mock_filter):
        """Tester le calcul du solde pour un compte de passif"""
        # Créer un compte de passif
        liability_account = Account.objects.create(
            tenant_id=self.tenant_id,
            code="4011",
            name="Fournisseurs",
            account_class=self.account_class,  # On réutilise la même classe pour simplifier
            type=AccountType.LIABILITY,
            level=1
        )
        
        # Configurer le mock pour simuler les transactions
        mock_query = mock_filter.return_value
        mock_query.filter.return_value = mock_query
        
        # Simuler les sommes de débit et crédit
        mock_query.aggregate.side_effect = [
            {'debit__sum': Decimal('300.00')},   # Somme des débits
            {'credit__sum': Decimal('800.00')}   # Somme des crédits
        ]
        
        # Calculer le solde (pour un compte de passif: crédit - débit)
        balance = liability_account.get_balance()
        
        # Vérifier le résultat
        self.assertEqual(balance, Decimal('500.00'))  # 800 - 300 = 500
        
        # Vérifier que les bonnes requêtes ont été faites
        mock_filter.assert_called_once_with(
            account=liability_account,
            transaction__tenant_id=self.tenant_id
        )

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "1 Comptes de capitaux": {
            "10 Capital": {
                "101": "Capital social",
                "109": "Actionnaires, capital souscrit non appelé"
            }
        }
    }))
    def test_create_default_accounts_ohada(self, mock_file, mock_exists):
        """Tester la création des comptes OHADA par défaut"""
        tenant_id = uuid.uuid4()
        accounts = Account.create_default_accounts_ohada(tenant_id)
        
        # Vérifier que les bons fichiers ont été ouverts
        mock_file.assert_called_once()
        self.assertIn('plan_comptable_ohada.json', mock_file.call_args[0][0])
        
        # Vérifier qu'une classe de compte a été créée
        account_class = AccountClass.objects.filter(tenant_id=tenant_id, number=1).first()
        self.assertIsNotNone(account_class)
        self.assertEqual(account_class.name, "Comptes de capitaux")
        
        # Vérifier qu'une catégorie a été créée
        category = AccountCategory.objects.filter(tenant_id=tenant_id, code="10").first()
        self.assertIsNotNone(category)
        self.assertEqual(category.name, "Capital")
        
        # Vérifier que les comptes ont été créés
        accounts_101 = Account.objects.filter(tenant_id=tenant_id, code="101").first()
        self.assertIsNotNone(accounts_101)
        self.assertEqual(accounts_101.name, "Capital Social")  # Formaté
        
        accounts_109 = Account.objects.filter(tenant_id=tenant_id, code="109").first()
        self.assertIsNotNone(accounts_109)
        
        # Vérifier le dictionnaire de références retourné
        self.assertIn("101", accounts)
        self.assertIn("109", accounts)
        self.assertEqual(accounts["101"].name, "Capital Social")

    def test_get_account_type_for_class(self):
        """Tester la détermination du type de compte en fonction de la classe"""
        self.assertEqual(Account._get_account_type_for_class(1), AccountType.EQUITY)
        self.assertEqual(Account._get_account_type_for_class(2), AccountType.ASSET)
        self.assertEqual(Account._get_account_type_for_class(3), AccountType.EXPENSE)
        self.assertEqual(Account._get_account_type_for_class(4), AccountType.LIABILITY)
        self.assertEqual(Account._get_account_type_for_class(5), AccountType.EQUITY)
        self.assertEqual(Account._get_account_type_for_class(6), AccountType.EXPENSE)
        self.assertEqual(Account._get_account_type_for_class(7), AccountType.LIABILITY)
        self.assertEqual(Account._get_account_type_for_class(8), AccountType.REVENUE)
        self.assertEqual(Account._get_account_type_for_class(9), AccountType.ASSET)  # Par défaut