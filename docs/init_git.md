@echo off
echo Initialisation des dépôts Git pour chaque sous-projet...

cd corporate-saas

:: Core Services
cd core-services\auth-service
git init
echo node_modules/ > .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo .env >> .gitignore
echo # Auth Service > README.md
git add .
git commit -m "Initial commit for Auth Service"
cd ..\..

cd core-services\tenant-service
git init
echo node_modules/ > .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo .env >> .gitignore
echo # Tenant Service > README.md
git add .
git commit -m "Initial commit for Tenant Service"
cd ..\..

cd core-services\user-service
git init
echo node_modules/ > .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo .env >> .gitignore
echo # User Service > README.md
git add .
git commit -m "Initial commit for User Service"
cd ..\..

:: Accounting Service
cd domain-services\accounting-service
git init
echo node_modules/ > .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo .env >> .gitignore
echo venv/ >> .gitignore
echo .vscode/ >> .gitignore
echo # Accounting Service > README.md
git add .
git commit -m "Initial commit for Accounting Service"
cd ..\..

:: Frontend Shell
cd frontend\shell
git init
echo node_modules/ > .gitignore
echo build/ >> .gitignore
echo .env >> .gitignore
echo .env.local >> .gitignore
echo # Frontend Shell Application > README.md
git add .
git commit -m "Initial commit for Frontend Shell"
cd ..\..

cd frontend\shared
git init
echo node_modules/ > .gitignore
echo dist/ >> .gitignore
echo # Shared Component Library > README.md
git add .
git commit -m "Initial commit for Shared Component Library"
cd ..\..

cd frontend\accounting
git init
echo node_modules/ > .gitignore
echo build/ >> .gitignore
echo .env >> .gitignore
echo # Accounting Frontend Module > README.md
git add .
git commit -m "Initial commit for Accounting Frontend"
cd ..\..

:: API Gateway
cd api-gateway
git init
echo node_modules/ > .gitignore
echo # API Gateway Configuration > README.md
git add .
git commit -m "Initial commit for API Gateway"
cd ..

:: Infrastructure
cd infrastructure
git init
echo .terraform/ > .gitignore
echo *.tfstate >> .gitignore
echo *.tfstate.backup >> .gitignore
echo # Infrastructure as Code > README.md
git add .
git commit -m "Initial commit for Infrastructure"
cd ..

echo Tous les dépôts Git ont été initialisés avec succès!