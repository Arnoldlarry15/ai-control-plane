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
Error handlers for the gateway.

Standardizes error responses across the API.
"""

import logging
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ControlPlaneError(Exception):
    """Base exception for control plane errors."""
    
    def __init__(self, message: str, status_code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class KillSwitchActiveError(ControlPlaneError):
    """Raised when kill switch blocks execution."""
    
    def __init__(self, reason: str = "Kill switch is active"):
        super().__init__(
            message=reason,
            status_code=status.HTTP_403_FORBIDDEN,
            details={"error_type": "kill_switch_active"},
        )


class PolicyViolationError(ControlPlaneError):
    """Raised when policy blocks execution."""
    
    def __init__(self, policy_id: str, reason: str, explanation: Dict[str, Any] = None):
        super().__init__(
            message=f"Policy violation: {reason}",
            status_code=status.HTTP_403_FORBIDDEN,
            details={
                "error_type": "policy_violation",
                "policy_id": policy_id,
                "explanation": explanation,
            },
        )


class AgentNotFoundError(ControlPlaneError):
    """Raised when agent is not registered."""
    
    def __init__(self, agent_id: str):
        super().__init__(
            message=f"Agent not found: {agent_id}",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_type": "agent_not_found", "agent_id": agent_id},
        )


class ExecutionError(ControlPlaneError):
    """Raised when AI execution fails."""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Execution failed: {reason}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_type": "execution_error"},
        )


async def control_plane_error_handler(request: Request, exc: ControlPlaneError) -> JSONResponse:
    """Handle control plane specific errors."""
    logger.error(f"Control plane error: {exc.message}", exc_info=True)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Request validation failed",
            "details": exc.errors(),
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "request_id": getattr(request.state, "request_id", None),
        },
    )


def register_error_handlers(app: FastAPI):
    """Register all error handlers with the app."""
    app.add_exception_handler(ControlPlaneError, control_plane_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    logger.info("Error handlers registered")
