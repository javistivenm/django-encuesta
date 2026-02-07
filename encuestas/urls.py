from django.urls import path

from .views import portal_exportar_csv, portal_inicio, tablet_encuesta, tablet_gracias, tablet_inicio

app_name = 'encuestas'

urlpatterns = [
    path('', tablet_inicio, name='tablet_inicio'),
    path('tablet/', tablet_inicio, name='tablet_inicio_alias'),
    path('tablet/<str:identificador>/', tablet_encuesta, name='tablet_encuesta'),
    path('tablet/<str:identificador>/gracias/', tablet_gracias, name='tablet_gracias'),
    path('portal/', portal_inicio, name='portal_inicio'),
    path('portal/exportar.csv', portal_exportar_csv, name='portal_exportar_csv'),
]
