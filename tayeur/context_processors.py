from django.contrib.auth import get_user_model
from api.models import Order, Workshop, ClothingModel

def admin_dashboard_stats(request):
    try:
        User = get_user_model()
        nb_clients = User.objects.filter(user_type='client').count()
        nb_workshops = Workshop.objects.count()
        nb_models = ClothingModel.objects.count()
        nb_orders = Order.objects.count()
        return {
            'nb_clients': nb_clients,
            'nb_workshops': nb_workshops,
            'nb_models': nb_models,
            'nb_orders': nb_orders,
        }
    except Exception:
        # Retourner des valeurs par défaut si les tables n'existent pas encore
        return {
            'nb_clients': 0,
            'nb_workshops': 0,
            'nb_models': 0,
            'nb_orders': 0,
        } 
