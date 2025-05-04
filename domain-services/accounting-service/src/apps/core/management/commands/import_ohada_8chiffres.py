import json
import os
import uuid
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from apps.core.models.account import AccountClass, AccountCategory, Account, AccountType


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

            # Supprimer les comptes existants si demandé
            if options['replace']:
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
            
            # Déterminer le type de compte en fonction du code complet
            account_type = self.get_account_type_detailed(code)
            
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
            
            # Créer le compte
            account = self.create_account(
                tenant_id=tenant_id,
                code=code,
                name=name,
                account_class=account_class,
                category=category,
                account_type=account_type,
                level=level,
                parent=parent
            )
            
            # Stocker le compte pour qu'il puisse servir de parent
            parent_accounts[code] = account

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

    def create_account(self, tenant_id, code, name, account_class, category, account_type, level, parent=None):
        """Crée un compte"""
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
                parent=parent
            )
            return account