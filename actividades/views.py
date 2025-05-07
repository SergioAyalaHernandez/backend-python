import base64
import json
from bson import ObjectId
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
from backend.mongo_client import get_collection
from utils.jwt_utils import jwt_required

actividades_collection = get_collection("actividades")



@csrf_exempt
@jwt_required
def crear_actividad(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    fecha_inicio = data.get("fechaInicio")
    fecha_fin = data.get("fechaFin")
    hora_inicio = data.get("horaInicio")
    hora_fin = data.get("horaFin")
    cupo_maximo = data.get("cupoMaximo")
    recursos = data.get("recursos")
    categoria = data.get("categoria")
    enlace = data.get("enlace")
    imagen_base64 = data.get("imagen")
    profesorId = data.get("profesorId")
    imagen_data = None
    imagen_tipo = "image/png"
    imagen_nombre = "imagen.png"

    if imagen_base64 and "base64," in imagen_base64:
        imagen_data = imagen_base64.split("base64,")[1]

    actividad_data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "fechaInicio": fecha_inicio,
        "fechaFin": fecha_fin,
        "horaInicio": hora_inicio,
        "horaFin": hora_fin,
        "cupoMaximo": cupo_maximo,
        "cuposDisponibles": cupo_maximo,
        "recursos": recursos,
        "categoria": categoria,
        "enlace": enlace,
        "profesorId": profesorId,
        "imagen": {
            "data": imagen_data,
            "contentType": imagen_tipo,
            "nombre": imagen_nombre
        } if imagen_data else None,
        "creado": datetime.now(),
        "usuariosRegistrados": [],
        "estado": "abierto"
    }

    result = actividades_collection.insert_one(actividad_data)

    return JsonResponse({
        'message': 'Actividad creada correctamente',
        'id': str(result.inserted_id)
    }, status=201)



