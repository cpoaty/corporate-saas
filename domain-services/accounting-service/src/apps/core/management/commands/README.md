# Commandes d'importation du plan comptable OHADA

Ce répertoire contient des commandes Django pour importer différentes versions du plan comptable OHADA.

## Importation du plan comptable OHADA à 8 chiffres

La commande `import_ohada_8chiffres` permet d'importer le plan comptable OHADA avec des codes de compte à 8 chiffres, 
offrant une granularité plus fine que le plan comptable standard.

### Utilisation

```bash
python manage.py import_ohada_8chiffres --tenant-id <UUID_DU_TENANT>
```

### Options

- `--tenant-id` : UUID du tenant pour lequel importer le plan comptable (obligatoire)
- `--file` : Chemin personnalisé vers le fichier JSON (facultatif)
- `--replace` : Supprimer tous les comptes existants avant l'importation (facultatif)

### Exemple

```bash
# Importer pour un tenant spécifique
python manage.py import_ohada_8chiffres --tenant-id 284e521a-7899-4290-88e3-ea6a50913210

# Remplacer les comptes existants
python manage.py import_ohada_8chiffres --tenant-id 284e521a-7899-4290-88e3-ea6a50913210 --replace

# Utiliser un fichier personnalisé
python manage.py import_ohada_8chiffres --tenant-id 284e521a-7899-4290-88e3-ea6a50913210 --file /chemin/vers/mon_fichier.json
```

### Structure du fichier JSON

Le fichier JSON doit contenir un tableau d'objets avec les champs suivants :

```json
[
  {
    "code": "10000000",
    "libelle": "Capital"
  },
  {
    "code": "10100000", 
    "libelle": "Capital social"
  },
  ...
]
```

### Hiérarchie des comptes

La commande crée automatiquement une structure hiérarchique des comptes basée sur les codes :

- Niveau 1 : XX000000 (ex: 10000000)
- Niveau 2 : XXXX0000 (ex: 10100000)
- Niveau 3 : XXXXXX00 (ex: 10110000)
- Niveau 4 : XXXXXXXX (ex: 10110001)

Chaque compte est associé à son parent direct dans la hiérarchie.