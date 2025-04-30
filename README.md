# Corporate SaaS Platform 
 
Une plateforme SaaS modulaire multi-domaines incluant comptabilit‚, paie, audit et archivage. 
 
## Structure du projet 
 
Ce projet est organis‚ selon une architecture de micro-services et micro-frontends: 
 
### Core Services 
- Auth Service - Service d'authentification et autorisation 
- Tenant Service - Gestion des tenants 
- User Service - Gestion des utilisateurs 
 
### Domain Services 
- Accounting Service - Service de comptabilit‚ 
 
### Frontend 
- Frontend Shell - Application conteneur 
- Shared Components - BibliothŠque de composants partag‚s 
- Accounting Frontend - Module comptabilit‚ 
 
### Infrastructure 
- API Gateway - Configuration du gateway API 
- Infrastructure - Code d'infrastructure (Kubernetes, Terraform) 
