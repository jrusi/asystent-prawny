from fastapi import Request
from fastapi.responses import Response, JSONResponse
from typing import Callable

async def cors_middleware(request: Request, call_next: Callable):
    """Custom CORS middleware that runs before any other middleware or route handlers"""
    
    # Always allow these headers and methods
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Credentials": "true",
    }
    
    # Handle preflight requests
    if request.method == "OPTIONS":
        return Response(
            status_code=200,
            headers=headers
        )
    
    # Process the request
    response = await call_next(request)
    
    # Add CORS headers to response
    for key, value in headers.items():
        response.headers[key] = value
    
    return response

async def error_middleware(request: Request, call_next: Callable):
    """Custom error handling middleware"""
    try:
        return await call_next(request)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
            }
        ) 