# Copyright 2024 AI Control Plane Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Middleware for request processing.

Handles logging, timing, security, and identity tracking for all requests.

Phase 2 Enhancement: Extract and propagate identity metadata.
"""

import logging
import time
import uuid
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class IdentityMiddleware(BaseHTTPMiddleware):
    """
    Extract and propagate identity metadata for all requests.
    
    Phase 2: Every request carries identity information.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract identity information from request
        # In production, this would come from JWT, OAuth, or API key
        
        # For now, extract from headers or use defaults
        user_id = request.headers.get("X-User-ID")
        user_email = request.headers.get("X-User-Email")
        user_role = request.headers.get("X-User-Role")
        api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization")
        
        # Store in request state for downstream use
        request.state.user_id = user_id
        request.state.user_email = user_email
        request.state.user_role = user_role
        request.state.api_key = api_key
        request.state.source_ip = request.client.host if request.client else None
        request.state.user_agent = request.headers.get("User-Agent")
        
        # Process request
        response = await call_next(request)
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses with identity context."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID (correlation ID)
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.correlation_id = request_id  # Use same as correlation ID
        
        # Extract identity if available
        user_id = getattr(request.state, "user_id", None)
        
        # Log request with identity
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"request_id={request_id} user_id={user_id}"
        )
        
        # Time the request
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log response with identity
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"status={response.status_code} "
            f"duration_ms={duration_ms} "
            f"request_id={request_id} "
            f"user_id={user_id}"
        )
        
        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = request_id
        response.headers["X-Duration-MS"] = str(duration_ms)
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


def add_middleware(app: FastAPI):
    """Add all middleware to the app."""
    app.add_middleware(IdentityMiddleware)  # Phase 2: Extract identity first
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    logger.info("Middleware configured with identity tracking")
