import json
import re

def transform_plan_comptable(json_data):
    """
    Transforme un plan comptable OHADA en conservant les libellés originaux
    mais en formatant les codes sur 8 chiffres
    """
    accounts = {}
    
    def extract_accounts(data, parent_key=""):
        """Extraire tous les comptes à plat avec leur libellé original"""
        if isinstance(data, dict):
            for key, value in data.items():
                # Vérifier si la clé commence par un chiffre (potentiellement un code de compte)
                code_match = re.match(r'^(\d+)', key)
                
                if code_match:
                    code = code_match.group(1)
                    # Extraire le libellé (tout ce qui est après le code)
                    libelle = key[len(code):].strip()
                    
                    # Si le libellé est vide et que la valeur est une chaîne, utiliser la valeur comme libellé
                    if not libelle and isinstance(value, str):
                        libelle = value
                    
                    # Formater le code sur 8 chiffres si sa longueur est <= 8
                    if len(code) <= 8:
                        formatted_code = code.ljust(8, '0')
                        accounts[formatted_code] = libelle
                
                # Traiter récursivement les sous-dictionnaires
                if isinstance(value, dict):
                    extract_accounts(value)
    
    # Début du traitement
    extract_accounts(json_data)
    
    # Convertir le dictionnaire en liste triée par code
    sorted_accounts = [{"code": code, "libelle": libelle} for code, libelle in sorted(accounts.items())]
    
    return sorted_accounts

def format_output(accounts):
    """
    Formate la sortie en JSON bien structuré
    """
    return json.dumps(accounts, indent=2, ensure_ascii=False)

# Charger les données du fichier JSON original
with open('plan_comptable_ohada.json', 'r', encoding='utf-8') as f:
    original_data = json.load(f)

# Transformer le plan comptable
transformed_accounts = transform_plan_comptable(original_data)

# Afficher le nombre de comptes transformés
print(f"Nombre de comptes dans le plan comptable transformé: {len(transformed_accounts)}")

# Écrire le résultat dans un nouveau fichier
with open('plan_comptable_ohada_8chiffres.json', 'w', encoding='utf-8') as f:
    f.write(format_output(transformed_accounts))

print("Transformation terminée. Le résultat est enregistré dans 'plan_comptable_ohada_8chiffres.json'")

# Afficher quelques exemples de comptes transformés
print("\nExemples de comptes transformés:")
for i in range(min(10, len(transformed_accounts))):
    print(f"{transformed_accounts[i]['code']} - {transformed_accounts[i]['libelle']}")