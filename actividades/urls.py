from django.urls import path
from .views import crear_actividad, obtener_actividades, eliminar_actividad, actualizar_actividad, obtener_actividad_por_id, registrar_usuario_actividad, cancelar_registro_usuario, cambiar_estado_actividad, obtener_usuarios_registrados, obtener_actividades_usuario

urlpatterns = [
    path('crear/', crear_actividad),
    path('obtener-actividades/', obtener_actividades),
    path('actividad/<str:actividad_id>/', obtener_actividad_por_id),
    path('actividad/<str:actividad_id>/actualizar/', actualizar_actividad),
    path('actividad/<str:actividad_id>/eliminar/', eliminar_actividad),
    path('actividades/<str:actividad_id>/registrar-usuario/', registrar_usuario_actividad),
    path('actividades/<str:actividad_id>/cancelar-registro/', cancelar_registro_usuario),
    path('actividades/<str:actividad_id>/cambiar-estado/', cambiar_estado_actividad),
    path('actividades/<str:actividad_id>/usuarios-registrados/', obtener_usuarios_registrados),
    path('actividades/usuario/<str:usuario_id>', obtener_actividades_usuario),
]

