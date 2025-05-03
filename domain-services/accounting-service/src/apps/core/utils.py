"""
Fonctions utilitaires pour l'application comptable.
Ce module contient des fonctions réutilisables pour le formatage et la validation
des données comptables, assurant la cohérence dans l'application.
"""

import re
import uuid
from datetime import datetime


def format_accounting_name(name):
    """
    Formate un libellé selon les conventions comptables.
    
    Args:
        name (str): Le libellé à formater
        
    Returns:
        str: Le libellé formaté selon les conventions (title case, sans caractères spéciaux excessifs)
    """
    if not name:
        return name
    
    # 1. Première lettre de chaque mot en majuscule, reste en minuscule
    name = name.title()
    
    # 2. Supprimer les caractères spéciaux indésirables
    name = re.sub(r'[^\w\s\-\.,&\(\)]', '', name)
    
    # 3. Supprimer les espaces multiples
    while "  " in name:
        name = name.replace("  ", " ")
    
    # 4. Supprimer les espaces en début et fin
    name = name.strip()
    
    return name


def format_accounting_code(code, account_prefix=None, desired_length=None):
    """
    Formate un code selon les conventions comptables.
    
    Args:
        code (str): Le code à formater
        account_prefix (str, optional): Préfixe de compte à ajouter si nécessaire
        desired_length (int, optional): Longueur souhaitée pour le code final
        
    Returns:
        str: Le code formaté (majuscules, longueur fixe si spécifiée)
    """
    if not code:
        return code
    
    # 1. Convertir en majuscules
    code = code.upper()
    
    # 2. Supprimer les caractères non alphanumériques
    code = re.sub(r'[^\w]', '', code)
    
    # 3. Ajouter le préfixe de compte si nécessaire
    if account_prefix and not code.startswith(account_prefix):
        code = f"{account_prefix}{code}"
    
    # 4. Ajuster à la longueur souhaitée si spécifiée
    if desired_length:
        if len(code) < desired_length:
            # Compléter avec des zéros
            code = code.ljust(desired_length, '0')
        elif len(code) > desired_length:
            # Tronquer
            code = code[:desired_length]
    
    return code


def generate_reference(prefix="", length=10):
    """
    Génère une référence unique pour les documents comptables.
    
    Args:
        prefix (str): Préfixe à ajouter à la référence (ex: 'INV', 'PO')
        length (int): Longueur souhaitée pour la partie aléatoire
        
    Returns:
        str: Référence unique au format PREFIX-YYYYMMDD-XXXXX
    """
    today = datetime.now().strftime("%Y%m%d")
    unique_part = str(uuid.uuid4().hex)[:length]
    
    if prefix:
        return f"{prefix.upper()}-{today}-{unique_part.upper()}"
    else:
        return f"{today}-{unique_part.upper()}"


def calculate_vat(amount, rate=0.18):
    """
    Calcule la TVA sur un montant donné.
    
    Args:
        amount (float): Montant HT
        rate (float): Taux de TVA (par défaut: 18%)
        
    Returns:
        tuple: (montant HT, montant de TVA, montant TTC)
    """
    vat = round(amount * rate, 2)
    total = amount + vat
    return (amount, vat, total)