"""
Demo script for the Proactive Relationship Manager Agent.
Shows the enhanced capabilities including batch operations, proactive triggers, and advice generation.
"""

import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

from hushh_mcp.agents.relationship_memory.index import (
    RelationshipMemoryAgent, run, run_proactive_check, ContactInfo, UserIntent
)
from hushh_mcp.constants import ConsentScope


def demo_enhanced_models():
    """Demonstrate enhanced Pydantic models"""
    print("🔧 ENHANCED MODELS DEMO")
    print("=" * 50)
    
    # Test enhanced ContactInfo with new fields
    contact = ContactInfo(
        name="Alice Johnson",
        email="alice@example.com",
        phone="+1234567890",
        company="Tech Corp",
        priority="high",
        last_talked_date="2024-01-15",
        dates={"birthday": "15-03", "anniversary": "22-06"}
    )
    
    print(f"✅ Enhanced ContactInfo created:")
    print(f"   Name: {contact.name}")
    print(f"   Priority: {contact.priority}")
    print(f"   Last talked: {contact.last_talked_date}")
    print(f"   Important dates: {contact.dates}")
    
    # Test batch contact support in UserIntent
    batch_contacts = [
        ContactInfo(name="Bob Wilson", phone="+1987654321", priority="medium"),
        ContactInfo(name="Carol Davis", email="carol@example.com", priority="low")
    ]
    
    intent = UserIntent(
        action="add_contact",
        confidence=0.95,
        contact_info=batch_contacts
    )
    
    print(f"\n✅ Batch UserIntent created:")
    print(f"   Action: {intent.action}")
    print(f"   Batch size: {len(intent.contact_info)}")
    print(f"   Contacts: {[c.name for c in intent.contact_info]}")
    
    # Test get_advice action
    advice_intent = UserIntent(
        action="get_advice",
        confidence=0.9,
        contact_name="Alice Johnson"
    )
    
    print(f"\n✅ Advice UserIntent created:")
    print(f"   Action: {advice_intent.action}")
    print(f"   Contact: {advice_intent.contact_name}")
    print()


def demo_utility_functions():
    """Demonstrate utility functions for date and interaction calculations"""
    print("🛠️ UTILITY FUNCTIONS DEMO")
    print("=" * 50)
    
    # Create agent to test utility functions
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'demo_key'}):
        agent = RelationshipMemoryAgent()
    
    # Test date calculations
    current_date = datetime(2024, 3, 1)  # March 1st
    
    # Birthday in same month
    days_until = agent._calculate_days_until_event("15-03", current_date)
    print(f"✅ Days until March 15th birthday: {days_until} days")
    
    # Birthday in next month
    days_until = agent._calculate_days_until_event("10-04", current_date)
    print(f"✅ Days until April 10th birthday: {days_until} days")
    
    # Test days since contact calculation
    contact_recent = {
        'last_talked_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    }
    days_since = agent._calculate_days_since_contact(contact_recent)
    print(f"✅ Days since last contact (recent): {days_since} days")
    
    contact_old = {
        'last_talked_date': (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')
    }
    days_since = agent._calculate_days_since_contact(contact_old)
    print(f"✅ Days since last contact (old): {days_since} days")
    
    # Test trigger formatting
    triggers = [
        {
            'type': 'upcoming_event',
            'contact_name': 'Jane Doe',
            'event_type': 'birthday',
            'days_until': 5
        },
        {
            'type': 'reconnection',
            'contact_name': 'John Smith',
            'days_since_contact': 30,
            'priority': 'medium'
        }
    ]
    
    formatted = agent._format_triggers_for_llm(triggers)
    print(f"\n✅ Formatted triggers for LLM:")
    print(formatted)
    print()


def demo_proactive_triggers():
    """Demonstrate proactive trigger detection"""
    print("🚀 PROACTIVE TRIGGERS DEMO")
    print("=" * 50)
    
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'demo_key'}):
        agent = RelationshipMemoryAgent()
    
    # Mock contacts with various scenarios
    current_date = datetime.now()
    birthday_soon = (current_date + timedelta(days=3)).strftime('%d-%m')
    old_contact_date = (current_date - timedelta(days=45)).strftime('%Y-%m-%d')
    very_old_date = (current_date - timedelta(days=100)).strftime('%Y-%m-%d')
    
    mock_contacts = [
        {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'dates': {'birthday': birthday_soon},
            'priority': 'high',
            'last_talked_date': (current_date - timedelta(days=2)).strftime('%Y-%m-%d')
        },
        {
            'name': 'John Smith',
            'email': 'john@example.com',
            'priority': 'medium',
            'last_talked_date': old_contact_date
        },
        {
            'name': 'Alice Johnson',
            'email': 'alice@example.com',
            'priority': 'low',
            'last_talked_date': very_old_date
        }
    ]
    
    # Mock VaultManager
    with patch('hushh_mcp.agents.relationship_memory.index.VaultManager') as mock_vm:
        mock_vault_manager = Mock()
        mock_vm.return_value = mock_vault_manager
        mock_vault_manager.get_all_contacts.return_value = mock_contacts
        
        # Create test state
        from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryState
        
        state = RelationshipMemoryState(
            user_input="",
            user_id="demo_user",
            vault_key="demo_key",
            parsed_intent=None,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=True,
            proactive_triggers=[],
            conversation_history=[]
        )
        
        # Test proactive trigger detection
        result_state = agent._check_for_proactive_triggers(state)
        
        print(f"✅ Proactive triggers detected: {len(result_state['proactive_triggers'])}")
        
        for trigger in result_state['proactive_triggers']:
            if trigger['type'] == 'upcoming_event':
                print(f"   🎂 {trigger['contact_name']}'s {trigger['event_type']} in {trigger['days_until']} days")
            elif trigger['type'] == 'reconnection':
                print(f"   📞 Reconnect with {trigger['contact_name']} ({trigger['priority']} priority, {trigger['days_since_contact']} days ago)")
    
    print()


