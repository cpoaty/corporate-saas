# Documentation - Corporate SAAS - Module Comptabilité OHADA

## 1. Classification des comptes OHADA

### 1.1 Fonction `get_account_classification`

La fonction `get_account_classification` analyse un code de compte OHADA pour déterminer sa classification complète selon le référentiel OHADA. Elle retourne un dictionnaire contenant les informations suivantes :

- **type** : ACTIF, PASSIF, CHARGE, PRODUIT
- **category** : BRUT ou AMORTISSEMENT_DEPRECIATION
- **ref** : Référence pour les états financiers (ex: AE, BJ, TA)
- **normal_balance** : Solde normal du compte (DEBIT ou CREDIT)

Exemple d'utilisation :
```python
from apps.core.management.commands.import_ohada_avec_classification import get_account_classification

# Analyser un code de compte
account_code = "21540000"  # Matériel de bureau
classification = get_account_classification(account_code)

print(classification)
# Résultat :
# {
#   'type': 'ACTIF', 
#   'category': 'BRUT', 
#   'ref': 'AG', 
#   'normal_balance': 'DEBIT'
# }
```

### 1.2 Modèle Account - Nouveaux champs

Le modèle `Account` a été enrichi avec de nouveaux champs pour stocker les informations de classification OHADA :

- **ref_financial_statement** : Référence pour les états financiers (ex: AE, BJ, TA)
- **is_amortization_depreciation** : Indique si le compte est un compte d'amortissement ou de dépréciation
- **normal_balance** : Solde normal du compte (DEBIT ou CREDIT)

Ces champs sont automatiquement remplis lors de l'importation du plan comptable OHADA par la commande `import_ohada_avec_classification`.

## 2. Importation du plan comptable OHADA

### 2.1 Commande `import_ohada_avec_classification`

Cette commande permet d'importer le plan comptable OHADA à 8 chiffres avec les informations de classification détaillées.

Syntaxe :
```bash
python manage.py import_ohada_avec_classification --tenant-id <UUID> [options]
```

Options :
- `--tenant-id` (obligatoire) : UUID du tenant pour lequel importer le plan comptable
- `--file` : Chemin vers un fichier JSON personnalisé (utilise le fichier par défaut si non spécifié)
- `--replace` : Supprime les comptes existants avant l'importation (compatibilité)
- `--purge` : Nettoie tous les comptes, catégories et classes existants pour ce tenant avant l'importation

Exemple :
```bash
# Importer le plan comptable OHADA pour un tenant en nettoyant d'abord les données existantes
python manage.py import_ohada_avec_classification --tenant-id 3f9c5254-f5e7-4883-a860-8b5c9324b832 --purge
```

### 2.2 Structure du fichier JSON d'importation

Le fichier JSON doit contenir un tableau d'objets avec la structure suivante :
```json
[
  {
    "code": "10100000",
    "libelle": "Capital social"
  },
  {
    "code": "10400000",
    "libelle": "Primes liées au capital social"
  },
  ...
]
```

## 3. Gestion des tiers

### 3.1 Sérialiseur Tiers - Accepter le code du compte

Le sérialiseur `TiersSerializer` a été modifié pour accepter le code du compte au lieu de son UUID lors de la création d'un tiers. Un nouveau champ `account_code_input` a été ajouté au sérialiseur.

Exemple d'utilisation via l'API REST :
```json
{
  "code": "401ABC",
  "name": "ABC SARL",
  "type": "SUPPLIER",
  "account_code_input": "40100000",
  "address": "123 Rue Exemple, Ville",
  "email": "contact@abc.com",
  "phone": "+123456789",
  "is_active": true
}
```

### 3.2 Validation du code tiers

Le sérialiseur effectue les validations suivantes sur le code tiers :
- Doit commencer par 401 (fournisseur), 411 (client) ou 422 (personnel)
- Doit contenir au moins 6 caractères (préfixe + 3 lettres du nom)
- Les positions 4-6 doivent être les trois premières lettres du nom
- Le code doit être unique pour le tenant

### 3.3 Recherche du compte par code

Lors de la création d'un tiers, le sérialiseur :
1. Accepte le code du compte via le champ `account_code_input`
2. Recherche le compte correspondant à ce code pour le tenant spécifié
3. Crée le tiers en utilisant l'objet compte trouvé
4. Gère le cas où le compte n'existe pas avec un message d'erreur approprié

## 4. Migrations

Deux migrations ont été créées pour ajouter les nouveaux champs de classification au modèle Account :
- `0006_account_ohada_classification.py` : Migration vide qui sert de point d'ancrage
- `0007_add_account_classification_fields.py` : Ajoute les nouveaux champs au modèle Account

Pour appliquer ces migrations, exécutez :
```bash
python manage.py migrate core
```

## 5. Exemples d'utilisation

### 5.1 Importation du plan comptable avec classification

```bash
# Importer le plan comptable OHADA pour un tenant
python manage.py import_ohada_avec_classification --tenant-id <UUID> --purge
```

### 5.2 Création d'un tiers avec code de compte

```python
from rest_framework.test import APIClient
client = APIClient()

# Créer un tiers avec code de compte
response = client.post('/api/tiers/', {
    "code": "401ACM",
    "name": "ACME Corporation",
    "type": "SUPPLIER",
    "account_code_input": "40100000",
    "email": "contact@acme.com",
    "is_active": true
}, format='json')
```

### 5.3 Utilisation de la classification dans les états financiers

```python
from apps.core.models.account import Account

# Obtenir tous les comptes d'actif avec leur référence pour les états financiers
actif_accounts = Account.objects.filter(
    type='ASSET',
    tenant_id=tenant_id
).order_by('ref_financial_statement', 'code')

# Grouper par référence pour construire un bilan
from itertools import groupby
from django.db.models import Sum

accounts_by_ref = {}
for ref, accounts in groupby(actif_accounts, key=lambda a: a.ref_financial_statement):
    accounts_list = list(accounts)
    total = sum(account.get_balance() for account in accounts_list)
    accounts_by_ref[ref] = {
        'accounts': accounts_list,
        'total': total
    }
```