# Architecture Corporate SaaS 
 
## Architecture hybride micro-services / micro-frontends 
 
Cette plateforme utilise une architecture hybride qui combine: 
 
- **Micro-frontends** pour une exp�rience utilisateur coh�rente et modulaire 
- **Micro-services backend** pour le d�veloppement ind�pendant des domaines m�tier 
- **Infrastructure multi-tenant partag�e** pour l'optimisation des ressources 
 
### Diagramme d'architecture 
 
```text 
�����������������������������������������������������Ŀ 
�                 Shell Application                    � 
�      (React.js + Micro-frontends + Design System)    � 
������������������������������������������������������� 
         �               �             � 
��������������Ŀ �������������Ŀ ���������������Ŀ 
� Comptabilit�  � �    Paie      � �  Autres Domaines� 
� Micro-frontend� �Micro-frontend� �  Micro-frontends� 
����������������� ���������������� ������������������ 
         �               �             � 
         �        �������������������������Ŀ 
         �        �     API Gateway          � 
         �        ���������������������������� 
         �               � 
��������������Ŀ �������������Ŀ ���������������Ŀ 
�  Services     � �  Services    � �   Services     � 
�  Core         � �  Comptabilit�� �   Autres       � 
� (Auth, Tenant)� �              � �   Domaines     � 
����������������� ���������������� ������������������ 
         �               �             � 
��������������������������������������������������Ŀ 
�         Infrastructure Multi-tenant Partag�e         � 
�     (Bases de donn�es, Stockage, Cache, Files)       � 
������������������������������������������������������� 
``` 
