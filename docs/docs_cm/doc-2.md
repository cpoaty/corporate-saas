# Documentation du Projet Corporate SaaS

## Vue d'ensemble du projet

Corporate SaaS est une plateforme modulaire multi-domaines basée sur une architecture micro-services et micro-frontends. Elle vise à offrir initialement des fonctionnalités de comptabilité avec possibilité d'extension future vers d'autres domaines comme la paie, l'audit et l'archivage.

## Architecture globale

L'architecture adoptée est une approche hybride qui combine :
- **Micro-frontends** pour l'interface utilisateur
- **Micro-services** pour le backend
- **Multi-tenancy** par schéma PostgreSQL pour l'isolation des données clients

### Structure du projet
```
corporate-saas/
├── core-services/                  # Services partagés
│   ├── auth-service/               # Service d'authentification 
│   ├── tenant-service/             # Gestion des tenants
│   └── user-service/               # Gestion des utilisateurs
│
├── domain-services/                # Services par domaine métier
│   ├── accounting-service/         # Service de comptabilité
│   ├── payroll-service/            # Service de paie (futur)
│   ├── audit-service/              # Service d'audit (futur)
│   └── archiving-service/          # Service d'archivage (futur)
│
├── api-gateway/                    # API Gateway
│
├── frontend/                       # Applications frontend
│   ├── shell/                      # Application conteneur
│   ├── shared/                     # Composants partagés
│   ├── accounting/                 # Module comptabilité
│   └── ...                         # Autres modules
│
└── infrastructure/                 # Code d'infrastructure
```

## Concept multi-tenant

Un système "multi-tenant" est une architecture où une seule instance d'une application sert plusieurs clients ou "tenants". Chaque tenant dispose d'un espace de données isolé, tout en partageant l'infrastructure et le code.

Pour notre plateforme, nous utilisons l'isolation par schéma PostgreSQL :
- Chaque client (entreprise) a son propre schéma dans la base de données
- L'authentification détermine le tenant et route vers le bon schéma
- Les données sont strictement isolées entre tenants

## État actuel du développement

### Service d'authentification (auth-service)

Nous avons entamé la mise en place du service d'authentification qui sera la première brique fondamentale de notre architecture :

1. **Structure mise en place** :
   - Configuration Django avec settings modulaires (base, development, production)
   - Support REST framework et JWT pour l'authentification par token
   - Configuration CORS pour les appels cross-domain

2. **À implémenter** :
   - Modèle utilisateur personnalisé avec support multi-tenant
   - Modèle Tenant pour gérer les clients
   - API d'authentification (enregistrement, connexion, etc.)

### Configuration terminée

- Structure du projet et organisation des dossiers
- Configuration Django de base fonctionnelle
- Résolution des problèmes d'import et de configuration

## Prochaines étapes

1. **Finaliser le service d'authentification** :
   - Créer les modèles User et Tenant
   - Implémenter les API d'authentification
   - Tester l'authentification JWT

2. **Développer le service de gestion des tenants** :
   - Middleware d'isolation des tenants
   - API de gestion des tenants
   - Mécanismes d'onboarding de nouveaux clients

3. **Mettre en place l'API Gateway** :
   - Configuration Kong/Gateway
   - Routes et politiques de sécurité
   - Intégration avec l'authentification

4. **Développer le shell frontend** :
   - Layout principal de l'application
   - Système de chargement dynamique des modules
   - Intégration avec le système d'authentification

## Modèles clés à implémenter

### Modèle User (Utilisateur)

```python
class User(AbstractUser):
    """
    Modèle utilisateur personnalisé avec support multi-tenant
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    tenant_id = models.UUIDField(null=True, blank=True)  # ID du tenant
    is_tenant_admin = models.BooleanField(default=False)  # Admin du tenant
    is_platform_admin = models.BooleanField(default=False)  # Admin global
    
    # Champs additionnels
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    preferred_language = models.CharField(max_length=10, default="fr")
    # ...
```

### Modèle Tenant (Client)

```python
class Tenant(models.Model):
    """
    Modèle Tenant pour la gestion multi-tenant
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, unique=True)
    schema_name = models.CharField(max_length=100, unique=True)
    
    # Informations business
    business_name = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    
    # État et configuration
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    settings = models.JSONField(default=dict, blank=True)
    # ...
```

## Roadmap du projet

Le développement suivra une approche progressive par phases:

1. **Phase 1** : Services Core (auth, tenant) et fondations
2. **Phase 2** : Domaine comptabilité 
3. **Phase 3** : Domaine paie (futur)
4. **Phase 4** : Domaine audit (futur) 
5. **Phase 5** : Domaine archivage (futur)
6. **Phase 6** : Enrichissements transverses

## Environnement de développement

Le projet utilise actuellement:
- Python 3.11 avec environnement Anaconda (normx_env)
- Django et Django REST Framework
- VS Code comme éditeur principal
- Système de gestion de version Git

## Défis résolus

- Configuration de l'environnement de développement
- Structure du projet modulaire
- Configuration multi-environnement (dev, prod)
- Résolution des conflits d'importation et de packages

## Notes importantes

- L'approche multi-tenant par schéma PostgreSQL nécessitera l'utilisation éventuelle d'une extension comme django-tenant-schemas
- L'interface utilisateur nécessitera une approche micro-frontend avec chargement dynamique des modules
- Les tests et la documentation doivent être développés en parallèle des fonctionnalités