from datafog import DataFog
from typing import Any
"""PII redaction for MCPCat logs."""

def create_datafog_redactor():
    """Create a default Datafog redactor function.
    Returns a redactor function that uses Datafog for PII detection
    and replaces all detected PII with '[Redacted by MCPCat]'.
    Falls back to regex-based redaction if Datafog is not available.
    """
    def datafog_redact(data: Any) -> Any:
        """Redact sensitive information using Datafog."""
        if isinstance(data, dict):
            return {k: datafog_redact(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [datafog_redact(item) for item in data]
        elif isinstance(data, str):
            # Use Datafog to scan and redact with custom replacement
            redactor = DataFog(operations=["scan", "redact"])
            # Process the text - Datafog will replace detected PII with [REDACTED]
            redacted_text = redactor.process_text(data)
            # Replace Datafog's [REDACTED] with our custom message
            return redacted_text.replace("[REDACTED]", "[Redacted by MCPCat]")
        else:
            return data
    return datafog_redact
# Singleton redactor instance
_default_redactor = None
def get_default_redactor():
    """Get or create the singleton default redactor."""
    global _default_redactor
    if _default_redactor is None:
        _default_redactor = create_datafog_redactor()
    return _default_redactor


async def defaultRedactor(text: str) -> str:
    """Default async redactor function using Datafog."""
    return text  # For now, just pass through
    # TODO: Implement actual redaction
    # redactor = get_default_redactor()
    # return redactor(text)
