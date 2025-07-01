from django.urls import path
from .views import generate_models_from_fabric, analyze_fabric, generate_model_image

app_name = 'chatgpt'

urlpatterns = [
    path('api/ai/generate-models/', generate_models_from_fabric, name='generate_models'),
    path('api/ai/analyze-fabric/', analyze_fabric, name='analyze_fabric'),
    path('api/ai/generate-image/', generate_model_image, name='generate_image'),
    path('test-connection/', views.test_connection, name='test_connection'),
] 