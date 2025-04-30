# Template de service backend 
 
Ce template sert de base pour cr�er un nouveau service backend dans l'architecture Corporate SaaS. 
 
## Structure 
 
```bash 
service-name/ 
��� src/ 
�   ��� config/ 
�   �   ��� settings/ 
�   �   �   ��� __init__.py 
�   �   �   ��� base.py 
�   �   �   ��� development.py 
�   �   �   ��� production.py 
�   �   ��� urls.py 
�   �   ��� wsgi.py 
�   ��� apps/ 
�   �   ��� core/ 
�   ��� utils/ 
�   ��� manage.py 
��� tests/ 
��� Dockerfile 
��� requirements/ 
    ��� base.txt 
    ��� development.txt 
    ��� production.txt 
``` 
