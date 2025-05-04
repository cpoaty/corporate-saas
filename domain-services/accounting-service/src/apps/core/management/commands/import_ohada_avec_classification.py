import json
import os
import uuid
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from apps.core.models.account import AccountClass, AccountCategory, Account, AccountType


def get_account_classification(code):
    """
    Détermine la classification complète d'un compte selon le plan comptable OHADA.
    
    Args:
        code (str): Code du compte (préférablement 8 chiffres)
        
    Returns:
        dict: Classification complète du compte
            - type: ACTIF, PASSIF, CHARGE, PRODUIT
            - category: Catégorie (BRUT, AMORTISSEMENT, etc.)
            - ref: Référence pour les états financiers
            - normal_balance: Solde normal (DEBIT ou CREDIT)
    """
    # Valeurs par défaut
    account_info = {
        "type": "INCONNU",
        "category": "INCONNU",
        "ref": "INCONNU",
        "normal_balance": "INCONNU"
    }
    
    if not code or not isinstance(code, str):
        return account_info
        
    # Normaliser le code (retirer les espaces, etc.)
    code = code.strip()
    
    # Extraire les premiers chiffres pour l'analyse
    class_digit = int(code[0]) if code and code[0].isdigit() else 0
    two_digits = int(code[:2]) if len(code) >= 2 and code[:2].isdigit() else 0
    three_digits = int(code[:3]) if len(code) >= 3 and code[:3].isdigit() else 0
    
    # CLASSE 1: TYPE PASSIF
    if class_digit == 1:
        account_info["type"] = "PASSIF"
        account_info["normal_balance"] = "CREDIT"
        
        # Références pour les comptes de classe 1
        if 101 <= two_digits <= 104:
            account_info["ref"] = "CA"
        elif two_digits == 109:
            account_info["ref"] = "CB"
        elif two_digits == 105:
            account_info["ref"] = "CD"
        elif two_digits == 106:
            account_info["ref"] = "CE"
        elif two_digits in [111, 112, 113]:
            account_info["ref"] = "CF"
        elif two_digits == 118:
            account_info["ref"] = "CG"
        elif two_digits in [121, 129]:
            account_info["ref"] = "CH"
        elif two_digits in [131, 139]:
            account_info["ref"] = "CJ"
        elif two_digits == 14:
            account_info["ref"] = "CL"
        elif two_digits == 15:
            account_info["ref"] = "CM"
        elif two_digits == 16 or two_digits in [181, 182, 183, 184]:
            account_info["ref"] = "DA"
        elif two_digits == 17:
            account_info["ref"] = "DB"
        elif two_digits == 19:
            account_info["ref"] = "DC"
    
    # CLASSE 2: TYPE ACTIF
    elif class_digit == 2:
        account_info["type"] = "ACTIF"
        account_info["normal_balance"] = "DEBIT"
        
        # Déterminer si BRUT ou AMORTISSEMENT/DEPRECIATION
        if code.startswith("28") or code.startswith("29"):
            account_info["category"] = "AMORTISSEMENT_DEPRECIATION"
        else:
            account_info["category"] = "BRUT"
        
        # Références pour les comptes de classe 2
        if three_digits in [211, 218] or code.startswith("2181") or code.startswith("2191"):
            if code.startswith("28") or code.startswith("29"):
                account_info["ref"] = "AE"  # Amortissements/dépréciations
            else:
                account_info["ref"] = "AE"  # Brut
                
        elif three_digits in [212, 213, 214] or code.startswith("2193"):
            if code.startswith("28") or code.startswith("29"):
                account_info["ref"] = "AF"  # Amortissements/dépréciations
            else:
                account_info["ref"] = "AF"  # Brut
                
        elif three_digits in [215, 216]:
            if code.startswith("28") or code.startswith("29"):
                account_info["ref"] = "AG"  # Amortissements/dépréciations
            else:
                account_info["ref"] = "AG"  # Brut
                
        elif three_digits == 217 or (three_digits == 218 and not code.startswith("2181")) or code.startswith("2198"):
            if code.startswith("28") or code.startswith("29"):
                account_info["ref"] = "AH"  # Amortissements/dépréciations
            else:
                account_info["ref"] = "AH"  # Brut
                
        elif two_digits == 22:
            if code.startswith("28") or code.startswith("29"):
                account_info["ref"] = "AJ"  # Amortissements/dépréciations
            else:
                account_info["ref"] = "AJ"  # Brut
                
        elif three_digits in [231, 232, 233, 237] or code.startswith("2391") or code.startswith("2392") or code.startswith("2393"):
            if code.startswith("28") or code.startswith("29"):
                account_info["ref"] = "AK"  # Amortissements/dépréciations
            else:
                account_info["ref"] = "AK"  # Brut
                
        elif three_digits in [234, 235, 238] or code.startswith("2394") or code.startswith("2395") or code.startswith("2398"):
            if code.startswith("28") or code.startswith("29"):
                account_info["ref"] = "AL"  # Amortissements/dépréciations
            else:
                account_info["ref"] = "AL"  # Brut
                
        elif two_digits == 24 and not (three_digits == 245 or code.startswith("2495")):
            if code.startswith("28") or code.startswith("29"):
                account_info["ref"] = "AM"  # Amortissements/dépréciations
            else:
                account_info["ref"] = "AM"  # Brut
                
        elif three_digits == 245 or code.startswith("2495"):
            if code.startswith("28") or code.startswith("29"):
                account_info["ref"] = "AN"  # Amortissements/dépréciations
            else:
                account_info["ref"] = "AN"  # Brut
                
        elif three_digits in [251, 252]:
            if code.startswith("29"):
                account_info["ref"] = "AP"  # Dépréciations
            else:
                account_info["ref"] = "AP"  # Brut
                
        elif two_digits == 26:
            if code.startswith("29"):
                account_info["ref"] = "AR"  # Dépréciations
            else:
                account_info["ref"] = "AR"  # Brut
                
        elif two_digits == 27:
            if code.startswith("29"):
                account_info["ref"] = "AS"  # Dépréciations
            else:
                account_info["ref"] = "AS"  # Brut
    
    # CLASSES 3, 4, 5 : TYPE ACTIF
    elif class_digit in [3, 4, 5]:
        # Cas spéciaux pour la classe 4/5 PASSIF
        if code.startswith("481") or code.startswith("482") or code.startswith("484") or code.startswith("4998"):
            account_info["type"] = "PASSIF"
            account_info["normal_balance"] = "CREDIT"
            account_info["ref"] = "DH"
        elif code.startswith("419"):
            account_info["type"] = "PASSIF"
            account_info["normal_balance"] = "CREDIT"
            account_info["ref"] = "DI"
        elif code.startswith("40") and not code.startswith("409"):
            account_info["type"] = "PASSIF"
            account_info["normal_balance"] = "CREDIT"
            account_info["ref"] = "DJ"
        elif code.startswith("42") or code.startswith("43") or code.startswith("44"):
            account_info["type"] = "PASSIF"
            account_info["normal_balance"] = "CREDIT"
            account_info["ref"] = "DK"
        elif code.startswith("185") or code.startswith("45") or code.startswith("46") or (code.startswith("47") and not code.startswith("479")):
            account_info["type"] = "PASSIF"
            account_info["normal_balance"] = "CREDIT"
            account_info["ref"] = "DM"
        elif code.startswith("499") and not code.startswith("4998") or code.startswith("599"):
            account_info["type"] = "PASSIF"
            account_info["normal_balance"] = "CREDIT"
            account_info["ref"] = "DN"
        elif code.startswith("564") or code.startswith("565"):
            account_info["type"] = "PASSIF"
            account_info["normal_balance"] = "CREDIT"
            account_info["ref"] = "DQ"
        elif code.startswith("52") or code.startswith("53") or code.startswith("54") or code.startswith("561") or code.startswith("566"):
            account_info["type"] = "PASSIF"
            account_info["normal_balance"] = "CREDIT"
            account_info["ref"] = "DR"
        elif code.startswith("479"):
            account_info["type"] = "PASSIF"
            account_info["normal_balance"] = "CREDIT"
            account_info["ref"] = "DV"
        
        # TYPE ACTIF pour autres comptes de classe 3, 4, 5
        else:
            account_info["type"] = "ACTIF"
            account_info["normal_balance"] = "DEBIT"
            
            # Determiner si c'est un compte de BRUT ou AMORTISSEMENT/DEPRECIATION
            if code.startswith("39") or code.startswith("49") or code.startswith("59"):
                account_info["category"] = "AMORTISSEMENT_DEPRECIATION"
            else:
                account_info["category"] = "BRUT"
            
            # Références pour les comptes de classe 3, 4, 5 (ACTIF)
            if code.startswith("485") or code.startswith("488"):
                account_info["ref"] = "BA"
            elif code.startswith("31") or code.startswith("32") or code.startswith("33") or code.startswith("34") or code.startswith("35") or code.startswith("36") or code.startswith("37") or code.startswith("38"):
                account_info["ref"] = "BB"
            elif code.startswith("409"):
                account_info["ref"] = "BH"
            elif code.startswith("41") and not code.startswith("419"):
                account_info["ref"] = "BI"
            elif code.startswith("185") or code.startswith("42") or code.startswith("43") or code.startswith("44") or code.startswith("45") or code.startswith("46") or (code.startswith("47") and not code.startswith("478")):
                account_info["ref"] = "BJ"
            elif code.startswith("50"):
                account_info["ref"] = "BQ"
            elif code.startswith("51"):
                account_info["ref"] = "BR"
            elif code.startswith("52") or code.startswith("53") or code.startswith("54") or code.startswith("55") or code.startswith("57") or code.startswith("581") or code.startswith("582"):
                account_info["ref"] = "BS"
            elif code.startswith("478"):
                account_info["ref"] = "BU"
    
    # CLASSE 6: TYPE CHARGE
    elif class_digit == 6:
        account_info["type"] = "CHARGE"
        account_info["normal_balance"] = "DEBIT"
        
        # Références pour les comptes de classe 6
        if code.startswith("601"):
            account_info["ref"] = "RA"
        elif code.startswith("6031"):
            account_info["ref"] = "RB"
        elif code.startswith("602"):
            account_info["ref"] = "RC"
        elif code.startswith("6032"):
            account_info["ref"] = "RD"
        elif code.startswith("604") or code.startswith("605") or code.startswith("608"):
            account_info["ref"] = "RE"
        elif code.startswith("6033"):
            account_info["ref"] = "RF"
        elif code.startswith("61"):
            account_info["ref"] = "RG"
        elif code.startswith("62") or code.startswith("63"):
            account_info["ref"] = "RH"
        elif code.startswith("64"):
            account_info["ref"] = "RI"
        elif code.startswith("65"):
            account_info["ref"] = "RJ"
        elif code.startswith("66"):
            account_info["ref"] = "RK"
        elif code.startswith("681") or code.startswith("691"):
            account_info["ref"] = "RL"
        elif code.startswith("67"):
            account_info["ref"] = "RM"
        elif code.startswith("697"):
            account_info["ref"] = "RN"
        elif code.startswith("81"):
            account_info["ref"] = "RO"
        elif code.startswith("83") or code.startswith("85"):
            account_info["ref"] = "RP"
        elif code.startswith("87"):
            account_info["ref"] = "RQ"
        elif code.startswith("89"):
            account_info["ref"] = "RS"
    
    # CLASSE 7: TYPE PRODUIT
    elif class_digit == 7:
        account_info["type"] = "PRODUIT"
        account_info["normal_balance"] = "CREDIT"
        
        # Références pour les comptes de classe 7
        if code.startswith("701"):
            account_info["ref"] = "TA"
        elif code.startswith("702") or code.startswith("703") or code.startswith("704"):
            account_info["ref"] = "TB"
        elif code.startswith("705") or code.startswith("706"):
            account_info["ref"] = "TC"
        elif code.startswith("707"):
            account_info["ref"] = "TD"
        elif code.startswith("73"):
            account_info["ref"] = "TE"
        elif code.startswith("72"):
            account_info["ref"] = "TF"
        elif code.startswith("71"):
            account_info["ref"] = "TG"
        elif code.startswith("75"):
            account_info["ref"] = "TI"
        elif code.startswith("791") or code.startswith("798") or code.startswith("799"):
            account_info["ref"] = "TJ"
        elif code.startswith("77"):
            account_info["ref"] = "TK"
        elif code.startswith("797"):
            account_info["ref"] = "TL"
        elif code.startswith("787"):
            account_info["ref"] = "TM"
        elif code.startswith("82"):
            account_info["ref"] = "TN"
        elif code.startswith("84") or code.startswith("86") or code.startswith("88"):
            account_info["ref"] = "TO"
    
    # CLASSE 8: TYPE SPECIAL
    elif class_digit == 8:
        # Classification en fonction des sous-catégories
        if code.startswith("82") or code.startswith("84") or code.startswith("86") or code.startswith("88"):
            account_info["type"] = "PRODUIT"
            account_info["normal_balance"] = "CREDIT"
        elif code.startswith("81") or code.startswith("83") or code.startswith("85") or code.startswith("87") or code.startswith("89"):
            account_info["type"] = "CHARGE"
            account_info["normal_balance"] = "DEBIT"
        else:
            account_info["type"] = "SPECIAL"
            account_info["normal_balance"] = "VARIABLE"
    
    return account_info


