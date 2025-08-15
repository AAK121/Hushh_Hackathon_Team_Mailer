# Debug script to test vault persistence
import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from hushh_mcp.agents.relationship_memory.utils.vault_manager import VaultManager

def test_vault_persistence():
    print("🧪 Testing Vault Persistence...")
    
    user_id = "demo_user_quick_test"
    vault_key = "1b0166345f10bd91dbd7da0f6f92384229a9c6d0858ba08b5a1e45a6af388134"  # 32-byte hex key
    
    # Test 1: Add a contact
    print("\n1️⃣ Adding contact...")
    vault1 = VaultManager(user_id=user_id, vault_key=vault_key)
    contact_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '1234567890'
    }
    contact_id = vault1.store_contact(contact_data)
    print(f"✅ Added contact with ID: {contact_id}")
    
    # Test 2: Create new vault instance and check if contact exists
    print("\n2️⃣ Creating new vault instance...")
    vault2 = VaultManager(user_id=user_id, vault_key=vault_key)
    
    # Debug: Check database directly
    import sqlite3
    with sqlite3.connect(vault2.db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM vault_records WHERE record_type='contact'")
        record_count = cursor.fetchone()[0]
        print(f"📊 Contact records in database: {record_count}")
        
        if record_count > 0:
            cursor = conn.execute("SELECT record_type, record_id, scope FROM vault_records WHERE record_type='contact'")
            records = cursor.fetchall()
            print("📋 Contact records in database:")
            for record in records:
                print(f"   - Type: {record[0]}, ID: {record[1]}, Scope: {record[2]}")
    
    # Test manual decryption
    print("\n🔍 Testing manual decryption...")
    try:
        from hushh_mcp.constants import ConsentScope
        
        # Try with WRITE scope (same as storage)
        print("   Trying with VAULT_WRITE_CONTACTS scope...")
        test_records_write = vault2._retrieve_all_records('contact', ConsentScope.VAULT_WRITE_CONTACTS)
        print(f"   ✅ With WRITE scope: {len(test_records_write)} contacts")
        
        # Try with READ scope 
        print("   Trying with VAULT_READ_CONTACTS scope...")
        test_records_read = vault2._retrieve_all_records('contact', ConsentScope.VAULT_READ_CONTACTS)
        print(f"   ✅ With READ scope: {len(test_records_read)} contacts")
        
        if test_records_write:
            for record in test_records_write:
                print(f"      - {record}")
    except Exception as e:
        print(f"❌ Manual decryption failed: {e}")
        import traceback
        traceback.print_exc()
    
    contacts = vault2.get_all_contacts()
    print(f"📋 Found {len(contacts)} contacts via get_all_contacts()")
    
    if contacts:
        print("✅ Contacts persist across vault instances!")
        for contact in contacts:
            print(f"   - {contact}")
    else:
        print("❌ Contacts do NOT persist - storage issue detected")
    
    # Test 3: Check database file
    db_path = vault1.db_path
    print(f"\n3️⃣ Database path: {db_path}")
    print(f"   Database exists: {os.path.exists(db_path)}")
    if os.path.exists(db_path):
        print(f"   Database size: {os.path.getsize(db_path)} bytes")

if __name__ == "__main__":
    test_vault_persistence()
