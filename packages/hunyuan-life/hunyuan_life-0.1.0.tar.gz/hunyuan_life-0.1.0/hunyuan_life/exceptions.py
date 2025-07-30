"""Custom exceptions for Yuanqi MCP."""

class YuanqiAPIError(Exception):
    """Base exception for Minimax API errors."""
    pass

class YuanqiAuthError(YuanqiAPIError):
    """Authentication related errors."""
    pass

class YuanqiRequestError(YuanqiAPIError):
    """Request related errors."""
    pass

class YuanqiTimeoutError(YuanqiAPIError):
    """Timeout related errors."""
    pass

class YuanqiValidationError(YuanqiAPIError):
    """Validation related errors."""
    pass 

class YuanqiMcpError(YuanqiAPIError):
    pass
