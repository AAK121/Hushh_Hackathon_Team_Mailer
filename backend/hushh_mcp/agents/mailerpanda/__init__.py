"""MailerPanda agent for HushhMCP."""

# Try to import simplified agent first, fall back to original
try:
    from .simple_agent import run as init_agent
except ImportError:
    try:
        from .index import run as init_agent
    except ImportError:
        def init_agent(*args, **kwargs):
            return {"status": "error", "message": "Agent not available"}

__all__ = ['init_agent']