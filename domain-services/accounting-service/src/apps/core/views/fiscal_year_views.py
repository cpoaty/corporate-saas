from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from dateutil.relativedelta import relativedelta
from datetime import timedelta

from ..models.fiscal_year import FiscalYear, FiscalPeriod
from ..serializers.fiscal_year_serializers import FiscalYearSerializer, FiscalPeriodSerializer

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
        """Crée automatiquement des périodes pour un exercice fiscal."""
        fiscal_year = self.get_object()
        period_type = request.data.get('period_type', 'monthly')
        tenant_id = request.data.get('tenant_id')
        
        # Logique pour créer les périodes
        periods = []
        if period_type == 'monthly':
            # Créer 12 périodes mensuelles
            start_date = fiscal_year.start_date
            while start_date <= fiscal_year.end_date:
                end_date = min(
                    (start_date.replace(day=1) + relativedelta(months=1, days=-1)),
                    fiscal_year.end_date
                )
                
                period = FiscalPeriod.objects.create(
                    fiscal_year=fiscal_year,
                    name=f"{start_date.strftime('%B %Y')}",
                    code=f"{start_date.strftime('%Y-%m')}",
                    start_date=start_date,
                    end_date=end_date,
                    number=len(periods) + 1,
                    tenant_id=tenant_id or fiscal_year.tenant_id
                )
                periods.append(period)
                
                # Passer au mois suivant
                start_date = end_date + timedelta(days=1)
        
        serializer = FiscalPeriodSerializer(periods, many=True)
        return Response(serializer.data)

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