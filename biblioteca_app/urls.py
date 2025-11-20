from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sala/<int:sala_id>/', views.sala_detail, name='sala_detail'),
    path('reserva-rapida/<int:sala_id>/', views.reserva_rapida, name='reserva_rapida'),
    path('reserva-programada/<int:sala_id>/', views.reserva_programada, name='reserva_programada'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('liberar-salas/', views.liberar_salas_manual, name='liberar_salas'),
    path('programar-liberacion/', views.programar_liberacion, name='programar_liberacion'),
    path('liberar-ahora/<int:sala_id>/', views.liberar_ahora, name='liberar_ahora'),
    path('estado-liberaciones/', views.estado_liberaciones, name='estado_liberaciones'),
    path('actualizar-contador/<int:reserva_id>/', views.actualizar_contador, name='actualizar_contador'),
]