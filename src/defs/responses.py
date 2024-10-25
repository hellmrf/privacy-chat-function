import azure.functions as func
import json


class EmptyResponse(func.HttpResponse):

    def __init__(self, status_code: int = 200):
        super().__init__(status_code=status_code)


class JsonResponse(func.HttpResponse):

    def __init__(self, data: dict, status_code: int = 200):
        super().__init__(json.dumps(data),
                         status_code=status_code,
                         mimetype="application/json")


class JsonErrorResponse(JsonResponse):

    def __init__(self, message: str | Exception, status_code: int = 500):
        if isinstance(message, Exception):
            message = str(message)

        super().__init__(data={"error": message}, status_code=status_code)


__all__ = [EmptyResponse, JsonResponse, JsonErrorResponse]
