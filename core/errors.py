"""
Structured exceptions for inbound order automation

All exceptions are agent-safe and provide clear error messages.
"""


class InboundOrderError(Exception):
    """Base exception for all inbound order automation errors"""
    pass


class ExtractionError(InboundOrderError):
    """Raised when Gmail extraction fails"""
    pass


class SubmissionError(InboundOrderError):
    """Raised when Arcadia order submission fails"""
    pass


class ValidationError(InboundOrderError):
    """Raised when input validation fails"""
    pass


class ScriptExecutionError(InboundOrderError):
    """Raised when subprocess script execution fails"""
    def __init__(self, message: str, exit_code: int = None, stderr: str = None):
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr


class TimeoutError(InboundOrderError):
    """Raised when automation script times out"""
    def __init__(self, message: str, timeout_seconds: int):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds

