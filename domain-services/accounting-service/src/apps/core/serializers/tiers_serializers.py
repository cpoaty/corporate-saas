"""
Sérialiseurs pour les tiers
"""
from rest_framework import serializers
from ..models.tiers import Tiers
from ..models.account import Account

class TiersSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Tiers"""
    account_code = serializers.CharField(source='account.code', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    # Utiliser pour accepter le code du compte au lieu de son UUID
    account_code_input = serializers.CharField(write_only=True, required=False)

    code_formatted = serializers.SerializerMethodField()

    def get_code_formatted(self, obj):
        """Retourne le code formaté selon vos règles"""
        return obj.code
    
    class Meta:
        model = Tiers
        fields = [
            'id', 'code', 'name', 'type', 'type_display', 
            'account', 'account_code', 'account_name', 'account_code_input',
            'address', 'email', 'phone', 'tax_id', 'notes',
            'is_active', 'tenant_id', 'created_at', 'updated_at',
            'code_formatted',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'account': {'required': False},  # Rendre account optionnel car on peut utiliser account_code_input
        }
    
    def validate_account(self, value):
        """Vérifie que le compte est un compte de tiers (classe 4)"""
        if not value:
            return value
            
        account_class = value.account_class.number
        if account_class != 4:
            raise serializers.ValidationError(
                f"Le compte doit être un compte de tiers (classe 4), "
                f"pas un compte de classe {account_class}"
            )
        return value
    
    def validate(self, data):
        """Validations supplémentaires"""
        # Vérifier si l'un des champs account ou account_code_input est fourni
        if not data.get('account') and not data.get('account_code_input'):
            if self.instance is None:  # C'est une création
                raise serializers.ValidationError({
                    'account_code_input': "Vous devez fournir un code de compte valide."
                })
        
        # Si c'est une création (pas d'ID), on vérifie l'unicité du code pour ce tenant
        if self.instance is None:  # C'est une création
            tenant_id = data.get('tenant_id')
            if not tenant_id and hasattr(self.context.get('request', {}), 'tenant_id'):
                tenant_id = self.context['request'].tenant_id
                
            code = data.get('code')
            if code and tenant_id and Tiers.objects.filter(tenant_id=tenant_id, code=code).exists():
                raise serializers.ValidationError({
                    'code': f"Un tiers avec le code '{code}' existe déjà pour ce tenant."
                })
        
        # Extraire les 3 premières lettres du nom et vérifier qu'elles correspondent aux positions 4-6 du code
        name = data.get('name', '')
        code = data.get('code', '')
        
        if name and code and len(code) >= 6 and len(name) >= 3:
            name_part = ''.join(c for c in name.upper() if c.isalpha())[:3]
            code_name_part = code[3:6].upper()
            
            # Vérifier que les 3 premières lettres du nom sont bien dans le code
            if name_part and code_name_part and name_part != code_name_part:
                raise serializers.ValidationError({
                    'code': f"Les positions 4-6 du code ({code_name_part}) doivent correspondre aux trois premières lettres du nom ({name_part})."
                })
        
        return data
    
    def validate_code(self, value):
        """Validation du code"""
        # Convertir en majuscules pour la validation
        value = value.upper()
        
        # Vérifier que le code commence par 401, 411 ou 422
        valid_prefixes = ['401', '411', '422']
        prefix = value[:3] if len(value) >= 3 else ''
        
        if prefix not in valid_prefixes:
            raise serializers.ValidationError(
                "Le code doit commencer par 401 (fournisseur), 411 (client) ou 422 (personnel)."
            )
        
        # Vérifier la longueur minimale (6 caractères)
        if len(value) < 6:
            raise serializers.ValidationError(
                "Le code doit contenir au moins 6 caractères (préfixe + 3 lettres du nom)."
            )
        
        # Vérifier que les positions 4-6 sont des lettres
        name_part = value[3:6]
        if not name_part.isalpha():
            raise serializers.ValidationError(
                "Les positions 4-6 du code doivent être les trois premières lettres du nom."
            )
        
        return value
    
    def validate_name(self, value):
        """Validation du nom selon les conventions du plan comptable"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Le nom ne peut pas être vide.")
        
        # Vérifier la longueur minimale
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Le nom doit comporter au moins 2 caractères."
            )
        
        # Vérifier que le nom ne contient pas trop de caractères spéciaux
        import re
        special_chars_count = len(re.findall(r'[^\w\s\-\.,&\(\)]', value))
        if special_chars_count > 5:
            raise serializers.ValidationError(
                "Le nom contient trop de caractères spéciaux."
            )
        
        return value

    def validate_account_code_input(self, value):
        """Valide le code du compte fourni"""
        if not value:
            return value
            
        # Vérifier qu'il s'agit d'un code de compte valide (classe 4)
        if not value.startswith('4'):
            raise serializers.ValidationError(
                "Le code du compte doit commencer par 4 (compte de tiers)."
            )
        
        return value

    def create(self, validated_data):
        """
        Fonction create personnalisée qui accepte soit un objet account, 
        soit un code de compte (account_code_input)
        """
        # Récupérer le tenant_id du contexte si non fourni
        tenant_id = validated_data.get('tenant_id')
        if not tenant_id and hasattr(self.context.get('request', {}), 'tenant_id'):
            tenant_id = self.context['request'].tenant_id
            validated_data['tenant_id'] = tenant_id
            
        # Récupérer le compte selon le code fourni
        account = validated_data.pop('account', None)
        account_code = validated_data.pop('account_code_input', None)
        
        if not account and account_code:
            try:
                account = Account.objects.get(code=account_code, tenant_id=tenant_id)
            except Account.DoesNotExist:
                raise serializers.ValidationError({
                    "account_code_input": f"Le compte avec le code {account_code} n'existe pas pour ce tenant."
                })
        
        if not account:
            raise serializers.ValidationError({
                "account": "Un compte valide est requis pour créer un tiers."
            })
            
        # Vérifier que le compte est bien un compte de tiers (classe 4)
        if account.account_class.number != 4:
            raise serializers.ValidationError({
                "account": f"Le compte doit être un compte de tiers (classe 4), pas un compte de classe {account.account_class.number}."
            })
        
        # Créer le tiers avec le compte trouvé
        tiers = Tiers.objects.create(account=account, **validated_data)
        return tiers
class TiersListSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour les listes de tiers"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Tiers
        fields = ['id', 'code', 'name', 'type', 'type_display', 'is_active']