def update_account_import_script():
    """
    Met à jour le script d'importation du plan comptable pour utiliser
    la classification détaillée basée sur le plan comptable OHADA
    """
    # Exemple de mise à jour d'un Account lors de l'importation
    # Dans votre script d'importation, remplacez le code existant par:
    
    """
    # Pour chaque compte dans le fichier JSON
    for account_data in accounts_data:
        code = account_data.get('code', '').strip()
        
        # Obtenez la classification complète
        classification = get_account_classification(code)
        
        # Créez ou mettez à jour le compte
        account = Account(
            code=code,
            name=account_data.get('name', ''),
            description=account_data.get('description', ''),
            
            # Utilisez la classification détaillée
            type=classification['type'],
            normal_balance=classification['normal_balance'],
            ref_financial_statement=classification['ref'],
            is_amortization=classification['category'] == 'AMORTISSEMENT_DEPRECIATION',
            
            # Autres champs selon votre modèle Account
            tenant_id=tenant_id,
            is_active=True
        )
        
        # Sauvegardez le compte
        account.save()
    """


class Command(BaseCommand):
    help = 'Importe le plan comptable OHADA avec codes à 8 chiffres'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant-id',
            type=str,
            required=True,
            help='UUID du tenant pour lequel importer le plan comptable'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Chemin vers le fichier JSON (facultatif, utilise le fichier par défaut si non spécifié)'
        )
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Supprimer tous les comptes existants avant import'
        )
        parser.add_argument(
            '--purge',
            action='store_true',
            help='Nettoyer tous les comptes existants pour ce tenant avant import'
        )

    def purge_accounts(self, tenant_id):
        """
        Supprime tous les comptes, catégories et classes existants pour un tenant donné
        """
        try:
            with transaction.atomic():
                deleted_accounts = Account.objects.filter(tenant_id=tenant_id).delete()[0]
                deleted_categories = AccountCategory.objects.filter(tenant_id=tenant_id).delete()[0]
                deleted_classes = AccountClass.objects.filter(tenant_id=tenant_id).delete()[0]
                
                return deleted_accounts, deleted_categories, deleted_classes
        except Exception as e:
            raise CommandError(f"Erreur lors de la suppression des comptes: {str(e)}")

    def handle(self, *args, **options):
        tenant_id = options['tenant_id']
        try:
            tenant_uuid = uuid.UUID(tenant_id)
        except ValueError:
            raise CommandError(f"'{tenant_id}' n'est pas un UUID valide")

        # Déterminer le chemin du fichier
        if options.get('file'):
            json_file_path = options['file']
        else:
            json_file_path = os.path.join(settings.BASE_DIR, 'data', 'plan_comptable_ohada_8chiffres.json')
            # Si le fichier n'est pas trouvé, essayer un autre chemin
            if not os.path.exists(json_file_path):
                current_dir = os.path.dirname(os.path.abspath(__file__))
                json_file_path = os.path.join(current_dir, '..', '..', '..', '..', 'data', 'plan_comptable_ohada_8chiffres.json')

        # Vérifier que le fichier existe
        if not os.path.exists(json_file_path):
            raise CommandError(f"Le fichier {json_file_path} n'existe pas")

        try:
            # Lire le fichier JSON
            with open(json_file_path, 'r', encoding='utf-8') as file:
                accounts_data = json.load(file)

            # Option --purge : Supprimer tous les comptes existants
            if options['purge']:
                self.stdout.write(self.style.WARNING(f"Nettoyage de tous les comptes existants pour le tenant {tenant_id}..."))
                deleted_accounts, deleted_categories, deleted_classes = self.purge_accounts(tenant_uuid)
                self.stdout.write(self.style.WARNING(
                    f"Suppression effectuée: {deleted_accounts} comptes, {deleted_categories} catégories, "
                    f"{deleted_classes} classes supprimés."
                ))
            # Option --replace : Supprimer les comptes avant import (maintenu pour compatibilité)
            elif options['replace']:
                self.stdout.write(self.style.WARNING(f"Suppression des comptes existants pour le tenant {tenant_id}..."))
                with transaction.atomic():
                    Account.objects.filter(tenant_id=tenant_uuid).delete()
                    AccountCategory.objects.filter(tenant_id=tenant_uuid).delete()
                    AccountClass.objects.filter(tenant_id=tenant_uuid).delete()

            # Création des comptes
            self.stdout.write(self.style.SUCCESS(f"Début de l'importation des comptes à 8 chiffres..."))
            
            # Utiliser une transaction pour garantir l'intégrité des données
            with transaction.atomic():
                self.import_accounts(accounts_data, tenant_uuid)

            self.stdout.write(self.style.SUCCESS(f"Importation terminée avec succès! {len(accounts_data)} comptes importés."))

        except Exception as e:
            raise CommandError(f"Erreur lors de l'importation: {str(e)}")

    def import_accounts(self, accounts_data, tenant_id):
        """
        Importe les comptes à partir des données JSON
        """
        # Dictionnaire pour suivre les classes, catégories et comptes créés
        classes = {}
        categories = {}
        parent_accounts = {}
        
        # Compter les comptes traités
        count = 0
        total = len(accounts_data)
        
        for account_data in accounts_data:
            code = account_data['code']
            name = account_data['libelle']
            
            count += 1
            if count % 100 == 0:
                self.stdout.write(f"Traitement: {count}/{total} comptes...")
            
            # Déterminer la classe (premier chiffre)
            class_number = int(code[0])
            
            # Créer ou récupérer la classe
            if class_number not in classes:
                class_name = self.get_class_name(class_number)
                classes[class_number] = self.get_or_create_class(tenant_id, class_number, class_name)
            
            account_class = classes[class_number]
            
            # Obtenir la classification détaillée du compte selon OHADA
            classification = get_account_classification(code)
            
            # Convertir le type OHADA en type AccountType de Django
            account_type = self.convert_ohada_type_to_account_type(classification['type'])
            
            # Déterminer la catégorie (2 premiers chiffres)
            category_code = code[:2]
            
            # Créer ou récupérer la catégorie si elle n'existe pas
            if category_code not in categories:
                # Chercher un compte avec le même code de catégorie pour obtenir le libellé
                category_name = self.find_category_name(accounts_data, category_code)
                categories[category_code] = self.get_or_create_category(
                    tenant_id, account_class, category_code, category_name
                )
            
            category = categories[category_code]
            
            # Déterminer le niveau hiérarchique et le compte parent
            level, parent_code = self.determine_level_and_parent(code)
            
            # Créer ou récupérer le compte parent si nécessaire
            parent = None
            if parent_code and parent_code in parent_accounts:
                parent = parent_accounts[parent_code]
            
            # Créer le compte avec les informations détaillées
            account = self.create_account(
                tenant_id=tenant_id,
                code=code,
                name=name,
                account_class=account_class,
                category=category,
                account_type=account_type,
                level=level,
                parent=parent,
                ref_financial_statement=classification['ref'],
                is_amortization=classification['category'] == 'AMORTISSEMENT_DEPRECIATION',
                normal_balance=classification['normal_balance']
            )
            
            # Stocker le compte pour qu'il puisse servir de parent
            parent_accounts[code] = account
            
    def convert_ohada_type_to_account_type(self, ohada_type):
        """Convertit le type OHADA en type AccountType de Django"""
        type_mapping = {
            'ACTIF': AccountType.ASSET,
            'PASSIF': AccountType.LIABILITY,
            'CHARGE': AccountType.EXPENSE,
            'PRODUIT': AccountType.REVENUE,
            'SPECIAL': AccountType.EQUITY  # Par défaut
        }
        return type_mapping.get(ohada_type, AccountType.ASSET)

    def get_class_name(self, class_number):
        """Retourne le nom de la classe basé sur le numéro"""
        class_names = {
            1: "Comptes de capitaux",
            2: "Comptes d'actifs immobilisés",
            3: "Comptes de stocks",
            4: "Comptes de tiers",
            5: "Comptes de trésorerie",
            6: "Comptes de charges",
            7: "Comptes de produits",
            8: "Comptes de résultats",
            9: "Comptes analytiques"
        }
        return class_names.get(class_number, f"Classe {class_number}")

    def get_account_type(self, class_number):
        """
        Détermine le type de compte par défaut selon la classe.
        Cette méthode est conservée pour compatibilité mais n'est plus utilisée directement.
        Utilisez get_account_type_detailed qui prend en compte le code complet.
        """
        if class_number == 1:
            return AccountType.LIABILITY  # Comptes de capitaux (Passif)
        elif class_number == 2:
            return AccountType.ASSET  # Comptes d'actifs immobilisés (Actif)
        elif class_number == 3:
            return AccountType.ASSET  # Comptes de stocks (Actif)
        elif class_number == 4:
            return AccountType.LIABILITY  # Par défaut pour les comptes de tiers
        elif class_number == 5:
            return AccountType.ASSET  # Comptes de trésorerie (Actif)
        elif class_number == 6:
            return AccountType.EXPENSE  # Comptes de charges (Charge)
        elif class_number == 7:
            return AccountType.REVENUE  # Comptes de produits (Produit)
        elif class_number == 8:
            return AccountType.REVENUE  # Comptes de résultats (par défaut)
        else:
            return AccountType.ASSET  # Par défaut (classe 9 et autres)
            
    def get_account_type_detailed(self, code):
        """
        Détermine le type de compte selon les normes OHADA en fonction du code complet.
        
        Selon le plan comptable OHADA:
        - Classe 1: Comptes de ressources durables (Passif, sauf 19 qui est Actif)
        - Classe 2: Comptes d'actifs immobilisés (Actif)
        - Classe 3: Comptes de stocks (Actif)
        - Classe 4: Comptes de tiers:
          * 40: Fournisseurs (Passif)
          * 41: Clients (Actif)
          * 42: Personnel (Actif)
          * 43: Organismes sociaux (Actif)
          * 44: État et collectivités publiques (Actif)
          * 45: Organismes internationaux (Passif)
          * 46: Associés/groupe (Passif)
          * 47: Débiteurs et créditeurs divers (Passif)
          * 48: Créances et dettes hors activités ordinaires (Passif)
          * 49: Provisions pour dépréciation des comptes de tiers (Passif)
        - Classe 5: Comptes de trésorerie (Actif, sauf 59 qui est Passif)
        - Classe 6: Comptes de charges (Charge)
        - Classe 7: Comptes de produits (Produit)
        - Classe 8: Comptes de résultats (Produit/Charge)
        - Classe 9: Comptes analytiques (Divers)
        """
        class_number = int(code[0])  # Premier chiffre = classe
        
        # Par défaut, utiliser la règle par classe
        if class_number == 1:
            # Comptes de classe 1: majoritairement Passif
            if code.startswith('19'):
                return AccountType.ASSET  # Provisions pour dépréciation = Actif
            return AccountType.LIABILITY
            
        elif class_number == 2:
            # Comptes de classe 2: tous Actif
            return AccountType.ASSET
            
        elif class_number == 3:
            # Comptes de classe 3: tous Actif
            return AccountType.ASSET
            
        elif class_number == 4:
            # Comptes de classe 4: dépend du compte
            category = code[:2]  # Deux premiers chiffres
            if category in ['41', '42', '43', '44']:
                return AccountType.ASSET  # Clients, personnel, etc. = Actif
            else:
                return AccountType.LIABILITY  # Fournisseurs, etc. = Passif
                
        elif class_number == 5:
            # Comptes de classe 5: majoritairement Actif
            if code.startswith('59'):
                return AccountType.LIABILITY  # Provisions pour dépréciation = Passif
            return AccountType.ASSET
            
        elif class_number == 6:
            # Comptes de classe 6: tous Charge
            return AccountType.EXPENSE
            
        elif class_number == 7:
            # Comptes de classe 7: tous Produit
            return AccountType.REVENUE
            
        elif class_number == 8:
            # Comptes de classe 8: dépend du compte
            if code.startswith('8'):  # Suite à déterminer selon règles spécifiques
                return AccountType.REVENUE  # Par défaut
            return AccountType.EXPENSE
            
        else:
            # Comptes de classe 9 (analytiques): majoritairement Actif
            return AccountType.ASSET

    def find_category_name(self, accounts_data, category_code):
        """Cherche le libellé de la catégorie dans les données"""
        # Chercher un compte qui a exactement ce code de catégorie
        exact_match = next(
            (a['libelle'] for a in accounts_data if a['code'][:2] == category_code and len(a['code'][:2]) == len(category_code)),
            None
        )
        if exact_match:
            return exact_match
        
        # Sinon, prendre le premier compte qui commence par ce code
        for account in accounts_data:
            if account['code'].startswith(category_code):
                return f"Catégorie {category_code}"
        
        # Par défaut
        return f"Catégorie {category_code}"

    def determine_level_and_parent(self, code):
        """
        Détermine le niveau hiérarchique et le code du parent
        en fonction de la longueur du code.
        
        Pour un code à 8 chiffres, on a plusieurs niveaux:
        - Niveau 1: XX000000 (2 premiers chiffres)
        - Niveau 2: XXXX0000 (4 premiers chiffres)
        - Niveau 3: XXXXXX00 (6 premiers chiffres)
        - Niveau 4: XXXXXXXX (tous les 8 chiffres)
        """
        if code[2:] == '000000':  # XX000000
            return 1, None  # Premier niveau, pas de parent
        elif code[4:] == '0000':  # XXXX0000
            return 2, code[:2] + '000000'  # Deuxième niveau, parent de niveau 1
        elif code[6:] == '00':    # XXXXXX00
            return 3, code[:4] + '0000'  # Troisième niveau, parent de niveau 2
        else:                     # XXXXXXXX
            return 4, code[:6] + '00'  # Quatrième niveau, parent de niveau 3

    def get_or_create_class(self, tenant_id, number, name):
        """Crée ou récupère une classe de compte"""
        account_class, created = AccountClass.objects.get_or_create(
            tenant_id=tenant_id,
            number=number,
            defaults={'name': name}
        )
        
        if created:
            self.stdout.write(f"Classe créée: {number} - {name}")
        
        return account_class

    def get_or_create_category(self, tenant_id, account_class, code, name):
        """Crée ou récupère une catégorie de compte"""
        category, created = AccountCategory.objects.get_or_create(
            tenant_id=tenant_id,
            code=code,
            defaults={
                'account_class': account_class,
                'name': name
            }
        )
        
        if created:
            self.stdout.write(f"Catégorie créée: {code} - {name}")
        
        return category

    def create_account(self, tenant_id, code, name, account_class, category, account_type, level, parent=None, ref_financial_statement="INCONNU", is_amortization=False, normal_balance="INCONNU"):
        """Crée un compte avec informations de classification détaillées"""
        # Vérifier si le compte existe déjà
        try:
            account = Account.objects.get(
                tenant_id=tenant_id,
                code=code
            )
            # Mettre à jour le compte existant
            account.name = name
            account.account_class = account_class
            account.category = category
            account.type = account_type
            account.level = level
            account.parent = parent
            
            # Nouvelles informations de classification
            account.ref_financial_statement = ref_financial_statement
            account.is_amortization_depreciation = is_amortization
            account.normal_balance = normal_balance
            
            account.save()
            return account
        except Account.DoesNotExist:
            # Créer un nouveau compte
            account = Account.objects.create(
                tenant_id=tenant_id,
                code=code,
                name=name,
                account_class=account_class,
                category=category,
                type=account_type,
                level=level,
                parent=parent,
                
                # Nouvelles informations de classification
                ref_financial_statement=ref_financial_statement,
                is_amortization_depreciation=is_amortization,
                normal_balance=normal_balance
            )
            return account