from django.urls import path, include
from rest_framework.routers import DefaultRouter
from secure_bite import views

app_name = "secure_bite"

router = DefaultRouter()
router.register(r'auth', views.AuthenticationViewset, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]
