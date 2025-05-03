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

    code_formatted = serializers.SerializerMethodField()

    def get_code_formatted(self, obj):
        """Retourne le code formaté selon vos règles"""
        return obj.code
    
    class Meta:
        model = Tiers
        fields = [
            'id', 'code', 'name', 'type', 'type_display', 
            'account', 'account_code', 'account_name',
            'address', 'email', 'phone', 'tax_id', 'notes',
            'is_active', 'tenant_id', 'created_at', 'updated_at',
            'code_formatted',  # Supprimez 'code' car il est déjà inclus plus haut
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_account(self, value):
        """Vérifie que le compte est un compte de tiers (classe 4)"""
        account_class = value.account_class.number
        if account_class != 4:
            raise serializers.ValidationError(
                f"Le compte doit être un compte de tiers (classe 4), "
                f"pas un compte de classe {account_class}"
            )
        return value
    
    def validate(self, data):
        """Validations supplémentaires"""
        # Si c'est une création (pas d'ID), on vérifie l'unicité du code pour ce tenant
        if self.instance is None:  # C'est une création
            tenant_id = data.get('tenant_id') or self.context['request'].tenant_id
            code = data.get('code')
            if Tiers.objects.filter(tenant_id=tenant_id, code=code).exists():
                raise serializers.ValidationError({
                    'code': f"Un tiers avec le code '{code}' existe déjà pour ce tenant."
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

class TiersListSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour les listes de tiers"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Tiers
        fields = ['id', 'code', 'name', 'type', 'type_display', 'is_active']
