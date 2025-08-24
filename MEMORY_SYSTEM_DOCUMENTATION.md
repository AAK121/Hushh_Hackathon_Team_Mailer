# MailerPanda Email Memory System

## 🧠 Overview

The MailerPanda agent now includes an advanced **Email Memory System** that learns and remembers how each user prefers their emails to be written. This creates a personalized, evolving email writing assistant that gets better over time.

## ✨ Key Features

### 📝 What It Remembers
- **Writing Style**: Professional, casual, formal, conversational
- **Tone**: Friendly, authoritative, warm, business-like
- **Email Structure**: Preferred greeting, body, and closing styles
- **Subject Line Patterns**: Length and style preferences
- **Key Phrases**: Words and phrases the user likes
- **Avoid List**: Phrases and words the user dislikes
- **User Feedback**: All feedback to learn from mistakes

### 🔄 How It Learns
1. **Every Email Draft** is saved to encrypted memory
2. **User Feedback** is analyzed and stored
3. **Approval/Rejection** patterns are tracked
4. **Style Analysis** identifies user preferences
5. **Future Emails** incorporate learned preferences

### 🔐 Security & Privacy
- All memory data is **encrypted** using AES-256-GCM
- Data is stored in **user-specific vault directories**
- Requires **proper consent tokens** for access
- Memory is **completely isolated** per user

## 🚀 How It Works

### Memory Storage Structure
```
vault/{user_id}/email_preferences.enc
├── 🎨 Writing Style Preferences
├── 📧 Recent Email Examples (last 10)
├── 💬 User Feedback History (last 20)
├── 📈 Campaign Performance Data
└── 🎯 Personalization Settings
```

### Memory Integration in Email Generation

When generating emails, the agent:

1. **Loads user memory** from encrypted vault
2. **Analyzes past preferences** and feedback
3. **Creates style guide** for AI generation
4. **Includes memory context** in AI prompt
5. **Generates email** matching learned style
6. **Saves new email** to memory for future learning

### Example Memory Context Sent to AI

```
📚 USER'S EMAIL WRITING PREFERENCES (Use this to match their style):
Style Guide: Writing style: professional | Tone: friendly | Formality: business_casual

🎯 Recent Email Examples (match this style):
Example 1:
Subject: Thank You for Your Purchase
Content: Dear Customer, Thank you for your recent purchase...

💬 Recent User Feedback (avoid these issues):
- Make it more professional and formal
- Use shorter sentences
```

## 🎯 Benefits

### For Users
- ✨ **Emails get better over time** - matches your preferred style
- ⚡ **Faster email generation** - no need to repeat preferences
- 🎯 **Consistent brand voice** across all campaigns
- 📈 **Improved satisfaction** through personalized learning

### For Organizations
- 🏢 **Brand consistency** across team members
- 📊 **Learning from feedback** patterns
- 🔄 **Continuous improvement** of email quality
- 💾 **Preserved knowledge** even with staff changes

## 🛠️ Technical Implementation

### Memory Methods Added

```python
def _save_user_email_memory(self, user_id: str, email_data: Dict, consent_tokens: Dict[str, str]) -> str:
    """Saves user's email preferences to encrypted vault"""

def _load_user_email_memory(self, user_id: str, consent_tokens: Dict[str, str]) -> Optional[Dict]:
    """Loads user's email preferences from encrypted vault"""

def _analyze_user_style_from_memory(self, memory_data: Dict) -> str:
    """Analyzes user's style patterns to create AI guidance"""
```

### Integration Points

1. **`_draft_content`** - Loads memory and includes in AI prompt
2. **`_get_feedback`** - Saves user feedback to memory
3. **Email approval/rejection** - Records user satisfaction
4. **Campaign completion** - Updates memory with results

## 📊 Memory Data Structure

```json
{
  "user_id": "user_123",
  "agent_id": "agent_mailerpanda",
  "data_type": "email_writing_preferences",
  "created_at": "2025-08-24T07:58:50Z",
  "updated_at": "2025-08-24T08:15:22Z",
  "preferences": {
    "writing_style": "professional",
    "tone": "friendly", 
    "formality_level": "business_casual",
    "key_phrases": ["Thank you", "We appreciate"],
    "avoid_phrases": ["URGENT", "ACT NOW"]
  },
  "email_examples": [
    {
      "subject": "Thank You for Your Purchase",
      "content": "Dear Customer...",
      "user_satisfaction": "approved",
      "timestamp": "2025-08-24T08:00:00Z"
    }
  ],
  "feedback_history": [
    {
      "feedback": "Make it more formal",
      "timestamp": "2025-08-24T08:10:00Z",
      "campaign_id": "campaign_001"
    }
  ]
}
```

## 🧪 Testing

### Memory Functionality Tests
- ✅ Save/load encrypted memory data
- ✅ Style analysis from user patterns
- ✅ Feedback integration and learning
- ✅ Memory evolution over time
- ✅ AI context generation from memory

### Test Files
- `test_memory_simple.py` - Core memory functionality
- `test_memory_functionality.py` - End-to-end API testing
- `test_memory_direct.py` - Direct method testing

## 🎉 Result

The MailerPanda agent now provides:

1. **Personalized Email Generation** - Each user gets emails in their preferred style
2. **Continuous Learning** - Agent improves with every interaction
3. **Brand Consistency** - Maintains user's preferred voice and tone
4. **Feedback Integration** - Learns from corrections and suggestions
5. **Secure Memory** - All data encrypted and user-isolated

Users will notice that:
- **First emails** are generic but professional
- **After feedback**, the agent learns their preferences
- **Future emails** automatically match their style
- **No need to repeat** style preferences
- **Consistent quality** across all campaigns

This creates a truly intelligent, personalized email assistant that evolves with each user's needs and preferences.
