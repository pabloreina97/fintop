from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'categorias', views.CategoriaViewSet)
router.register(r'transacciones', views.TransaccionViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth_truelayer/', views.AuthTruelayer.as_view(), name='auth_truelayer'),
    path('auth_refresh/', views.AuthRefresh.as_view(), name='auth_refresh'),
    path('redirect_truelayer/', views.RedirectTruelayer.as_view(),
         name='redirect_truelayer'),
    path('get_transacciones/', views.GetTransaccionesView.as_view(),
         name='get_transacciones'),
    path('get_accounts/', views.GetAccountsView.as_view(),
         name='get_accounts'),
    path('sincronizar_transacciones/', views.SincronizarTransaccionesView.as_view(),
         name='sincronizar_transacciones'),
]
