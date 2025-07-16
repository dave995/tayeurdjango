from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Remove or comment out the old import for obtain_auth_token
# from rest_framework.authtoken.views import obtain_auth_token

# Import JWT views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/', include('api.urls')),  # Ajout pour vues admin personnalisées
    path('api/', include('api.urls')),
    # Remove or comment out the old token auth URL
    # path('api/token/', obtain_auth_token, name='api_token_auth'),

    # Add JWT authentication URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)