"""Logging functionality for MCPCat."""

import json
import os
from datetime import datetime
from typing import Any

from ..types import MCPCatOptions, Trace

logPath = "mcpcat.log"  # Default log file path

async def log_trace(trace: Trace, options: MCPCatOptions) -> None:
    """Log a tool call trace."""
    # Convert Trace to dict using Pydantic's model_dump
    log_data = trace.model_dump()
    # Convert datetime to ISO format string for JSON serialization
    log_data["timestamp"] = trace.timestamp.isoformat()

    # Apply redaction if configured and function exists
    if hasattr(options, 'redactSensitiveInformation') and options.redactSensitiveInformation is not None:
        if log_data.get("context"):
            log_data["context"] = await redact_message(log_data["context"], options)
        if log_data.get("arguments"):
            log_data["arguments"] = await redact_message(log_data["arguments"], options)
        if log_data.get("response"):
            log_data["response"] = await redact_message(log_data["response"], options)

    _write_log(log_data, options)


def log_info(message: str, data: dict[str, Any], options: MCPCatOptions) -> None:
    """Log an informational message."""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "event": "info",
        "message": message,
        **data
    }

    _write_log(log_data, options)


def log_warning(message: str, data: dict[str, Any], options: MCPCatOptions) -> None:
    """Log a warning message."""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "event": "warning",
        "message": message,
        **data
    }

    _write_log(log_data, options)


def log_error(message: str, error: Exception, data: dict[str, Any], options: MCPCatOptions) -> None:
    """Log an error message."""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "event": "error",
        "message": message,
        "error": str(error),
        "error_type": type(error).__name__,
        **data
    }

    _write_log(log_data, options)


def _write_log(log_data: dict[str, Any], options: MCPCatOptions) -> None:
    """Write log data to file."""
    try:
        # Ensure log directory exists
        log_dir = os.path.dirname(logPath)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Write to log file in JSON format
        with open(logPath, "a") as f:
            f.write(json.dumps(log_data) + "\n")
    except Exception:
        # Silently fail - we don't want logging errors to break the server
        pass


def write_to_log(message: str, options: MCPCatOptions) -> None:
    """Write a simple text message to log (TypeScript-compatible format)."""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] {message}\n"

    try:
        # Ensure log directory exists
        log_dir = os.path.dirname(logPath)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Write to log file
        with open(logPath, "a") as f:
            f.write(log_entry)
    except Exception:
        # Silently fail - we don't want logging errors to break the server
        pass


async def redact_message(message: str, options: MCPCatOptions) -> str:
    """Apply redaction to a message if enabled."""
    if not hasattr(options, 'redactSensitiveInformation'):
        return message

    try:
        if options.redactSensitiveInformation:
            return await options.redactSensitiveInformation(message)
        return message
    except Exception as e:
        write_to_log(f"Warning: Failed to redact message - Error: {e}", options)
        return message


async def log_with_session(server, session_id: str, user_id: str | None, message: str, options: MCPCatOptions) -> None:
    """Log a message with session information (TypeScript-compatible format)."""
    try:
        user_info = f" (User: {user_id})" if user_id else ""
        full_message = f"[Session: {session_id}{user_info}] {message}"

        # Apply redaction
        redacted_message = await redact_message(full_message, options)
        write_to_log(redacted_message, options)
    except Exception as e:
        write_to_log(f"Warning: Failed to log message - {e}", options)
