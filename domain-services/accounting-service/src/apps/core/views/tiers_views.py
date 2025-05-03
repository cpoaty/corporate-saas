"""
Vues pour la gestion des tiers
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ..models.tiers import Tiers
from ..serializers.tiers_serializers import TiersSerializer, TiersListSerializer

class TiersViewSet(viewsets.ModelViewSet):
    """ViewSet pour les tiers (clients, fournisseurs, etc.)"""
    serializer_class = TiersSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['code', 'name', 'email', 'tax_id']
    ordering_fields = ['code', 'name', 'type', 'created_at']
    ordering = ['code']
    filterset_fields = ['type', 'is_active']
    
    def get_queryset(self):
        """Filtre les résultats par tenant_id et autres critères"""
        queryset = Tiers.objects.all()
        tenant_id = getattr(self.request, 'tenant_id', None)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        # Filtrage par compte
        account_id = self.request.query_params.get('account', None)
        if account_id:
            queryset = queryset.filter(account_id=account_id)
        
        return queryset
    
    def get_serializer_class(self):
        """Utiliser un sérialiseur différent pour list"""
        if self.action == 'list':
            return TiersListSerializer
        return TiersSerializer
    
    def perform_create(self, serializer):
        """Ajoute le tenant_id lors de la création"""
        tenant_id = getattr(self.request, 'tenant_id', None)
        serializer.save(tenant_id=tenant_id)
    
    @action(detail=False, methods=['post'])
    def create_defaults(self, request):
        """Crée les tiers par défaut pour le tenant actuel"""
        tenant_id = getattr(request, 'tenant_id', None)
        if not tenant_id:
            return Response(
                {"detail": "Tenant ID requis pour cette opération."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            created_tiers = Tiers.create_default_tiers(tenant_id)
            serializer = TiersListSerializer(created_tiers, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
