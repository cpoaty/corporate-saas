from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from apps.core.models.account import AccountClass, AccountCategory, Account
from apps.core.serializers.account_serializers import (
    AccountClassSerializer, 
    AccountCategorySerializer, 
    AccountSerializer
)

class AccountClassViewSet(viewsets.ModelViewSet):
    """ViewSet pour les classes de comptes"""
    serializer_class = AccountClassSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['number', 'name']
    ordering_fields = ['number', 'name', 'created_at']
    ordering = ['number']

    def get_queryset(self):
        """Filtre les résultats par tenant_id"""
        queryset = AccountClass.objects.all()
        tenant_id = getattr(self.request, 'tenant_id', None)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        return queryset

class AccountCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour les catégories de comptes"""
    serializer_class = AccountCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']

    def get_queryset(self):
        """Filtre les résultats par tenant_id et account_class"""
        queryset = AccountCategory.objects.all()
        tenant_id = getattr(self.request, 'tenant_id', None)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        account_class_id = self.request.query_params.get('account_class', None)
        if account_class_id:
            queryset = queryset.filter(account_class_id=account_class_id)
            
        return queryset

class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet pour les comptes"""
    serializer_class = AccountSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'account_class', 'type', 'created_at']
    ordering = ['code']

    def get_queryset(self):
        """Filtre les résultats par tenant_id et divers critères"""
        queryset = Account.objects.all()
        tenant_id = getattr(self.request, 'tenant_id', None)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        # Filtrage par critères additionnels
        account_class = self.request.query_params.get('account_class', None)
        if account_class:
            queryset = queryset.filter(account_class_id=account_class)
            
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
            
        account_type = self.request.query_params.get('type', None)
        if account_type:
            queryset = queryset.filter(type=account_type)
            
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
            
        parent = self.request.query_params.get('parent', None)
        if parent:
            if parent.lower() == 'null':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent)
        
        # Recherche textuelle avancée
        search = self.request.query_params.get('q', None)
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) | 
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
            
        return queryset
    
    @action(detail=False, methods=['post'])
    def import_ohada(self, request):
        """Endpoint pour importer le plan comptable OHADA"""
        tenant_id = getattr(request, 'tenant_id', None)
        if not tenant_id:
            return Response(
                {"error": "Tenant ID est requis pour cette opération"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            accounts = Account.create_default_accounts_ohada(tenant_id)
            return Response(
                {"message": f"{len(accounts)} comptes créés avec succès"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )