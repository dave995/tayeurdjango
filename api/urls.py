from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views
from .views import GenerateModelView

# Router principal
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'workshops', views.WorkshopViewSet)
router.register(r'models', views.ClothingModelViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'material-categories', views.MaterialCategoryViewSet)
router.register(r'materials', views.MaterialViewSet)
router.register(r'stock-movements', views.StockMovementViewSet)
router.register(r'measurements', views.MeasurementsViewSet)

# Router imbriqué pour les ateliers
workshop_router = routers.NestedDefaultRouter(router, r'workshops', lookup='workshop')
workshop_router.register(r'images', views.WorkshopImageViewSet, basename='workshop-images')
workshop_router.register(r'reviews', views.ReviewViewSet, basename='workshop-reviews')

# Router imbriqué pour les modèles
model_router = routers.NestedDefaultRouter(router, r'models', lookup='model')
model_router.register(r'images', views.ModelImageViewSet, basename='model-images')

# Router imbriqué pour les commandes
order_router = routers.NestedDefaultRouter(router, r'orders', lookup='order')
order_router.register(r'status-updates', views.OrderStatusUpdateViewSet, basename='order-status-updates')

# URLs imbriquées pour les images et les mouvements de stock
material_router = routers.NestedDefaultRouter(router, r'materials', lookup='material')
material_router.register(r'images', views.MaterialImageViewSet, basename='material-images')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(workshop_router.urls)),
    path('', include(model_router.urls)),
    path('', include(order_router.urls)),
    path('', include(material_router.urls)),
    # Authentification session/cookie DRF
    path('api-auth/', include('rest_framework.urls')),
    
    # Authentification JWT
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', views.register_user, name='register_user'),
    path('auth/logout/', views.logout_user, name='logout_user'),
]

urlpatterns += [
    path('generate-model/', GenerateModelView.as_view(), name='generate-model'),
     path('admin/modele/', views.modele_list, name='modele_list'),
    path('admin/modele/ajouter/', views.modele_add, name='modele_add'),
    path('admin/modele/<int:pk>/modifier/', views.modele_edit, name='modele_edit'),
    path('admin/modele/<int:pk>/supprimer/', views.modele_delete, name='modele_delete'),
    path('admin/client/', views.client_list, name='client_list'),
    path('admin/client/ajouter/', views.client_add, name='client_add'),
    path('admin/client/<int:pk>/modifier/', views.client_edit, name='client_edit'),
    path('admin/client/<int:pk>/supprimer/', views.client_delete, name='client_delete'),
    path('admin/commande/', views.commande_list, name='commande_list'),
    path('admin/commande/ajouter/', views.commande_add, name='commande_add'),
    path('admin/commande/<int:pk>/modifier/', views.commande_edit, name='commande_edit'),
    path('admin/commande/<int:pk>/supprimer/', views.commande_delete, name='commande_delete'),
    path('admin/atelier/', views.atelier_list, name='atelier_list'),
    path('admin/atelier/ajouter/', views.atelier_add, name='atelier_add'),
    path('admin/atelier/<int:pk>/modifier/', views.atelier_edit, name='atelier_edit'),
    path('admin/atelier/<int:pk>/supprimer/', views.atelier_delete, name='atelier_delete'),
]