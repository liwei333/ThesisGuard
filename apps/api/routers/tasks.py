"""Task dispatch endpoints.

Allows the API to enqueue tasks for the worker.
"""

import logging

from apps.worker.main import echo_task, system_health_task
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)


class TaskDispatchResponse(BaseModel):
    task_id: str
    actor: str
    status: str
    message: str


class EchoRequest(BaseModel):
    message: str = "hello"


@router.post("/health-check", response_model=TaskDispatchResponse)
async def dispatch_health_check() -> TaskDispatchResponse:
    """Dispatch a system health check task to the worker."""
    try:
        message = system_health_task.send()
        return TaskDispatchResponse(
            task_id=message.message_id,
            actor="system_health_task",
            status="queued",
            message="Health check task queued successfully",
        )
    except Exception as e:
        logger.error(f"Failed to dispatch health check task: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Task queue unavailable: {str(e)[:100]}",
        ) from e


@router.post("/echo", response_model=TaskDispatchResponse)
async def dispatch_echo(payload: EchoRequest) -> TaskDispatchResponse:
    """Dispatch an echo task to the worker (for testing)."""
    try:
        message = echo_task.send(payload.message)
        return TaskDispatchResponse(
            task_id=message.message_id,
            actor="echo_task",
            status="queued",
            message=f"Echo task queued with message: {payload.message}",
        )
    except Exception as e:
        logger.error(f"Failed to dispatch echo task: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Task queue unavailable: {str(e)[:100]}",
        ) from e
