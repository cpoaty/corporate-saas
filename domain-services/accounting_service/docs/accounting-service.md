Documentation du Service de Comptabilité - Corporate SaaS
Introduction
Le Service de Comptabilité est l'un des domaines métier fondamentaux de l'architecture Corporate SaaS. Il fournit les fonctionnalités nécessaires pour gérer la comptabilité générale des entreprises clientes (tenants) de la plateforme. Construit sur une architecture multi-tenant, il assure une isolation complète des données comptables entre les différents clients.
Architecture du Service de Comptabilité
accounting-service/
├── src/
│   ├── manage.py                             # Script de gestion Django
│   ├── apps/
│   │   ├── __init__.py
│   │   └── core/                             # Application principale
│   │       ├── __init__.py
│   │       ├── admin/                        # Configuration de l'interface d'administration
│   │       │   ├── __init__.py
│   │       │   ├── account_admin.py          # Admin pour les comptes
│   │       │   └── fiscal_admin.py           # Admin pour les exercices fiscaux
│   │       ├── middleware/                   # Middlewares personnalisés
│   │       │   ├── __init__.py
│   │       │   └── tenant_middleware.py      # Middleware d'isolation des tenants
│   │       ├── models/                       # Modèles de données
│   │       │   ├── __init__.py
│   │       │   ├── account.py                # Plan comptable
│   │       │   └── fiscal_year.py            # Exercices fiscaux
│   │       ├── serializers/                  # Sérialiseurs pour les API
│   │       │   ├── __init__.py
│   │       │   ├── account_serializers.py    # Sérialiseurs des comptes
│   │       │   └── fiscal_year_serializers.py # Sérialiseurs des exercices fiscaux
│   │       ├── views/                        # Vues et endpoints API
│   │       │   ├── __init__.py
│   │       │   ├── account_views.py          # Vues pour les comptes
│   │       │   └── fiscal_year_views.py      # Vues pour les exercices fiscaux
│   │       ├── urls.py                       # Configuration des URLs de l'API
│   │       └── apps.py                       # Configuration de l'application
│   └── config/                               # Configuration du projet
│       ├── __init__.py
│       ├── settings/                         # Paramètres Django modulaires
│       │   ├── __init__.py
│       │   ├── base.py                       # Paramètres de base
│       │   ├── development.py                # Paramètres de développement
│       │   ├── production.py                 # Paramètres de production
│       │   └── test.py                       # Paramètres de test
│       ├── urls.py                           # URLs principales
│       ├── asgi.py                           # Configuration ASGI
│       └── wsgi.py                           # Configuration WSGI
└── .env                                      # Variables d'environnement
Modèles principaux
Le service de comptabilité s'appuie sur plusieurs modèles de données clés qui permettent de représenter les concepts comptables fondamentaux.
1. Plan Comptable (Account)
Le modèle de plan comptable est structuré selon le référentiel OHADA (Organisation pour l'Harmonisation en Afrique du Droit des Affaires), qui est largement utilisé en Afrique francophone.
Hiérarchie du Plan Comptable

AccountClass: Représente les classes de comptes (1 à 9)

Classe 1: Comptes de ressources durables
Classe 2: Comptes d'actif immobilisé
Classe 3: Comptes de stocks
Classe 4: Comptes de tiers
Classe 5: Comptes de trésorerie
Classe 6: Comptes de charges
Classe 7: Comptes de produits
Classe 8: Comptes de résultats
Classe 9: Comptes analytiques


AccountCategory: Sous-catégories dans chaque classe (ex: 10, 11, 12...)
Account: Comptes individuels avec leur code et description

Structure du modèle Account
pythonclass Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(null=True, blank=True)  # ID du tenant pour isolation
    
    code = models.CharField(max_length=20)
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
Le modèle Account inclut également une méthode utilitaire create_default_accounts_ohada() qui permet d'initialiser automatiquement le plan comptable OHADA pour un tenant.
2. Exercice Fiscal (FiscalYear)
L'exercice fiscal représente une période comptable, généralement d'un an, pendant laquelle les transactions sont regroupées pour les états financiers.
pythonclass FiscalYear(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(null=True, blank=True)  # ID du tenant pour isolation
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, help_text="Code unique pour l'exercice (ex: FY2023)")
    start_date = models.DateField()
    end_date = models.DateField()
    
    is_closed = models.BooleanField(default=False)
    closed_date = models.DateTimeField(null=True, blank=True)
    closed_by = models.UUIDField(null=True, blank=True)  # ID de l'utilisateur
    
    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False, help_text="Empêche toute modification des transactions")
Chaque exercice fiscal est divisé en périodes (typiquement des mois ou des trimestres) :
pythonclass FiscalPeriod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(null=True, blank=True)  # ID du tenant pour isolation
    
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='periods')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30)
    start_date = models.DateField()
    end_date = models.DateField()
    
    number = models.PositiveSmallIntegerField(help_text="Numéro de la période dans l'exercice")
    is_closed = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
