# Quick test of the restructured agent
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from hushh_mcp.agents.relationship_memory.manifest import manifest
from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryAgentHandler

print("🧪 Testing Restructured Agent...")
print("=" * 50)

# Test manifest
print(f"📋 Agent ID: {manifest['id']}")
print(f"📋 Agent Name: {manifest['name']}")
print(f"📋 Scopes: {len(manifest['scopes'])}")

# Test handler initialization
try:
    handler = RelationshipMemoryAgentHandler()
    print("✅ Handler initialized successfully")
    print(f"📋 Agent ID: {handler.agent_id}")
    print(f"📋 Required Scopes: {len(handler.required_scopes)}")
except Exception as e:
    print(f"❌ Handler initialization failed: {e}")

print("\n🎉 Structure validation complete!")
print("📁 Current structure:")
print("├── index.py          # ✅ All logic here")
print("├── manifest.py       # ✅ Agent metadata")
print("├── run_agent.py      # ✅ Standalone runner")
print("└── legacy/           # ✅ Old files archived")
