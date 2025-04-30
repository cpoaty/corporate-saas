# Documentation des Core Services

## Introduction

Les **Core Services** constituent l'épine dorsale de l'architecture Corporate SaaS et fournissent les fonctionnalités transversales fondamentales utilisées par tous les domaines métier. Contrairement aux Domain Services qui sont spécifiques à un domaine métier particulier (comptabilité, paie, etc.), les Core Services sont des services partagés qui prennent en charge des aspects essentiels comme l'authentification, la gestion des utilisateurs et la gestion des tenants (clients).

## Architecture des Core Services

```
core-services/
├── auth-service/               # Service d'authentification
├── tenant-service/             # Service de gestion des tenants
└── user-service/               # Service de gestion des utilisateurs
```

Chaque service est un microservice indépendant avec sa propre base de données, ses API et sa logique métier spécifique. Ces services communiquent entre eux via des API REST et sont accessibles via l'API Gateway central.

## Vue d'ensemble des Core Services

### 1. Auth Service (Service d'Authentification)

Le service d'authentification est le gardien de la sécurité de la plateforme. Il gère l'authentification et l'autorisation des utilisateurs sur l'ensemble de la plateforme.

### 2. Tenant Service (Service de Gestion des Tenants)

Le service de gestion des tenants s'occupe de la création et de la gestion des différents clients (tenants) de la plateforme, y compris le provisionnement des ressources et l'isolation des données.

### 3. User Service (Service de Gestion des Utilisateurs)

Le service de gestion des utilisateurs prend en charge l'administration des utilisateurs, leurs profils, leurs préférences et leurs associations avec les tenants.

## Auth Service en détail

### Objectif du service

L'Auth Service est la porte d'entrée sécurisée de la plateforme Corporate SaaS. Il garantit que seuls les utilisateurs autorisés peuvent accéder aux ressources et que chaque utilisateur ne peut voir que les données du tenant auquel il appartient.

### Fonctionnalités principales

1. **Authentification**
   - Gestion des identifiants (username/email + mot de passe)
   - Authentification via JWT (JSON Web Tokens)
   - Support de l'authentification multi-facteurs (MFA)
   - Sessions sécurisées

2. **Autorisation**
   - Gestion des rôles et permissions
   - Contrôle d'accès basé sur les rôles (RBAC)
   - Isolation des tenants

3. **Sécurité**
   - Stockage sécurisé des mots de passe (hachage avec sel)
   - Protection contre les attaques courantes (brute force, injection, CSRF)
   - Journalisation des tentatives de connexion

4. **Gestion des tokens**
   - Émission de tokens JWT (access token et refresh token)
   - Validation et renouvellement des tokens
   - Révocation des tokens

### Architecture technique

```
auth-service/
├── src/
│   ├── apps/
│   │   └── core/                    # Application principale
│   │       ├── models/
│   │       │   ├── user.py          # Modèle utilisateur
│   │       │   └── tenant.py        # Modèle tenant
│   │       ├── serializers/         # Sérialiseurs pour les API
│   │       ├── views/               # Vues et endpoints API
│   │       ├── middleware/          # Middlewares personnalisés
│   │       └── permissions/         # Classes de permission
│   ├── config/                      # Configuration Django
│   │   ├── settings/
│   │   │   ├── base.py             # Paramètres communs
│   │   │   ├── development.py      # Paramètres de développement
│   │   │   └── production.py       # Paramètres de production
│   │   ├── urls.py                 # Configuration des URLs
│   │   └── wsgi.py                 # Configuration WSGI
│   └── manage.py                   # Script de gestion Django
└── requirements/                   # Dépendances du projet
```

### Modèles de données principaux

#### Modèle User (Utilisateur)

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
    profile_picture = models.URLField(blank=True, null=True)
    
    # Préférences utilisateur
    preferred_language = models.CharField(max_length=10, default="fr")
    date_format = models.CharField(max_length=20, default="DD/MM/YYYY")
```

#### Modèle Tenant (Client)

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
    
    # État du tenant
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Configuration
    settings = models.JSONField(default=dict, blank=True)
```

### Endpoints API principaux

#### Authentification

- `POST /api/auth/register/` - Inscription d'un nouvel utilisateur
- `POST /api/auth/login/` - Connexion (obtention de tokens JWT)
- `POST /api/auth/refresh/` - Rafraîchissement du token d'accès
- `POST /api/auth/verify/` - Vérification de la validité d'un token
- `POST /api/auth/logout/` - Déconnexion (révocation des tokens)

#### Gestion de profil

- `GET /api/auth/profile/` - Obtention du profil utilisateur
- `PUT /api/auth/profile/` - Mise à jour du profil utilisateur
- `PUT /api/auth/password/change/` - Changement de mot de passe
- `POST /api/auth/password/reset/` - Demande de réinitialisation de mot de passe

### Aspects multi-tenant

L'Auth Service joue un rôle crucial dans l'architecture multi-tenant:

1. **Isolation des données**: Chaque utilisateur est lié à un tenant spécifique via `tenant_id`
2. **Contexte tenant**: À chaque requête authentifiée, l'identifiant du tenant est extrait du token JWT
3. **Middleware d'isolation**: Garantit qu'un utilisateur ne peut accéder qu'aux données de son propre tenant
4. **Administrateurs**: Distingue entre administrateurs de tenant (peuvent gérer leur tenant) et administrateurs de plateforme (peuvent gérer tous les tenants)

### Sécurité et conformité

- **Chiffrement**: Toutes les communications sont chiffrées via HTTPS/TLS
- **Protection des données**: Conformité RGPD/GDPR
- **Audit trail**: Journalisation des actions sensibles pour des raisons de sécurité et de conformité
- **Rate limiting**: Protection contre les attaques par force brute

### Intégration avec d'autres services

- **API Gateway**: Valide les tokens JWT pour toutes les requêtes à n'importe quel service
- **Tenant Service**: Communique pour les opérations liées aux tenants
- **User Service**: Partage les informations utilisateur via API
- **Domain Services**: Fournit le contexte d'authentification et de tenant

## Évolutions futures

1. **Authentification sociale**: Intégration avec Google, Microsoft, etc.
2. **Single Sign-On (SSO)**: Support des protocoles SAML et OIDC
3. **Authentification biométrique**: Support de WebAuthn
4. **Gestion des sessions avancée**: Détection d'activités suspectes
5. **Analytics de sécurité**: Tableaux de bord et alertes de sécurité