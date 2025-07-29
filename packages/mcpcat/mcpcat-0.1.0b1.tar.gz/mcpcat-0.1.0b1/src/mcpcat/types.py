"""Type definitions for MCPCat."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, TypedDict

from pydantic import BaseModel

# Type alias for identify function
IdentifyFunction = Callable[[dict[str, Any], Any], Optional["UserData"]]
# Type alias for redaction function
RedactionFunction = Callable[[str], str | Awaitable[str]]

# Import default redactor
from .modules.redaction import defaultRedactor


class UserData(TypedDict, total=False):
    """User identification data."""
    userId: str
    userData: dict[str, str] | None


@dataclass
class MCPCatOptions:
    """Configuration options for MCPCat."""
    enableToolCallContext: bool = True
    enableTracing: bool = True
    enableReportMissing: bool = True
    identify: IdentifyFunction | None = None
    redactSensitiveInformation: RedactionFunction | None = defaultRedactor


@dataclass
class MCPSession:
    """Session information."""
    id: str
    created: datetime
    last_used: datetime


class Trace(BaseModel):
    """Pydantic model for structured trace data."""
    # Structured fields
    timestamp: datetime
    session_id: str
    user_id: str
    event_type: str
    tool_name: str
    is_error: bool
    duration: float
    context: str

    # Unstructured fields
    arguments: str = ""
    response: str = ""


@dataclass
class MCPCatData:
    """Internal data structure for tracking."""
    options: MCPCatOptions
    traces: list[Trace] = field(default_factory=list)
    identified_sessions: dict[str, str] = field(default_factory=dict)
    unknown_session: MCPSession | None = None
