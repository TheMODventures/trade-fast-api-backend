from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.api_key import verify_api_key, get_api_key_from_header


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate API key for all requests
    """

    # Paths that don't require API key authentication
    EXCLUDED_PATHS = [
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/vapi/webhook",  # VAPI webhook - called by VAPI servers, not frontend
    ]

    async def dispatch(self, request: Request, call_next):
        # Check if path is excluded from authentication
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # Get API key from Authorization header
        authorization = request.headers.get("Authorization")
        api_key = get_api_key_from_header(authorization)

        print("API Key from Header:", api_key)
        # Verify API key
        if not verify_api_key(api_key):
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid or missing API key",
                    "message": "Please provide a valid API key in the Authorization header",
                    "format": "Authorization: Bearer <your_api_key>"
                }
            )

        # API key is valid, proceed with request
        response = await call_next(request)
        return response
