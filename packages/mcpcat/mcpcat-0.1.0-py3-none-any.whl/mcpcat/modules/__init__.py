"""MCPCat modules."""

from .compatibility import is_compatible_server, is_fastmcp_server
from .context_parameters import (
    add_context_parameter_to_schema,
    add_context_parameter_to_tools,
)
from .internal import get_mcpcat_data, has_mcpcat_data, set_mcpcat_data
from .logging import log_error, log_info, log_trace, log_warning
from .session import capture_session_info, get_unknown_or_stdio_session
from .tools import handle_report_missing
from .tracing import record_trace

__all__ = [
    # Compatibility
    "is_compatible_server",
    "is_fastmcp_server",
    # Context parameters
    "add_context_parameter_to_schema",
    "add_context_parameter_to_tools",
    # Internal
    "get_mcpcat_data",
    "has_mcpcat_data",
    "set_mcpcat_data",
    # Logging
    "log_error",
    "log_info",
    "log_trace",
    "log_warning",
    # Redaction
    # Session
    "get_unknown_or_stdio_session",
    "capture_session_info",
    # Tools
    "handle_report_missing",
    # Tracing
    "record_trace",
]
