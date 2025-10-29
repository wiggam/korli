# app/routes/chat_route.py
from __future__ import annotations

from typing import AsyncGenerator, Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uuid


def _new_thread_id() -> str:
    return str(uuid.uuid4())

router = APIRouter()


class ChatInput(BaseModel):
    """
    One payload model for both init and follow-up turns.
    - thread_id: optional; if omitted, server will create one and return it
    - message: optional; omit on first turn to trigger initial question
    """
    thread_id: Optional[str] = Field(None, description="Stable thread/session identifier")
    message: Optional[str] = Field(None, description="User message; omit on first turn to initialize")

    # Initialization params used by initialize_state in your graph
    student_level: Optional[str] = None
    foreign_language: Optional[str] = None
    native_language: Optional[str] = None

    # Optional extras
    tutor_gender: Optional[str] = Field(None, pattern="^(male|female)$")
    student_gender: Optional[str] = Field(None, pattern="^(male|female)$")


def _build_state(body: ChatInput) -> Dict[str, Any]:
    """
    Build the graph state payload. Keep it JSON-serializable.
    If body.message is None, omit 'messages' so the graph routes to generate_initial_question.
    """
    state: Dict[str, Any] = {}
    if body.message is not None:
        state["messages"] = [{"role": "user", "content": body.message}]

    # Include init fields only if provided
    if body.student_level is not None:
        state["student_level"] = body.student_level
    if body.foreign_language is not None:
        state["foreign_language"] = body.foreign_language
    if body.native_language is not None:
        state["native_language"] = body.native_language
    if body.tutor_gender is not None:
        state["tutor_gender"] = body.tutor_gender
    if body.student_gender is not None:
        state["student_gender"] = body.student_gender

    return state


def _validate_init_requirements(body: ChatInput):
    """
    For the very first turn (no message), ensure we have the three init fields.
    """
    if body.message is None:
        missing = [
            name for name, val in [
                ("student_level", body.student_level),
                ("foreign_language", body.foreign_language),
                ("native_language", body.native_language),
            ]
            if not val
        ]
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required initialization fields for first turn: {', '.join(missing)}",
            )


@router.post("/chat/invoke", status_code=status.HTTP_200_OK)
async def chat_invoke(body: ChatInput, request: Request):
    """
    One-shot invocation:
      - If message is omitted: initializes the conversation and returns the model's initial question.
      - If message is present: continues the conversation.
    If thread_id is omitted, server generates one and returns it.
    """
    graph = getattr(request.app.state, "graph", None)
    if graph is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")

    # Ensure init fields on first call
    _validate_init_requirements(body)

    # Ensure we have a thread_id
    thread_id = body.thread_id or _new_thread_id()

    state = _build_state(body)
    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = await graph.ainvoke(state, config=config)
        # Attach thread_id so FE can persist it
        return {
            "thread_id": thread_id,
            "result": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph invoke failed: {e}") from e


@router.post("/chat/stream")
async def chat_stream(body: ChatInput, request: Request):
    """
    Server-Sent Events (SSE) streaming endpoint.
    Behaves like /chat/invoke but streams events as they occur.
    If thread_id is omitted, server generates one and emits it as an SSE comment line.
    """
    graph = getattr(request.app.state, "graph", None)
    if graph is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")

    _validate_init_requirements(body)

    thread_id = body.thread_id or _new_thread_id()
    state = _build_state(body)
    config = {"configurable": {"thread_id": thread_id}}

    async def event_generator() -> AsyncGenerator[str, None]:
        # Send the thread_id up front so the FE can store it
        yield f": thread_id {thread_id}\n\n"  # SSE comment line (won't be parsed as data)
        try:
            async for ev in graph.astream_events(state, config=config, version="v2"):
                # ev is a dict; stream as NDJSON lines for SSE
                yield f"data: {ev}\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
