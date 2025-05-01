# apps/core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.account_views import AccountClassViewSet, AccountCategoryViewSet, AccountViewSet
from .views.fiscal_year_views import FiscalYearViewSet, FiscalPeriodViewSet

# Créer un routeur pour les viewsets
router = DefaultRouter()
router.register(r'account-classes', AccountClassViewSet, basename='account-class')
router.register(r'account-categories', AccountCategoryViewSet, basename='account-category')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'fiscal-years', FiscalYearViewSet, basename='fiscal-year')
router.register(r'fiscal-periods', FiscalPeriodViewSet, basename='fiscal-period')

urlpatterns = [
    # Inclure les routes générées automatiquement par le routeur
    path('', include(router.urls)),
    
    # Vous pouvez ajouter d'autres routes personnalisées ici si nécessaire
    # path('custom-endpoint/', custom_view_function),
]