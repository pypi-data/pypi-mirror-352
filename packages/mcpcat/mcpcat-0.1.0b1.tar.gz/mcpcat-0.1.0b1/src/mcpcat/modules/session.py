"""Session management for MCPCat."""

import uuid
from datetime import datetime, timedelta
from typing import Any

from mcp.server import Server

from mcpcat.modules.internal import get_mcpcat_data

from ..types import MCPSession, UserData
from .logging import log_info, log_warning


def get_unknown_or_stdio_session(server: Server) -> str:
    """Get or create an unknown/STDIO session."""
    data = get_mcpcat_data(server)
    now = datetime.now()

    # Check if we have an existing session
    if data.unknown_session:
        # Check if session is still valid (30 minutes)
        if now - data.unknown_session.last_used < timedelta(minutes=30):
            # Update last used time
            data.unknown_session.last_used = now
            return data.unknown_session.id

    # Create new session
    session_id = str(uuid.uuid4())
    data.unknown_session = MCPSession(
        id=session_id,
        created=now,
        last_used=now
    )

    return session_id


async def capture_session_info(server: Server, arguments: dict[str, Any] | None = None, request_context: Any | None = None ) -> tuple[str | None, str | None]:
    """Get session and user ID from request context."""
    session_id = None
    user_id = 'unidentified-user-id'

    # Extract session_id from request context if available
    if request_context is not None:
        try:
            session = request_context.session  # assumes .session is always present
            session_id = getattr(session, "session_id", None) or getattr(session, "id", None)
        except (ValueError, AttributeError):
            # No valid session in context
            pass

    # If session_id is not found, use the unknown session ID for stdio implementations
    if not session_id:
        session_id = get_unknown_or_stdio_session(server)

    data = get_mcpcat_data(server)

    found_user_for_session = data.identified_sessions.get(session_id, None)
    if found_user_for_session:
        return session_id, found_user_for_session

    # Try custom identification for user data if no user ID is found
    if data.options.identify:
        try:
            # Call identify function with (arguments, context) signature
            user_data: UserData = await data.options.identify(arguments, request_context)
            if user_data:
                user_id = user_data.get("userId")
                # Store identified session with user ID
                if user_id:
                    data.identified_sessions[session_id] = user_id
                    log_info(f"User identified (ID: {user_id})", {
                        "userId": user_id,
                        "sessionId": session_id,
                        "userData": user_data.get("userData") if user_data else None
                    }, data.options)
        except Exception as e:
            # Log identification errors
            log_warning(f"Failed to identify session: {str(e)}", {
                "sessionId": session_id,
                "error": str(e)
            }, data.options)

    return session_id, user_id
