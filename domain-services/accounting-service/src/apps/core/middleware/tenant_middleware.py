class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Définir un tenant_id fixe pour tous les tests
        request.tenant_id = '284e521a-7899-4290-88e3-ea6a50913210'
        return self.get_response(request)