@csrf_exempt
@jwt_required
def obtener_actividades(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    actividades = list(actividades_collection.find())

    actividades_serializadas = []
    for actividad in actividades:

        fecha_inicio = actividad.get("fechaInicio")
        if isinstance(fecha_inicio, str):
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            except ValueError:
                fecha_inicio = None
        elif isinstance(fecha_inicio, datetime):
            fecha_inicio = fecha_inicio.isoformat()

        fecha_fin = actividad.get("fechaFin")
        if isinstance(fecha_fin, str):
            try:
                fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
            except ValueError:
                fecha_fin = None
        elif isinstance(fecha_fin, datetime):
            fecha_fin = fecha_fin.isoformat()

        actividades_serializadas.append({
            "id": str(actividad.get("_id")),
            "nombre": actividad.get("nombre"),
            "descripcion": actividad.get("descripcion"),
            "fechaInicio": fecha_inicio,
            "fechaFin": fecha_fin,
            "cupoMaximo": actividad.get("cupoMaximo"),
            "cuposDisponibles": actividad.get("cuposDisponibles"),
            "recursos": actividad.get("recursos"),
            "categoria": actividad.get("categoria"),
            "imagen": actividad.get("imagen"),
            "creado": actividad.get("creado").isoformat() if actividad.get("creado") else None,
            "estado": actividad.get("estado", "abierto"),
            "profesorId": actividad.get("profesorId"),
            "usuariosRegistrados": actividad.get("usuariosRegistrados", [])
        })

    return JsonResponse(actividades_serializadas, safe=False, status=200)


@csrf_exempt
@jwt_required
def obtener_actividad_por_id(request, actividad_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    actividad = actividades_collection.find_one({"_id": ObjectId(actividad_id)})

    if not actividad:
        return JsonResponse({'error': 'Actividad no encontrada'}, status=404)

    fecha_inicio = actividad.get("fechaInicio")
    if isinstance(fecha_inicio, str):
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        except ValueError:
            fecha_inicio = None
    elif isinstance(fecha_inicio, datetime):
        fecha_inicio = fecha_inicio.date()

    fecha_fin = actividad.get("fechaFin")
    if isinstance(fecha_fin, str):
        try:
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        except ValueError:
            fecha_fin = None
    elif isinstance(fecha_fin, datetime):
        fecha_fin = fecha_fin.date()

        # Hora de inicio
    hora_inicio = actividad.get("horaInicio")
    if isinstance(hora_inicio, str):
        try:
            hora_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
        except ValueError:
            hora_inicio = None

    # Hora de fin
    hora_fin = actividad.get("horaFin")
    if isinstance(hora_fin, str):
        try:
            hora_fin = datetime.strptime(hora_fin, "%H:%M").time()
        except ValueError:
            hora_fin = None

    actividad_serializada = {
        "id": str(actividad.get("_id")),
        "nombre": actividad.get("nombre"),
        "descripcion": actividad.get("descripcion"),
        "fechaInicio": f"{fecha_inicio.isoformat()} {hora_inicio.isoformat()}" if fecha_inicio and hora_inicio else None,
        "fechaFin": f"{fecha_fin.isoformat()} {hora_fin.isoformat()}" if fecha_fin and hora_fin else None,
        "cupoMaximo": actividad.get("cupoMaximo"),
        "cuposDisponibles": actividad.get("cuposDisponibles", actividad.get("cupoMaximo")),
        "recursos": actividad.get("recursos"),
        "categoria": actividad.get("categoria"),
        "imagen": actividad.get("imagen") if actividad.get("imagen") else None,
        "creado": actividad.get("creado").isoformat() if actividad.get("creado") else None,
        "estado": actividad.get("estado", "abierto"),
        "profesorId": actividad.get("profesorId"),
        "usuariosRegistrados": actividad.get("usuariosRegistrados", [])
    }

    return JsonResponse(actividad_serializada, status=200)


@csrf_exempt
@jwt_required
def actualizar_actividad(request, actividad_id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    update_data = {}

    campos = ["nombre", "descripcion", "fechaInicio", "fechaFin", "cupoMaximo", "recursos", "categoria", "imagen",
              "estado"]
    for campo in campos:
        if campo in data:
            update_data[campo] = data[campo]

    if "imagen" in data and data["imagen"] and "base64," in data["imagen"]:
        imagen_base64 = data["imagen"].split("base64,")[1]
        update_data["imagen"] = {
            "data": imagen_base64,
            "contentType": "image/png",
            "nombre": "imagen.png"
        }

    if "cupoMaximo" in update_data:
        actividad = actividades_collection.find_one({"_id": ObjectId(actividad_id)})
        if actividad:
            usuarios_registrados = len(actividad.get("usuariosRegistrados", []))

            if update_data["cupoMaximo"] < usuarios_registrados:
                return JsonResponse({
                    'error': 'El cupo maximo no puede ser menor que el numero de usuarios ya registrados',
                    'usuariosRegistrados': usuarios_registrados
                }, status=400)

            update_data["cuposDisponibles"] = update_data["cupoMaximo"] - usuarios_registrados

            # Si se aumenta el cupo y estaba en estado "completo", cambiar a "abierto"
            if update_data["cupoMaximo"] > actividad.get("cupoMaximo", 0) and actividad.get("estado") == "completo":
                update_data["estado"] = "abierto"

    result = actividades_collection.update_one(
        {"_id": ObjectId(actividad_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return JsonResponse({'error': 'Actividad no encontrada'}, status=404)

    actividad_actualizada = actividades_collection.find_one({"_id": ObjectId(actividad_id)})

    actividad_serializada = {
        "id": str(actividad_actualizada.get("_id")),
        "nombre": actividad_actualizada.get("nombre"),
        "descripcion": actividad_actualizada.get("descripcion"),
        "fechaInicio": actividad_actualizada.get("fechaInicio"),
        "fechaFin": actividad_actualizada.get("fechaFin"),
        "cupoMaximo": actividad_actualizada.get("cupoMaximo"),
        "cuposDisponibles": actividad_actualizada.get("cuposDisponibles", actividad_actualizada.get("cupoMaximo")),
        "recursos": actividad_actualizada.get("recursos"),
        "categoria": actividad_actualizada.get("categoria"),
        "imagen": actividad_actualizada.get("imagen"),
        "creado": actividad_actualizada.get("creado").isoformat() if actividad_actualizada.get("creado") else None,
        "estado": actividad_actualizada.get("estado", "abierto"),
        "usuariosRegistrados": actividad_actualizada.get("usuariosRegistrados", [])
    }

    return JsonResponse(actividad_serializada, status=200)


@csrf_exempt
@jwt_required
def eliminar_actividad(request, actividad_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    result = actividades_collection.delete_one({"_id": ObjectId(actividad_id)})

    if result.deleted_count == 0:
        return JsonResponse({'error': 'Actividad no encontrada'}, status=404)

    return JsonResponse({'message': 'Actividad eliminada correctamente'}, status=200)


@csrf_exempt
@jwt_required
def registrar_usuario_actividad(request, actividad_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    usuario_id = data.get("usuarioId")
    correo = data.get("correo")

    if not usuario_id or not correo:
        return JsonResponse({'error': 'Se requiere ID de usuario y correo'}, status=400)

    # Obtener la actividad
    actividad = actividades_collection.find_one({"_id": ObjectId(actividad_id)})

    if not actividad:
        return JsonResponse({'error': 'Actividad no encontrada'}, status=404)

    # Verificar si la actividad está cerrada o completa
    if actividad.get("estado") == "cerrado":
        return JsonResponse({'error': 'La actividad está cerrada'}, status=400)

    # Verificar disponibilidad de cupos
    cupos_disponibles = actividad.get("cuposDisponibles", actividad.get("cupoMaximo", 0))

    if cupos_disponibles <= 0:
        return JsonResponse({'error': 'No hay cupos disponibles'}, status=400)

    usuarios_registrados = actividad.get("usuariosRegistrados", [])
    for usuario in usuarios_registrados:
        if usuario.get("usuarioId") == usuario_id:
            return JsonResponse({'error': 'Usuario ya registrado en esta actividad'}, status=400)

    nuevo_usuario = {
        "usuarioId": usuario_id,
        "correo": correo,
        "fechaRegistro": datetime.now().isoformat()
    }

    result = actividades_collection.update_one(
        {"_id": ObjectId(actividad_id)},
        {
            "$push": {"usuariosRegistrados": nuevo_usuario},
            "$inc": {"cuposDisponibles": -1}
        }
    )

    actividad_actualizada = actividades_collection.find_one({"_id": ObjectId(actividad_id)})

    if actividad_actualizada.get("cuposDisponibles") == 0:
        actividades_collection.update_one(
            {"_id": ObjectId(actividad_id)},
            {"$set": {"estado": "completo"}}
        )

    return JsonResponse({
        'message': 'Usuario registrado correctamente en la actividad',
        'cuposRestantes': actividad_actualizada.get("cuposDisponibles")
    }, status=200)


@csrf_exempt
@jwt_required
def cancelar_registro_usuario(request, actividad_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    usuario_id = data.get("usuarioId")

    if not usuario_id:
        return JsonResponse({'error': 'Se requiere ID de usuario'}, status=400)

    # Obtener la actividad
    actividad = actividades_collection.find_one({"_id": ObjectId(actividad_id)})

    if not actividad:
        return JsonResponse({'error': 'Actividad no encontrada'}, status=404)

    # Verificar si la actividad está cerrada
    if actividad.get("estado") == "cerrado":
        return JsonResponse({'error': 'La actividad está cerrada'}, status=400)

    # Verificar si el usuario está registrado
    usuarios_registrados = actividad.get("usuariosRegistrados", [])
    usuario_encontrado = False
    for usuario in usuarios_registrados:
        if usuario.get("usuarioId") == usuario_id:
            usuario_encontrado = True
            break

    if not usuario_encontrado:
        return JsonResponse({'error': 'Usuario no registrado en esta actividad'}, status=404)

    # Eliminar usuario y actualizar cupos
    result = actividades_collection.update_one(
        {"_id": ObjectId(actividad_id)},
        {
            "$pull": {"usuariosRegistrados": {"usuarioId": usuario_id}},
            "$inc": {"cuposDisponibles": 1}
        }
    )

    # Actualizar estado si estaba completo
    actividad_actualizada = actividades_collection.find_one({"_id": ObjectId(actividad_id)})
    if actividad_actualizada.get("estado") == "completo" and actividad_actualizada.get("cuposDisponibles") > 0:
        actividades_collection.update_one(
            {"_id": ObjectId(actividad_id)},
            {"$set": {"estado": "abierto"}}
        )

    return JsonResponse({
        'message': 'Registro de usuario cancelado correctamente',
        'cuposRestantes': actividad_actualizada.get("cuposDisponibles")
    }, status=200)


@csrf_exempt
@jwt_required
def cambiar_estado_actividad(request, actividad_id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    nuevo_estado = data.get("estado")

    if nuevo_estado not in ["abierto", "completo", "cerrado"]:
        return JsonResponse({'error': 'Estado no válido. Debe ser "abierto", "completo" o "cerrado"'}, status=400)

    # Si el estado es "completo", verificar que no haya cupos disponibles
    if nuevo_estado == "completo":
        actividad = actividades_collection.find_one({"_id": ObjectId(actividad_id)})
        if actividad and actividad.get("cuposDisponibles", 0) > 0:
            return JsonResponse({'error': 'No se puede marcar como completo mientras haya cupos disponibles'},
                                status=400)

    result = actividades_collection.update_one(
        {"_id": ObjectId(actividad_id)},
        {"$set": {"estado": nuevo_estado}}
    )

    if result.matched_count == 0:
        return JsonResponse({'error': 'Actividad no encontrada'}, status=404)

    return JsonResponse({'message': f'Estado de actividad actualizado a "{nuevo_estado}"'}, status=200)


@csrf_exempt
@jwt_required
def obtener_usuarios_registrados(request, actividad_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    actividad = actividades_collection.find_one({"_id": ObjectId(actividad_id)})

    if not actividad:
        return JsonResponse({'error': 'Actividad no encontrada'}, status=404)

    return JsonResponse({
        'usuarios': actividad.get("usuariosRegistrados", []),
        'cupoMaximo': actividad.get("cupoMaximo"),
        'cuposDisponibles': actividad.get("cuposDisponibles", actividad.get("cupoMaximo")),
        'estado': actividad.get("estado", "abierto")
    }, status=200)

@csrf_exempt
@jwt_required
def obtener_actividades_usuario(request, usuario_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    # Buscar actividades donde el usuario está inscrito
    actividades = list(actividades_collection.find(
        {"usuariosRegistrados.usuarioId": usuario_id}
    ))

    if not actividades:
        return JsonResponse([], safe=False, status=200)

    actividades_serializadas = []
    for actividad in actividades:
        # Convertir fechas y serializar la actividad igual que en obtener_actividades
        fecha_inicio = actividad.get("fechaInicio")
        if isinstance(fecha_inicio, str):
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            except ValueError:
                fecha_inicio = None
        elif isinstance(fecha_inicio, datetime):
            fecha_inicio = fecha_inicio.isoformat()

        fecha_fin = actividad.get("fechaFin")
        if isinstance(fecha_fin, str):
            try:
                fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
            except ValueError:
                fecha_fin = None
        elif isinstance(fecha_fin, datetime):
            fecha_fin = fecha_fin.isoformat()

        actividades_serializadas.append({
            "id": str(actividad.get("_id")),
            "nombre": actividad.get("nombre"),
            "descripcion": actividad.get("descripcion"),
            "fechaInicio": fecha_inicio,
            "fechaFin": fecha_fin,
            "horaInicio": actividad.get("horaInicio"),
            "horaFin": actividad.get("horaFin"),
            "cupoMaximo": actividad.get("cupoMaximo"),
            "cuposDisponibles": actividad.get("cuposDisponibles"),
            "recursos": actividad.get("recursos"),
            "categoria": actividad.get("categoria"),
            "imagen": actividad.get("imagen"),
            "creado": actividad.get("creado").isoformat() if actividad.get("creado") else None,
            "estado": actividad.get("estado", "abierto"),
            "profesorId": actividad.get("profesorId")
        })

    return JsonResponse(actividades_serializadas, safe=False, status=200)