from rest_framework.routers import DefaultRouter
from .views import VagaViewSet, CandidaturaViewSet

router = DefaultRouter()
router.register(r'vagas', VagaViewSet, basename='vaga')
router.register(r'candidaturas', CandidaturaViewSet, basename='candidatura')

urlpatterns = router.urls