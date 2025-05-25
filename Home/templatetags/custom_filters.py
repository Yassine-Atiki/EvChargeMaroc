from django import template
from django.contrib.auth import get_user_model
from users.models import Fournisseur, ProprietaireVE

register = template.Library()

@register.filter
def is_instance_of(user, class_path):
    if not user.is_authenticated:
        return False
        
    try:
        if class_path == "users.models.Fournisseur":
            return Fournisseur.objects.filter(id=user.id).exists()
        elif class_path == "users.models.ProprietaireVE":
            return ProprietaireVE.objects.filter(id=user.id).exists()
        return False
    except Exception:
        return False

@register.filter
def format_k(value):
    """
    Convertit un nombre en format K (1000+) ou M (1000000+)
    Exemple: 1500 devient 1.5K, 1500000 devient 1.5M
    """
    try:
        value = int(value)
        if value >= 1000000:
            return f"{value/1000000:.1f}M"
        elif value >= 1000:
            return f"{value/1000:.1f}K"
        return str(value)
    except (ValueError, TypeError):
        return "0"

@register.filter
def add_plus(value):
    """
    Ajoute un signe + après un nombre si celui-ci est supérieur à 0
    """
    try:
        value = int(value)
        if value > 0:
            return f"{value}+"
        return str(value)
    except (ValueError, TypeError):
        return "0"
