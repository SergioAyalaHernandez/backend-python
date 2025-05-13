from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .auth import create_user, authenticate_user, generate_tokens, refresh_access_token, get_users_paginated, get_user_by_id

@csrf_exempt
def register_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    required_fields = ["email", "nombre", "identificacion", "password", "rol"]
    for field in required_fields:
        if field not in data:
            return JsonResponse({'error': f'El campo {field} es requerido'}, status=400)

    user, error = create_user(
        data.get("email"),
        data.get("nombre"),
        data.get("identificacion"),
        data.get("password"),
        data.get("rol")
    )

    if error:
        if "email ya está registrado" in error:
            return JsonResponse({'error': error}, status=409)
        elif "identificación ya está registrada" in error:
            return JsonResponse({'error': error}, status=409)
        else:
            return JsonResponse({'error': error}, status=400)

    return JsonResponse({'message': 'Usuario creado correctamente'}, status=201)

@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    data = json.loads(request.body)
    user = authenticate_user(data.get("email"), data.get("password"))
    if not user:
        return JsonResponse({'error': 'Credenciales inválidas'}, status=401)

    access, refresh = generate_tokens(user)

    user_data = {
        'email': user.get('email'),
        'nombre': user.get('nombre'),
        'identificacion': user.get('identificacion'),
        'rol': user.get('rol'),
        'id': str(user.get('_id')),
    }

    return JsonResponse({
        'user': user_data,
        'access': access,
        'refresh': refresh
    }, status=200)


@csrf_exempt
def refresh_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    data = json.loads(request.body)
    new_token = refresh_access_token(data.get("refresh"))
    if not new_token:
        return JsonResponse({'error': 'Refresh token inválido o expirado'}, status=401)
    return JsonResponse({'access': new_token}, status=200)

@csrf_exempt
def users_list_view(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))

    users, total = get_users_paginated(page, per_page)

    return JsonResponse({
        'users': users,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }, status=200)


@csrf_exempt
def user_detail_view(request, user_id):

    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    user = get_user_by_id(user_id)
    if not user:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

    return JsonResponse({'user': user}, status=200)

@csrf_exempt
def delete_user_view(request, user_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    from .auth import delete_user_by_id

    success = delete_user_by_id(user_id)
    if not success:
        return JsonResponse({'error': 'Usuario no encontrado o no eliminado'}, status=404)

    return JsonResponse({'message': 'Usuario eliminado correctamente'}, status=200)


@csrf_exempt
def update_user_view(request, user_id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    from .auth import update_user_by_id

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    user = update_user_by_id(user_id, data)
    if not user:
        return JsonResponse({'error': 'Usuario no encontrado o sin cambios'}, status=404)

    return JsonResponse({'message': 'Usuario actualizado correctamente', 'user': user}, status=200)
