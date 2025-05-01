from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.models.fiscal_year import FiscalYear, FiscalPeriod
from apps.core.serializers.fiscal_year_serializers import (
    FiscalYearSerializer, 
    FiscalPeriodSerializer
)

class FiscalYearViewSet(viewsets.ModelViewSet):
    """ViewSet pour les exercices fiscaux"""
    serializer_class = FiscalYearSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['start_date', 'end_date', 'name', 'code', 'is_active', 'created_at']
    ordering = ['-start_date']

    def get_queryset(self):
        """Filtre les résultats par tenant_id et autres critères"""
        queryset = FiscalYear.objects.all()
        tenant_id = getattr(self.request, 'tenant_id', None)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        # Filtrage supplémentaire
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
            
        is_closed = self.request.query_params.get('is_closed', None)
        if is_closed is not None:
            is_closed = is_closed.lower() == 'true'
            queryset = queryset.filter(is_closed=is_closed)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def create_periods(self, request, pk=None):
        """Endpoint pour créer les périodes d'un exercice fiscal"""
        fiscal_year = self.get_object()
        
        period_type = request.data.get('period_type', 'monthly')
        if period_type not in ['monthly', 'quarterly']:
            return Response(
                {"error": "Le type de période doit être 'monthly' ou 'quarterly'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fiscal_year.create_periods(period_type=period_type)
            return Response(
                {"message": f"Périodes créées avec succès pour l'exercice {fiscal_year.name}"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FiscalPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet pour les périodes fiscales"""
    serializer_class = FiscalPeriodSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['fiscal_year', 'number', 'start_date', 'end_date', 'created_at']
    ordering = ['fiscal_year', 'number']

    def get_queryset(self):
        """Filtre les résultats par tenant_id et fiscal_year"""
        queryset = FiscalPeriod.objects.all()
        tenant_id = getattr(self.request, 'tenant_id', None)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        # Filtrage par exercice fiscal
        fiscal_year = self.request.query_params.get('fiscal_year', None)
        if fiscal_year:
            queryset = queryset.filter(fiscal_year_id=fiscal_year)
            
        # Filtrage par statut
        is_closed = self.request.query_params.get('is_closed', None)
        if is_closed is not None:
            is_closed = is_closed.lower() == 'true'
            queryset = queryset.filter(is_closed=is_closed)
        
        return queryset