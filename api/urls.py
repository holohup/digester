from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import DigestViewSet, generate_digest

router = DefaultRouter()
router.register('digest', DigestViewSet, basename='digests')

urlpatterns = [
    path('generate/<int:pk>/', generate_digest, name='generate_digest'),
    path('', include(router.urls)),
]