API du Service de Comptabilité
Le service expose plusieurs endpoints API RESTful pour interagir avec les fonctionnalités comptables :
Endpoints du Plan Comptable
MéthodeURLDescriptionGET/api/accounting/account-classes/Liste des classes de comptesPOST/api/accounting/account-classes/Création d'une classe de comptesGET/api/accounting/account-classes/{id}/Détails d'une classe de comptesPUT/api/accounting/account-classes/{id}/Mise à jour d'une classe de comptesDELETE/api/accounting/account-classes/{id}/Suppression d'une classe de comptesGET/api/accounting/account-categories/Liste des catégories de comptesGET/api/accounting/accounts/Liste des comptesPOST/api/accounting/accounts/import-ohada/Importe le plan comptable OHADAGET/api/accounting/accounts/{id}/Détails d'un compte spécifique
Endpoints des Exercices Fiscaux
MéthodeURLDescriptionGET/api/accounting/fiscal-years/Liste des exercices fiscauxPOST/api/accounting/fiscal-years/Création d'un exercice fiscalPOST/api/accounting/fiscal-years/{id}/create-periods/Création des périodes pour un exerciceGET/api/accounting/fiscal-periods/Liste des périodes fiscales
Isolation Multi-tenant
Le service de comptabilité est conçu avec une approche multi-tenant où les données sont isolées par tenant. Cette isolation est mise en œuvre de plusieurs façons :

Champ tenant_id dans tous les modèles : Chaque enregistrement est associé à un tenant spécifique via le champ tenant_id.
Middleware d'isolation : Le middleware TenantMiddleware extrait le tenant_id du token JWT et filtre automatiquement toutes les requêtes.
Filtrage au niveau des vues : Toutes les vues filtrent les résultats par tenant_id :

pythondef get_queryset(self):
    queryset = super().get_queryset()
    tenant_id = getattr(self.request, 'tenant_id', None)
    if tenant_id:
        queryset = queryset.filter(tenant_id=tenant_id)
    return queryset

Contraintes d'unicité par tenant : Les contraintes d'unicité dans les modèles incluent le tenant_id pour permettre des codes identiques dans différents tenants :

pythonclass Meta:
    unique_together = [['tenant_id', 'code']]
Administration
Le service de comptabilité fournit une interface d'administration complète basée sur Django Admin, permettant aux administrateurs de :

Gérer le plan comptable
Créer et configurer les exercices fiscaux
Superviser les périodes fiscales
Importer le plan comptable OHADA pour les nouveaux tenants

État actuel du développement

 Modèle de Plan Comptable avec support OHADA
 Modèle d'Exercice Fiscal avec périodes
 API REST pour la gestion des comptes et exercices fiscaux
 Interface d'administration pour la gestion des données
 Isolation multi-tenant des données
 Documentation API avec Swagger/OpenAPI
 Modèle de Journal Comptable
 Modèle de Transaction

Prochaines étapes

Développer les modèles Journal et Transaction

Implémenter le modèle Journal pour les journaux comptables
Implémenter le modèle Transaction pour les écritures comptables
Ajouter les contraintes de validation (équilibre débit/crédit)


Développer les fonctionnalités comptables avancées

Saisie des écritures comptables
Clôture des périodes et exercices fiscaux
Importation/exportation des données


Développer le module de reporting financier

Grand livre
Balance des comptes
Compte de résultat
Bilan


Intégration avec les autres services

Interface avec le service de facturation
Interface avec le service de paie
Interface avec le service bancaire



Configuration et Installation
Prérequis

Python 3.11+
PostgreSQL 13+
Django 5.2+
Django REST Framework 3.14+

Installation

Cloner le dépôt :
bashgit clone https://github.com/votre-organisation/accounting-service.git
cd accounting-service

Installer les dépendances :
bashpip install -r requirements.txt

Configurer les variables d'environnement :
Créer un fichier .env dans le répertoire racine avec :
# Variables d'environnement pour le service de comptabilité
# Paramètres Django
DEBUG=True
SECRET_KEY=votre_clé_secrète_ici_changez_la_en_production
# Configuration de la base de données PostgreSQL
DB_NAME=accounting_service_db
DB_USER=corporate_saas
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
# Paramètres d'isolation multi-tenant
TENANT_ID_FIELD=tenant_id
# Paramètres de sécurité JWT
JWT_SECRET_KEY=une_autre_clé_secrète_pour_jwt_à_changer
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=14
# Paramètres d'application
DEFAULT_PAGE_SIZE=20

Appliquer les migrations :
bashcd src
python manage.py migrate

Créer un superutilisateur :
bashpython manage.py createsuperuser

Lancer le serveur de développement :
bashpython manage.py runserver


Accès aux interfaces

Interface d'administration : http://127.0.0.1:8000/admin/
API REST : http://127.0.0.1:8000/api/accounting/
Documentation Swagger : http://127.0.0.1:8000/swagger/
Documentation ReDoc : http://127.0.0.1:8000/redoc/

Utilisation
Importer le plan comptable OHADA
Pour initialiser le plan comptable OHADA pour un tenant, utilisez l'endpoint API /api/accounting/accounts/import-ohada/ ou exécutez la commande suivante dans le shell Django :
pythonfrom apps.core.models.account import Account
Account.create_default_accounts_ohada('tenant_id_here')
Créer un exercice fiscal avec périodes

Créez un exercice fiscal via l'interface d'administration ou l'API
Utilisez l'endpoint /api/accounting/fiscal-years/{id}/create-periods/ pour générer automatiquement les périodes mensuelles ou trimestrielles


Cette documentation sera mise à jour au fur et à mesure de l'avancement du développement du service de comptabilité.