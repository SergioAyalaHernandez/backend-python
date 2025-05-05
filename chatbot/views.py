from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from backend.mongo_client import get_collection
from bson import ObjectId
from bson.errors import InvalidId


chatbot_collection = get_collection("chatbot_messages")


@csrf_exempt
def create_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chatbot_collection.insert_one(data)
        return JsonResponse({'message': 'Mensaje creado correctamente'}, status=201)


def get_messages(request):
    if request.method == 'GET':
        messages = list(chatbot_collection.find({}, {'_id': 0}))
        return JsonResponse(messages, safe=False)


@csrf_exempt
def update_message(request, message_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        result = chatbot_collection.update_one({'id': message_id}, {'$set': data})
        if result.matched_count == 0:
            return JsonResponse({'error': 'Mensaje no encontrado'}, status=404)
        return JsonResponse({'message': 'Mensaje actualizado correctamente'})


@csrf_exempt
def delete_message(request, message_id):
    if request.method == 'DELETE':
        result = chatbot_collection.delete_one({'id': message_id})
        if result.deleted_count == 0:
            return JsonResponse({'error': 'Mensaje no encontrado'}, status=404)
        return JsonResponse({'message': 'Mensaje eliminado correctamente'})

@csrf_exempt
def list_questions(request):
    if request.method == 'GET':
        documents = chatbot_collection.find({}, {'menu_text': 1, 'response_text': 1})
        results = []
        for doc in documents:
            doc['id'] = str(doc['_id'])  # convertir ObjectId a string
            del doc['_id']  # opcional: elimina el campo MongoDB por defecto
            results.append(doc)
        return JsonResponse(results, safe=False)



@csrf_exempt
def get_answer(request, message_id):
    if request.method == 'GET':
        try:
            object_id = ObjectId(message_id)  # convierte string a ObjectId
        except InvalidId:
            return JsonResponse({'error': 'ID inválido'}, status=400)

        message = chatbot_collection.find_one({'_id': object_id}, {'_id': 0})
        if message:
            return JsonResponse(message, safe=False)
        return JsonResponse({'error': 'Mensaje no encontrado'}, status=404)



