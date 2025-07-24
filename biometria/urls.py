from django.contrib import admin
from django.urls import include, path
from cadastros import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.validar_biometria, name='validar_biometria'),
    path('cadastros/', views.cadastrar_biometria, name='cadastrar_biometria'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('monitoramento_basico/', views.monitoramento_basico_view, name='monitoramento_basico'),
    path('analise_detalhada/', views.analise_detalhada_view, name='analise_detalhada'),
    path('gerenciamento_projetos/', views.gerenciamento_projetos_view, name='gerenciamento_projetos'),
    path('logout/', views.user_logout, name='logout'),
]
