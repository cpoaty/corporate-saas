from rest_framework import serializers
from apps.core.models.fiscal_year import FiscalYear, FiscalPeriod

class FiscalPeriodSerializer(serializers.ModelSerializer):
    fiscal_year_name = serializers.ReadOnlyField(source='fiscal_year.name')
    
    class Meta:
        model = FiscalPeriod
        fields = ['id', 'fiscal_year', 'fiscal_year_name', 'name', 'code', 
                 'start_date', 'end_date', 'number', 'is_closed', 'is_locked',
                 'tenant_id', 'created_at', 'updated_at']

class FiscalYearSerializer(serializers.ModelSerializer):
    periods = FiscalPeriodSerializer(many=True, read_only=True)
    
    class Meta:
        model = FiscalYear
        fields = ['id', 'name', 'code', 'start_date', 'end_date', 
                 'is_closed', 'closed_date', 'closed_by', 'is_active', 'is_locked',
                 'tenant_id', 'created_at', 'updated_at', 'periods']