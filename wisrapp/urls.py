from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'categorias', views.CategoriaViewSet)
router.register(r'transacciones', views.TransaccionViewSet)
router.register(r'transaccionesprog', views.TransaccionProgramadaViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('totales/', views.TotalesView.as_view(), name='totales'),
]
