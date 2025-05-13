import jwt as pyjwt 
import datetime
from django.conf import settings
from werkzeug.security import generate_password_hash, check_password_hash
from .mongo import get_collection
from bson.objectid import ObjectId, InvalidId


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'

def create_user(email, nombre, identificacion, password, rol):
    users = get_collection("users")
    
    # Verificar si existe un usuario con el mismo email
    if users.find_one({'email': email}):
        return None, "El email ya está registrado"
    
    # Verificar si existe un usuario con la misma identificación
    if users.find_one({'identificacion': identificacion}):
        return None, "La identificación ya está registrada"
        
    hashed_password = generate_password_hash(password)
    user = {
        "email": email,
        "nombre": nombre,
        "identificacion": identificacion,
        "password": hashed_password,
        "rol": rol
    }
    users.insert_one(user)
    return user, None

def authenticate_user(email, password):
    users = get_collection("users")
    user = users.find_one({"email": email})
    if user and check_password_hash(user["password"], password):
        return user
    return None

def generate_tokens(user):
    payload = {
        'user_id': str(user['_id']),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        'token_type': 'access'
    }
    access_token = pyjwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM) 

    refresh_payload = {
        'user_id': str(user['_id']),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'token_type': 'refresh'
    }
    refresh_token = pyjwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM) 
    return access_token, refresh_token

def refresh_access_token(refresh_token):
    try:
        payload = pyjwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM]) 
        if payload['token_type'] != 'refresh':
            raise pyjwt.InvalidTokenError
        new_payload = {
            'user_id': payload['user_id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
            'token_type': 'access'
        }
        return pyjwt.encode(new_payload, SECRET_KEY, algorithm=ALGORITHM)  
    except pyjwt.ExpiredSignatureError:
        return None
    except pyjwt.InvalidTokenError:
        return None

def get_users_paginated(page, per_page):
    users = get_collection("users")
    skip = (page - 1) * per_page
    cursor = users.find().skip(skip).limit(per_page)
    total = users.count_documents({})
    user_list = []
    for user in cursor:
        user['_id'] = str(user['_id'])  
        user.pop("password", None)
        user_list.append(user)
    return user_list, total

def get_user_by_id(user_id):
    users = get_collection("users")
    try:
        object_id = ObjectId(user_id) 
    except InvalidId:
        print("ID inválido para ObjectId")
        return None

    user = users.find_one({"_id": object_id})
    if user:
        user['_id'] = str(user['_id'])
        user.pop("password", None)
        return user
    return None
def delete_user_by_id(user_id):
    users = get_collection("users")
    actividades = get_collection("actividades")

    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        print("ID inválido para ObjectId")
        return False

    # Primero verificamos si el usuario existe y obtenemos su rol
    user = users.find_one({"_id": object_id})
    if not user:
        return False

    # Si es un profesor, eliminamos todas sus actividades asociadas
    if user.get("rol") == "profesor":
        actividades.delete_many({"profesorId": str(object_id)})

    # Finalmente eliminamos el usuario
    result = users.delete_one({"_id": object_id})
    return result.deleted_count > 0


def update_user_by_id(user_id, data):
    users = get_collection("users")
    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        print("ID inválido para ObjectId")
        return None

    update_fields = {}
    for key in ['email', 'nombre', 'identificacion', 'rol']:
        if key in data:
            update_fields[key] = data[key]

    if 'password' in data:
        update_fields['password'] = generate_password_hash(data['password'])

    if not update_fields:
        return None 

    result = users.update_one({"_id": object_id}, {"$set": update_fields})
    if result.modified_count > 0:
        user = users.find_one({"_id": object_id})
        user['_id'] = str(user['_id'])
        user.pop("password", None)
        return user
    return None
