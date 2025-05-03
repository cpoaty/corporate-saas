from django.shortcuts import render

def home_view(request):
    """Vue pour la page d'accueil utilisant le système de templates."""
    return render(request, 'core/home.html')