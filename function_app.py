import azure.functions as func
from src import UserThread
from src.defs import *

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
ut = UserThread()


@app.route(route="ask", methods=[func.HttpMethod.POST])
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
    except StatusCodeError as e:
        return JsonErrorResponse(e.message, e.status_code)
    except Exception as e:
        return JsonErrorResponse(e)


@app.route(route="thread", methods=[func.HttpMethod.GET])
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
    except StatusCodeError as e:
        return JsonErrorResponse(e.message, e.status_code)
    except Exception as e:
        return JsonErrorResponse(e)

@app.route(route="thread", methods=[func.HttpMethod.DELETE])
def clear_thread(req: func.HttpRequest) -> func.HttpResponse:
    thread_id = req.params.get("thread-id", None) or req.form.get("thread-id", None)

    if thread_id is None:
        return JsonErrorResponse("Thread ID is required", 400)

    try:
        ut.delete_thread(thread_id)
        return EmptyResponse()
    except StatusCodeError as e:
        return JsonErrorResponse(e.message, e.status_code)
    except Exception as e:
        return JsonErrorResponse(e)
