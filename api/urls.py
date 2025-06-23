from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

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
    path('api-auth/', include('rest_framework.urls')),
]