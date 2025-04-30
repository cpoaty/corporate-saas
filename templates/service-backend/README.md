# Template de service backend 
 
Ce template sert de base pour cr‚er un nouveau service backend dans l'architecture Corporate SaaS. 
 
## Structure 
 
```bash 
service-name/ 
ÃÄÄ src/ 
³   ÃÄÄ config/ 
³   ³   ÃÄÄ settings/ 
³   ³   ³   ÃÄÄ __init__.py 
³   ³   ³   ÃÄÄ base.py 
³   ³   ³   ÃÄÄ development.py 
³   ³   ³   ÀÄÄ production.py 
³   ³   ÃÄÄ urls.py 
³   ³   ÀÄÄ wsgi.py 
³   ÃÄÄ apps/ 
³   ³   ÀÄÄ core/ 
³   ÃÄÄ utils/ 
³   ÀÄÄ manage.py 
ÃÄÄ tests/ 
ÃÄÄ Dockerfile 
ÀÄÄ requirements/ 
    ÃÄÄ base.txt 
    ÃÄÄ development.txt 
    ÀÄÄ production.txt 
``` 
