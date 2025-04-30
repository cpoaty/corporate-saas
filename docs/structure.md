@echo off
echo Création de la structure du projet Corporate SaaS...

:: Création du dossier racine
mkdir corporate-saas
cd corporate-saas

:: Core Services
mkdir core-services
mkdir core-services\auth-service
mkdir core-services\auth-service\src
type nul > core-services\auth-service\Dockerfile

mkdir core-services\tenant-service
mkdir core-services\tenant-service\src
type nul > core-services\tenant-service\Dockerfile

mkdir core-services\user-service
mkdir core-services\user-service\src
type nul > core-services\user-service\Dockerfile

:: Domain Services - Comptabilité
mkdir domain-services
mkdir domain-services\accounting-service
mkdir domain-services\accounting-service\src
mkdir domain-services\accounting-service\src\config
mkdir domain-services\accounting-service\src\config\settings
type nul > domain-services\accounting-service\src\config\settings\__init__.py
type nul > domain-services\accounting-service\src\config\settings\base.py
type nul > domain-services\accounting-service\src\config\settings\development.py
type nul > domain-services\accounting-service\src\config\settings\production.py
type nul > domain-services\accounting-service\src\config\urls.py
type nul > domain-services\accounting-service\src\config\wsgi.py

mkdir domain-services\accounting-service\src\apps
mkdir domain-services\accounting-service\src\apps\accounts
mkdir domain-services\accounting-service\src\apps\accounts\models
mkdir domain-services\accounting-service\src\apps\accounts\services
mkdir domain-services\accounting-service\src\apps\accounts\api
mkdir domain-services\accounting-service\src\apps\accounts\management
type nul > domain-services\accounting-service\src\apps\accounts\__init__.py
type nul > domain-services\accounting-service\src\apps\accounts\models\__init__.py
type nul > domain-services\accounting-service\src\apps\accounts\services\__init__.py
type nul > domain-services\accounting-service\src\apps\accounts\api\__init__.py

mkdir domain-services\accounting-service\src\apps\transactions
mkdir domain-services\accounting-service\src\apps\transactions\models
mkdir domain-services\accounting-service\src\apps\transactions\services
mkdir domain-services\accounting-service\src\apps\transactions\api
type nul > domain-services\accounting-service\src\apps\transactions\__init__.py
type nul > domain-services\accounting-service\src\apps\transactions\models\__init__.py

mkdir domain-services\accounting-service\src\apps\partners
mkdir domain-services\accounting-service\src\apps\partners\models
mkdir domain-services\accounting-service\src\apps\partners\services
mkdir domain-services\accounting-service\src\apps\partners\api
type nul > domain-services\accounting-service\src\apps\partners\__init__.py
type nul > domain-services\accounting-service\src\apps\partners\models\__init__.py

mkdir domain-services\accounting-service\src\apps\treasury
mkdir domain-services\accounting-service\src\apps\treasury\models
mkdir domain-services\accounting-service\src\apps\treasury\services
mkdir domain-services\accounting-service\src\apps\treasury\api
type nul > domain-services\accounting-service\src\apps\treasury\__init__.py
type nul > domain-services\accounting-service\src\apps\treasury\models\__init__.py

mkdir domain-services\accounting-service\src\apps\reports
mkdir domain-services\accounting-service\src\apps\reports\models
mkdir domain-services\accounting-service\src\apps\reports\services
mkdir domain-services\accounting-service\src\apps\reports\api
type nul > domain-services\accounting-service\src\apps\reports\__init__.py
type nul > domain-services\accounting-service\src\apps\reports\models\__init__.py

mkdir domain-services\accounting-service\src\apps\taxes
mkdir domain-services\accounting-service\src\apps\taxes\models
mkdir domain-services\accounting-service\src\apps\taxes\services
mkdir domain-services\accounting-service\src\apps\taxes\api
type nul > domain-services\accounting-service\src\apps\taxes\__init__.py
type nul > domain-services\accounting-service\src\apps\taxes\models\__init__.py

mkdir domain-services\accounting-service\src\utils
type nul > domain-services\accounting-service\src\utils\__init__.py
type nul > domain-services\accounting-service\src\manage.py

mkdir domain-services\accounting-service\tests
mkdir domain-services\accounting-service\tests\unit
mkdir domain-services\accounting-service\tests\integration
type nul > domain-services\accounting-service\Dockerfile

mkdir domain-services\accounting-service\requirements
type nul > domain-services\accounting-service\requirements\base.txt
type nul > domain-services\accounting-service\requirements\development.txt
type nul > domain-services\accounting-service\requirements\production.txt

:: Future Domain Services (placeholders)
mkdir domain-services\payroll-service
mkdir domain-services\payroll-service\src
type nul > domain-services\payroll-service\Dockerfile

mkdir domain-services\audit-service
mkdir domain-services\audit-service\src
type nul > domain-services\audit-service\Dockerfile

mkdir domain-services\archiving-service
mkdir domain-services\archiving-service\src
type nul > domain-services\archiving-service\Dockerfile

:: API Gateway
mkdir api-gateway
mkdir api-gateway\routes
mkdir api-gateway\policies
type nul > api-gateway\Dockerfile

:: Frontend
mkdir frontend
mkdir frontend\shell
mkdir frontend\shell\src
mkdir frontend\shell\src\app
mkdir frontend\shell\src\layout
mkdir frontend\shell\src\auth
mkdir frontend\shell\src\router
type nul > frontend\shell\src\App.js
mkdir frontend\shell\public
type nul > frontend\shell\package.json

mkdir frontend\shared
mkdir frontend\shared\src
mkdir frontend\shared\src\components
mkdir frontend\shared\src\hooks
mkdir frontend\shared\src\styles
mkdir frontend\shared\src\utils
type nul > frontend\shared\package.json

mkdir frontend\accounting
mkdir frontend\accounting\src
mkdir frontend\accounting\src\components
mkdir frontend\accounting\src\modules
mkdir frontend\accounting\src\modules\accounts
mkdir frontend\accounting\src\modules\transactions
mkdir frontend\accounting\src\modules\reports
mkdir frontend\accounting\src\modules\dashboard
mkdir frontend\accounting\src\services
type nul > frontend\accounting\src\index.js
type nul > frontend\accounting\package.json

mkdir frontend\payroll
mkdir frontend\payroll\src
type nul > frontend\payroll\package.json

mkdir frontend\audit
mkdir frontend\audit\src
type nul > frontend\audit\package.json

:: Infrastructure
mkdir infrastructure
mkdir infrastructure\kubernetes
mkdir infrastructure\kubernetes\core
mkdir infrastructure\kubernetes\accounting
mkdir infrastructure\kubernetes\shared

mkdir infrastructure\terraform

mkdir infrastructure\ci-cd
mkdir infrastructure\ci-cd\core-services
mkdir infrastructure\ci-cd\accounting-service
mkdir infrastructure\ci-cd\frontend-shell
mkdir infrastructure\ci-cd\frontend-accounting

echo Structure du projet créée avec succès!