from django.contrib import admin
from apps.core.models.account import AccountClass, AccountCategory, Account

@admin.register(AccountClass)
class AccountClassAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'tenant_id')
    list_filter = ('created_at',)
    search_fields = ('name', 'number')

@admin.register(AccountCategory)
class AccountCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'account_class', 'tenant_id')
    list_filter = ('account_class', 'created_at')
    search_fields = ('name', 'code')

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'account_class', 'type', 'is_active', 'tenant_id')
    list_filter = ('account_class', 'type', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description')
        }),
        ('Classification', {
            'fields': ('account_class', 'category', 'parent', 'level', 'type')
        }),
        ('Options', {
            'fields': ('is_active', 'is_reconcilable', 'is_tax_relevant')
        }),
        ('Tenant', {
            'fields': ('tenant_id',)
        }),
    )