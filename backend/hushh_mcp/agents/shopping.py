# hushh_mcp/agents/shopping.py

from __future__ import annotations

from typing import List
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID


class HushhShoppingAgent:
    """
    A mock shopping agent that returns personalized offers if valid consent is provided.
    """

    required_scope = ConsentScope.VAULT_READ_EMAIL

    def __init__(self, agent_id: str = "agent_shopper"):
        self.agent_id = agent_id

    def search_deals(self, user_id: UserID, token_str: str) -> List[str]:
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)

        if not valid:
            raise PermissionError(f"Consent validation failed: {reason}")

        if token.user_id != user_id:
            raise PermissionError("Token user ID does not match the provided user")

        print(f"✅ Consent verified for user {user_id} and agent {self.agent_id} on scope {token.scope}")

        # Return mock personalized deals
        return [
            "💻 10% off MacBook Air for Hushh users",
            "🎧 Free AirPods with iPhone 16 preorder",
            "📦 20% cashback on your next Amazon order",
            "🛒 Curated fashion drops based on your inbox purchases"
        ]
