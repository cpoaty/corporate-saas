from django.contrib import admin
from apps.core.models.fiscal_year import FiscalYear, FiscalPeriod

@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'start_date', 'end_date', 'is_active', 'is_closed', 'tenant_id')
    list_filter = ('is_active', 'is_closed', 'created_at')
    search_fields = ('name', 'code')
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'start_date', 'end_date')
        }),
        ('Statut', {
            'fields': ('is_active', 'is_closed', 'is_locked', 'closed_date', 'closed_by')
        }),
        ('Tenant', {
            'fields': ('tenant_id',)
        }),
    )
    actions = ['create_periods']

    def create_periods(self, request, queryset):
        count = 0
        for fiscal_year in queryset:
            fiscal_year.create_periods()
            count += 1
        self.message_user(request, f"Périodes créées pour {count} exercices fiscaux.")
    create_periods.short_description = "Créer les périodes mensuelles"

@admin.register(FiscalPeriod)
class FiscalPeriodAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'fiscal_year', 'start_date', 'end_date', 'is_closed', 'tenant_id')
    list_filter = ('fiscal_year', 'is_closed', 'created_at')
    search_fields = ('name', 'code')
    fieldsets = (
        (None, {
            'fields': ('fiscal_year', 'name', 'code', 'number', 'start_date', 'end_date')
        }),
        ('Statut', {
            'fields': ('is_closed', 'is_locked')
        }),
        ('Tenant', {
            'fields': ('tenant_id',)
        }),
    )