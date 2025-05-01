from rest_framework import serializers
from apps.core.models.account import AccountClass, AccountCategory, Account

class AccountClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountClass
        fields = ['id', 'number', 'name', 'description', 'tenant_id', 'created_at', 'updated_at']

class AccountCategorySerializer(serializers.ModelSerializer):
    account_class_name = serializers.ReadOnlyField(source='account_class.name')
    
    class Meta:
        model = AccountCategory
        fields = ['id', 'code', 'name', 'description', 'account_class', 'account_class_name', 
                 'tenant_id', 'created_at', 'updated_at']

class AccountSerializer(serializers.ModelSerializer):
    account_class_name = serializers.ReadOnlyField(source='account_class.name')
    category_name = serializers.ReadOnlyField(source='category.name')
    parent_name = serializers.ReadOnlyField(source='parent.name')
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Account
        fields = ['id', 'code', 'name', 'description', 'account_class', 'account_class_name',
                 'category', 'category_name', 'parent', 'parent_name', 'level',
                 'type', 'type_display', 'is_active', 'is_reconcilable', 'is_tax_relevant',
                 'tenant_id', 'created_at', 'updated_at']