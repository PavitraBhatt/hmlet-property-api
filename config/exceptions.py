from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    """Keep error payloads in one predictable shape: {"detail": ..., "errors": {...}}."""
    if isinstance(exc, IntegrityError):
        return Response(
            {"detail": "The request conflicts with existing data."},
            status=status.HTTP_409_CONFLICT,
        )

    response = exception_handler(exc, context)
    if response is None:
        return None

    data = response.data
    if isinstance(data, dict) and "detail" in data:
        response.data = {"detail": str(data["detail"])}
    elif isinstance(data, dict):
        response.data = {"detail": "Validation failed.", "errors": data}
    else:
        response.data = {"detail": "Validation failed.", "errors": data}
    return response
