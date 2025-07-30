from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
# Remove or comment out the old import for obtain_auth_token
# from rest_framework.authtoken.views import obtain_auth_token

# Import JWT views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.http import HttpResponse

def spa_root(request):
    return HttpResponse("OK")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/', include('api.urls')),  # Ajout pour vues admin personnalisées
    path('api/', include('api.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Remove or comment out the old token auth URL
    # path('api/token/', obtain_auth_token, name='api_token_auth'),

    # Add JWT authentication URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', spa_root),  # Pour éviter l'erreur 404 après login
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)