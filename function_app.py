from typing import Literal
import azure.functions as func
import logging
import json
import openai
from src.api import UserThread

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
ut = UserThread()

class EmptyResponse(func.HttpResponse):
    def __init__(self, status_code: int = 200):
        super().__init__(status_code=status_code)

class JsonResponse(func.HttpResponse):
    def __init__(self, data: dict, status_code: int = 200):
        super().__init__(json.dumps(data), status_code=status_code, mimetype="application/json")

class JsonErrorResponse(JsonResponse):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(data={"error": str(message)}, status_code=status_code)


@app.route(route="/ask", methods=[func.HttpMethod.POST])
def ask(req: func.HttpRequest) -> func.HttpResponse:
    thread_id = req.form.get("thread-id", None)
    message = req.form.get("message", None)

    if message is None:
        return JsonErrorResponse("Message is required", 400)


    try:
        thread_id, answer = ut.ask(message, thread_id)
        return JsonResponse({
            "thread-id": thread_id,
            "answer": answer
        }, 200)
    except Exception as e:
        return JsonErrorResponse(e)


@app.route(route="/thread", methods=[func.HttpMethod.GET])
def get_thread(req: func.HttpRequest) -> func.HttpResponse:
    thread_id = req.params.get("thread-id", None)

    if thread_id is None:
        return JsonErrorResponse("Thread ID is required", 400)

    asc = req.params.get("order", "desc").lower() == "asc"

    try:
        messages = ut.list_messages(thread_id, asc=asc)
        return JsonResponse({
            "thread-id": thread_id,
            "messages": messages
        }, 200)
    except openai.NotFoundError:
        return JsonErrorResponse(f"Thread {thread_id} not found", 404)
    except Exception as e:
        return JsonErrorResponse(e)

@app.route(route="/thread", methods=[func.HttpMethod.DELETE])
def clear_thread(req: func.HttpRequest) -> func.HttpResponse:
    thread_id = req.form.get("thread-id", None)

    if thread_id is None:
        return JsonErrorResponse("Thread ID is required", 400)

    try:
        ut.delete_thread(thread_id)
        return EmptyResponse()
    except openai.NotFoundError:
        return JsonErrorResponse(f"Thread {thread_id} not found", 404)
    except Exception as e:
        return JsonErrorResponse(e)
