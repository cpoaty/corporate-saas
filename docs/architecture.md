# Architecture Corporate SaaS 
 
## Architecture hybride micro-services / micro-frontends 
 
Cette plateforme utilise une architecture hybride qui combine: 
 
- **Micro-frontends** pour une exp‚rience utilisateur coh‚rente et modulaire 
- **Micro-services backend** pour le d‚veloppement ind‚pendant des domaines m‚tier 
- **Infrastructure multi-tenant partag‚e** pour l'optimisation des ressources 
 
### Diagramme d'architecture 
 
```text 
ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿ 
³                 Shell Application                    ³ 
³      (React.js + Micro-frontends + Design System)    ³ 
ÀÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ 
         ³               ³             ³ 
ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿ ÚÄÄÄÄÄÄÄÄÄÄÄÄÄ¿ ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿ 
³ Comptabilit‚  ³ ³    Paie      ³ ³  Autres Domaines³ 
³ Micro-frontend³ ³Micro-frontend³ ³  Micro-frontends³ 
ÀÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÙ ÀÄÄÄÄÄÄÂÄÄÄÄÄÄÄÙ ÀÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÙ 
         ³               ³             ³ 
         ³        ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿ 
         ³        ³     API Gateway          ³ 
         ³        ÀÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ 
         ³               ³ 
ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿ ÚÄÄÄÄÄÄÄÄÄÄÄÄÄ¿ ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿ 
³  Services     ³ ³  Services    ³ ³   Services     ³ 
³  Core         ³ ³  Comptabilit‚³ ³   Autres       ³ 
³ (Auth, Tenant)³ ³              ³ ³   Domaines     ³ 
ÀÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÙ ÀÄÄÄÄÄÄÂÄÄÄÄÄÄÄÙ ÀÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÙ 
         ³               ³             ³ 
ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿ 
³         Infrastructure Multi-tenant Partag‚e         ³ 
³     (Bases de donn‚es, Stockage, Cache, Files)       ³ 
ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ 
``` 
