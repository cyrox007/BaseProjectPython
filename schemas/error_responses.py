from typing import Dict, Any

ERROR_RESPONSES = {
    400: {"description": "Bad Request", "content": {"application/json": {"example": {"detail": "Bad request"}}}},
    401: {"description": "Unauthorized", "content": {"application/json": {"example": {"detail": "Not authenticated"}}}},
    403: {"description": "Forbidden", "content": {"application/json": {"example": {"detail": "Permission denied"}}}},
    404: {"description": "Not Found", "content": {"application/json": {"example": {"detail": "Resource not found"}}}},
    409: {"description": "Conflict", "content": {"application/json": {"example": {"detail": "Resource conflict"}}}},
    422: {"description": "Validation Error", "content": {"application/json": {"example": {"detail": [{"loc": ["body", "field"], "msg": "error", "type": "value_error"}]}}}},
}