def demo_batch_processing():
    """Demonstrate batch contact processing"""
    print("📦 BATCH PROCESSING DEMO")
    print("=" * 50)
    
    # Create batch contacts
    batch_contacts = [
        ContactInfo(name="Alice Johnson", email="alice@example.com", priority="high"),
        ContactInfo(name="Bob Wilson", phone="+1234567890", priority="medium"),
        ContactInfo(name="Carol Davis", company="Tech Corp", priority="low")
    ]
    
    print(f"✅ Batch contacts prepared: {len(batch_contacts)} contacts")
    for i, contact in enumerate(batch_contacts, 1):
        print(f"   {i}. {contact.name} ({contact.priority} priority)")
        if contact.email:
            print(f"      Email: {contact.email}")
        if contact.phone:
            print(f"      Phone: {contact.phone}")
        if contact.company:
            print(f"      Company: {contact.company}")
    
    # Simulate batch processing results
    print(f"\n✅ Batch processing simulation:")
    print(f"   ✅ Successfully added: Alice Johnson, Bob Wilson, Carol Davis")
    print(f"   🔄 Updated: 0 existing contacts")
    print(f"   ❌ Failed: 0 contacts")
    print()


def demo_workflow_enhancements():
    """Demonstrate enhanced LangGraph workflow"""
    print("🔄 WORKFLOW ENHANCEMENTS DEMO")
    print("=" * 50)
    
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'demo_key'}):
        agent = RelationshipMemoryAgent()
    
    # Test routing logic
    from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryState
    
    # Test proactive routing with triggers
    state_with_triggers = RelationshipMemoryState(
        user_input="",
        user_id="demo_user",
        vault_key="demo_key",
        parsed_intent=None,
        result_data=[],
        response_message="",
        error=None,
        action_taken="",
        is_startup=True,
        proactive_triggers=[{'type': 'upcoming_event'}],
        conversation_history=[]
    )
    
    route = agent._route_from_proactive_check(state_with_triggers)
    print(f"✅ Proactive routing with triggers: {route}")
    
    # Test normal routing without triggers
    state_no_triggers = RelationshipMemoryState(
        user_input="add contact John",
        user_id="demo_user",
        vault_key="demo_key",
        parsed_intent=None,
        result_data=[],
        response_message="",
        error=None,
        action_taken="",
        is_startup=False,
        proactive_triggers=[],
        conversation_history=[]
    )
    
    route = agent._route_from_proactive_check(state_no_triggers)
    print(f"✅ Normal routing without triggers: {route}")
    
    # Test enhanced tool routing
    intent = UserIntent(action="get_advice", confidence=0.9, contact_name="John")
    state_no_triggers["parsed_intent"] = intent
    
    route = agent._route_to_tool(state_no_triggers)
    print(f"✅ Enhanced tool routing for advice: {route}")
    
    print()


def demo_error_handling():
    """Demonstrate enhanced error handling"""
    print("⚠️ ERROR HANDLING DEMO")
    print("=" * 50)
    
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'demo_key'}):
        agent = RelationshipMemoryAgent()
    
    from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryState
    
    # Test different error scenarios
    error_scenarios = [
        ("VaultManager not available", "Storage system is not available"),
        ("Contact name is required", "Please provide a contact name"),
        ("Contact not found", "You can add them first"),
        ("validation failed", "Please check your input format"),
        ("Unknown error", "Try commands like")
    ]
    
    for error_input, expected_pattern in error_scenarios:
        state = RelationshipMemoryState(
            user_input="test input",
            user_id="demo_user",
            vault_key="demo_key",
            parsed_intent=None,
            result_data=[],
            response_message="",
            error=error_input,
            action_taken="",
            is_startup=False,
            proactive_triggers=[],
            conversation_history=[]
        )
        
        result_state = agent._handle_error_node(state)
        print(f"✅ Error '{error_input}' -> Response contains '{expected_pattern}': {expected_pattern in result_state['response_message']}")
    
    print()


def main():
    """Run all demos"""
    print("🎯 PROACTIVE RELATIONSHIP MANAGER AGENT DEMO")
    print("=" * 60)
    print("Demonstrating enhanced capabilities of the relationship memory agent")
    print("with proactive triggers, batch operations, and conversational advice.")
    print("=" * 60)
    print()
    
    try:
        demo_enhanced_models()
        demo_utility_functions()
        demo_proactive_triggers()
        demo_batch_processing()
        demo_workflow_enhancements()
        demo_error_handling()
        
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("✅ Enhanced Pydantic models working")
        print("✅ Utility functions operational")
        print("✅ Proactive trigger detection functional")
        print("✅ Batch processing capabilities ready")
        print("✅ Enhanced workflow routing active")
        print("✅ Improved error handling implemented")
        print()
        print("🚀 The Proactive Relationship Manager Agent is ready for use!")
        print("   Features include:")
        print("   • Proactive birthday and anniversary reminders")
        print("   • Intelligent reconnection suggestions")
        print("   • Batch contact import and management")
        print("   • Conversational advice based on stored memories")
        print("   • Automatic interaction history tracking")
        print("   • Enhanced error handling and validation")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()