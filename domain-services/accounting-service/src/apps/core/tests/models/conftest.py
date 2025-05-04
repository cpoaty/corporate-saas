"""
Fixtures pour les tests des modèles.
"""

import uuid
import pytest
from datetime import date

from apps.core.models.account import AccountClass, AccountCategory, Account, AccountType


@pytest.fixture
def tenant_id():
    """Fournit un UUID pour le tenant"""
    return uuid.uuid4()


@pytest.fixture
def account_class(tenant_id):
    """Crée une classe de compte pour les tests"""
    return AccountClass.objects.create(
        tenant_id=tenant_id,
        number=2,
        name="Comptes d'actifs immobilisés",
        description="Immobilisations incorporelles et corporelles"
    )


@pytest.fixture
def account_category(tenant_id, account_class):
    """Crée une catégorie de compte pour les tests"""
    return AccountCategory.objects.create(
        tenant_id=tenant_id,
        account_class=account_class,
        code="21",
        name="Immobilisations corporelles"
    )


@pytest.fixture
def parent_account(tenant_id, account_class, account_category):
    """Crée un compte parent pour les tests"""
    return Account.objects.create(
        tenant_id=tenant_id,
        code="21",
        name="Immobilisations corporelles",
        account_class=account_class,
        category=account_category,
        type=AccountType.ASSET,
        level=1
    )


@pytest.fixture
def child_account(tenant_id, account_class, account_category, parent_account):
    """Crée un compte enfant pour les tests"""
    return Account.objects.create(
        tenant_id=tenant_id,
        code="2131",
        name="Bâtiments industriels",
        account_class=account_class,
        category=account_category,
        parent=parent_account,
        type=AccountType.ASSET,
        level=2,
        is_reconcilable=True,
        is_tax_relevant=False
    )