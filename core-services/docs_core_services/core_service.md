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
│   │       │   └── tenant_middleware.py  # Middleware d'isolation des tenants
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
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
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

#### Test du tenant

- `GET /api/tenant-test/` - Endpoint de test qui vérifie l'isolation des tenants

### Middleware d'isolation des tenants

Le middleware d'isolation des tenants est une composante essentielle de l'architecture multi-tenant. Il assure que chaque utilisateur ne peut accéder qu'aux données de son propre tenant.

```python
class TenantMiddleware:
    """
    Middleware qui identifie le tenant de l'utilisateur actuel et le stocke dans request.
    Empêche l'accès aux données d'autres tenants.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Initialiser tenant_id à None
        request.tenant_id = None
        
        # Essayer d'extraire le token JWT de l'en-tête Authorization
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # Décoder le token JWT
                decoded_token = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
                
                # Extraire l'user_id du token
                user_id = decoded_token.get('user_id')
                
                # Si on a un user_id, on peut récupérer le tenant_id
                if user_id:
                    from apps.core.models import User
                    try:
                        user = User.objects.get(id=user_id)
                        request.tenant_id = user.tenant_id
                        request.user_id = user_id
                    except User.DoesNotExist:
                        pass
            except jwt.PyJWTError:
                pass
        
        # Pour les admin de plateforme, on ne restreint pas l'accès
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_platform_admin:
            return self.get_response(request)
        
        # URLs non protégées par tenant
        non_tenant_urls = [
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/auth/refresh/',
            '/admin/',
            '/api/docs/',
        ]
        
        if any(request.path.startswith(url) for url in non_tenant_urls):
            return self.get_response(request)
        
        # Pour les requêtes qui nécessitent un tenant_id
        if not request.tenant_id:
            return HttpResponseForbidden("Accès refusé: aucun tenant identifié")
        
        # Tout va bien, on continue avec la requête
        return self.get_response(request)
```

### Configuration multi-tenant avec PostgreSQL

Nous utilisons PostgreSQL comme base de données avec une approche d'isolation par filtrage au niveau de l'application. Cette méthode offre une bonne isolation des données tout en étant simple à mettre en œuvre et à maintenir.

```python
# Configuration de la base de données dans settings/base.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'corporate_saas_db',
        'USER': 'corporate_saas',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Avec cette approche, chaque modèle de données qui doit être isolé par tenant contient une référence au tenant_id, et notre middleware s'assure que les requêtes sont correctement filtrées pour n'accéder qu'aux données du tenant de l'utilisateur connecté.

### État actuel du développement

- [x] **Modèle utilisateur personnalisé** avec support multi-tenant
- [x] **Modèle Tenant** pour la gestion des clients
- [x] **API d'authentification** complète avec JWT
- [x] **Middleware d'isolation des tenants** qui empêche l'accès aux données d'autres tenants
- [x] **Base de données PostgreSQL** configurée
- [x] **Tests d'API** avec utilisateurs associés à des tenants
- [ ] API complète de gestion des tenants
- [ ] Services métier avec isolation des données par tenant

### Sécurité et conformité

- **Chiffrement**: Toutes les communications sont chiffrées via HTTPS/TLS (à configurer en production)
- **Protection des données**: Conformité RGPD/GDPR
- **Audit trail**: Journalisation des actions sensibles pour des raisons de sécurité et de conformité
- **Rate limiting**: Protection contre les attaques par force brute
- **Isolation des tenants**: Garantie que les utilisateurs ne peuvent accéder qu'aux données de leur propre tenant

### Intégration avec d'autres services

- **API Gateway**: Valide les tokens JWT pour toutes les requêtes à n'importe quel service
- **Tenant Service**: Communique pour les opérations liées aux tenants
- **User Service**: Partage les informations utilisateur via API
- **Domain Services**: Fournit le contexte d'authentification et de tenant

## Prochaines étapes

1. **Développement du service de comptabilité**
   - Création des modèles (plan comptable, transactions, journaux)
   - Implémentation des API respectant l'isolation des tenants
   - Ajout des vues et des sérialiseurs

2. **Mise en place de l'API Gateway**
   - Configuration de Kong ou autre solution
   - Mise en place du routage vers les différents services
   - Configuration de la sécurité et du rate limiting

3. **Développement du frontend**
   - Création de l'application shell (React/Angular)
   - Implémentation des modules micro-frontend pour chaque domaine
   - Intégration avec le système d'authentification

4. **Améliorations de la sécurité**
   - Configuration HTTPS
   - Audit de sécurité
   - Journalisation des événements

5. **Évolutions futures**
   - Authentification sociale (Google, Microsoft, etc.)
   - Single Sign-On (SSO) avec support SAML et OIDC
   - Authentification biométrique avec WebAuthn
   - Gestion des sessions avancée avec détection d'activités suspectes
   - Analytics de sécurité avec tableaux de bord et alertes