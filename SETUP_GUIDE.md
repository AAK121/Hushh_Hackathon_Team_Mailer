# 🔧 **SETUP GUIDE: HushMCP Privacy-First AI System**

## **🎯 Current Status Analysis**

✅ **What's Already Done:**
- ✅ Frontend deployed to Vercel
- ✅ Backend partially deployed 
- ✅ Supabase authentication configured
- ✅ HushMCP architecture implemented
- ✅ User-specific vault system created

❌ **What You Need To Fix:**

### **1. Missing Critical Environment Variables**

Your backend `.env` is missing the **HushMCP security keys** that are absolutely required:

```bash
# Add these to backend/.env file:
SECRET_KEY=generate_64_character_hex_string
VAULT_ENCRYPTION_KEY=generate_64_character_hex_string  
VAULT_MASTER_KEY=generate_64_character_hex_string
```

### **2. Generate the Required Keys**

Run these commands to generate proper security keys:

```bash
# Generate SECRET_KEY (64 chars)
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Generate VAULT_ENCRYPTION_KEY (64 chars) 
python -c "import secrets; print('VAULT_ENCRYPTION_KEY=' + secrets.token_hex(32))"

# Generate VAULT_MASTER_KEY (64 chars)
python -c "import secrets; print('VAULT_MASTER_KEY=' + secrets.token_hex(32))"
```

### **3. Set Vercel Environment Variables**

For your deployed backend, you need to set these in Vercel Dashboard:

1. Go to: https://vercel.com/dashboard
2. Select your backend project
3. Go to Settings > Environment Variables
4. Add each key-value pair

**Required Variables for Vercel Backend:**
```
SECRET_KEY=your_generated_64_char_key
VAULT_ENCRYPTION_KEY=your_generated_64_char_key
VAULT_MASTER_KEY=your_generated_64_char_key
GEMINI_API_KEY=AIzaSyCyTIMomAZ-EtebfSToII2gwLo8pInVXwY
MAILJET_API_KEY=cca56ed08f5272f813370d7fc5a34a24
MAILJET_API_SECRET=60fb43675233e2ac775f1c6cb8fe455c
PINECONE_API_KEY=pcsk_6vCMdb_3WH5y9VhN4oj9zcCyVTynYMMEM6p9peJad3dE3kauD3dD1Q6Mo5F3pWDtV5YXTT
PINECONE_ENVIRONMENT=3fe7cae0-f092-408c-98e1-c48f9303e809
```

---

## **🏗️ Architecture Explanation**

### **🔐 HushMCP Security Flow**

```
User Login (Supabase) → Get User ID → Generate Consent Tokens → AI Agent Access
                                   ↓
                            User-Specific Vault Created
                                   ↓
                            Encrypted Data Storage
```

### **🎯 How Consent Tokens Work**

1. **User authenticates** via Supabase
2. **Frontend requests consent tokens** for specific actions (email, calendar, etc.)
3. **Backend validates user** and issues **cryptographically signed tokens**
4. **AI agents check tokens** before every action
5. **No hardcoded access** - everything requires explicit permission

### **🗄️ User Vault System**

Each user gets:
- **Unique encryption key** (AES-256-GCM)
- **Encrypted data storage** for contacts, memories, interactions
- **Isolated vault** - no cross-user data access
- **Automatic key rotation** for security

---

## **📋 Step-by-Step Setup Instructions**

### **Step 1: Generate Security Keys**
```bash
# Run these commands and copy the output
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('VAULT_ENCRYPTION_KEY=' + secrets.token_hex(32))"  
python -c "import secrets; print('VAULT_MASTER_KEY=' + secrets.token_hex(32))"
```

### **Step 2: Update Backend .env**
Add the generated keys to `backend/.env`:
```bash
SECRET_KEY=your_generated_key_here
VAULT_ENCRYPTION_KEY=your_generated_key_here
VAULT_MASTER_KEY=your_generated_key_here
```

### **Step 3: Set Vercel Environment Variables**
1. Go to Vercel Dashboard
2. Select your backend project  
3. Settings → Environment Variables
4. Add all the keys from Step 1

### **Step 4: Redeploy Backend**
```bash
cd backend
vercel --prod
```

### **Step 5: Test the System**
1. Open your frontend URL
2. Sign up/login with Supabase
3. Try using any AI agent
4. Check that consent tokens are properly generated

---

## **🚨 Security Features Implemented**

✅ **No Demo Mode** - Requires proper authentication
✅ **Consent Tokens** - Every AI action needs permission  
✅ **User-Specific Encryption** - Each user has unique keys
✅ **No Hardcoded Values** - Everything configurable
✅ **Automatic Token Refresh** - Prevents authentication failures
✅ **Vault Isolation** - Users can't access each other's data

---

## **🔧 Troubleshooting**

**If backend deployment fails:**
- Check all environment variables are set in Vercel
- Ensure keys are exactly 64 characters (hex)
- Check Vercel function logs for specific errors

**If authentication fails:**
- Verify Supabase URL and keys in frontend .env
- Check user is properly logged in before using agents

**If agents don't work:**
- Verify consent tokens are being generated
- Check backend logs for token validation errors
- Ensure API keys (Gemini, etc.) are valid

---

## **🎉 What Happens After Setup**

Once properly configured, your system will:

1. **Authenticate users** securely via Supabase
2. **Generate unique encryption keys** for each user
3. **Issue consent tokens** for AI agent access
4. **Execute AI operations** with proper permissions
5. **Store data securely** in user-specific encrypted vaults
6. **Automatically refresh tokens** to prevent failures

This creates a **production-ready, privacy-first AI system** that follows enterprise security standards!
