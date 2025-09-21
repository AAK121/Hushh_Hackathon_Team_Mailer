"""MailerPanda agent for HushhMCP."""

from __future__ import annotations

# Import the main agent class with detailed error logging
try:
    from .index import MassMailerAgent
    print(f"✅ Successfully imported MassMailerAgent: {MassMailerAgent}")
except ImportError as e:
    print(f"❌ CRITICAL: Could not import MassMailerAgent: {e}")
    print(f"❌ Error type: {type(e)}")
    import traceback
    print(f"❌ Full traceback:")
    traceback.print_exc()
    MassMailerAgent = None
except Exception as e:
    print(f"❌ UNEXPECTED ERROR importing MassMailerAgent: {e}")
    print(f"❌ Error type: {type(e)}")
    import traceback
    traceback.print_exc()
    MassMailerAgent = None

# Try to import simplified agent first, fall back to creating a fallback
try:
    from .simple_agent import run as init_agent
    print("✅ Successfully imported run function from simple_agent")
except ImportError as e:
    print(f"❌ Could not import run from simple_agent: {e}")
    # Create a fallback function instead of trying to import from index
    def init_agent(*args, **kwargs):
        if MassMailerAgent is not None:
            try:
                agent = MassMailerAgent()
                return {"status": "success", "message": "MassMailerAgent available but no run function"}
            except Exception as e:
                return {"status": "error", "message": f"MassMailerAgent initialization failed: {e}"}
        return {"status": "error", "message": "Agent not available"}
    print("✅ Created fallback init_agent function")

__all__ = ['MassMailerAgent', 'init_agent']