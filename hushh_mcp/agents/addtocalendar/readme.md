# 🤖 Self-Contained Calendar Agent

![Agent Banner](https://googleusercontent.com/file_content/0)

This directory contains a **Self-Contained Calendar Agent**, a privacy-first AI agent built on the HushhMCP protocol. Its primary function is to securely access a user's emails, identify potential calendar events using AI, and automatically add them to their Google Calendar, all while strictly enforcing user consent.

This agent is designed to be fully encapsulated, meaning all its dependencies, credentials, and runners are located within its own directory for maximum portability and ease of use.

---

## ✨ Core Features

* **🔒 Consent-Driven**: No action is taken without a valid, signed `HushhConsentToken`. The agent validates permissions for both reading emails and writing to the calendar.
* **🧠 AI-Powered Event Extraction**: Uses an AI model (GPT-4o) to intelligently parse email content and extract structured event details like summaries, start times, and end times.
* **🔌 Seamless Google Integration**: Authenticates with Google's Gmail and Calendar APIs using OAuth2, storing refresh tokens locally for continued use.
* **📦 Fully Encapsulated**: All necessary files, including `credentials.json`, `.env`, and the runner script, are located within the agent's directory.

---

## 🔐 Consent Architecture

The agent operates on the principle of **"never trust, always verify."** Before performing any sensitive action, it uses the HushhMCP `validate_token` function to check for a valid consent token with the appropriate scope.

1.  **Email Access**: The agent first checks for a token with the `ConsentScope.VAULT_READ_EMAIL` scope. If valid, it proceeds to read unread emails.
2.  **Calendar Creation**: Before creating any calendar events, it performs a second check on the same token for the `ConsentScope.VAULT_WRITE_CALENDAR` scope.

This two-step validation ensures that the agent's actions are precisely aligned with the permissions granted by the user.

---

## 🗂️ File Structure

The agent is organized to be self-contained and easy to navigate:

```

hushh\_mcp/agents/addtocalendar/
├── .env               \# Agent-specific secrets (OpenAI, Hushh keys)
├── **init**.py        \# Makes this a Python package
├── credentials.json   \# Your Google API credentials
├── index.py           \# The core agent logic
├── manifest.py        \# Agent's identity and required scopes
└── run\_agent.py       \# Script to execute the agent

````

---

## 🚀 Setup and Usage

Follow these steps to get your agent running.

### 1. Install Dependencies

Ensure you have all the necessary Python packages installed.

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib beautifulsoup4 openai python-dotenv
````

### 2\. Get Google Credentials

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project.
3.  Enable the **Gmail API** and **Google Calendar API**.
4.  Create an **OAuth 2.0 Client ID** for a **Desktop app**.
5.  Download the credentials JSON file and rename it to `credentials.json`.
6.  Place the `credentials.json` file inside this directory (`hushh_mcp/agents/addtocalendar/`).

### 3\. Configure Environment Variables

Create a `.env` file within this directory by copying the contents of `.env.example` from the root of the project. Fill in the required values:

```env
# hushh_mcp/agents/addtocalendar/.env

# Your OpenAI API Key
OPENAI_API_KEY="sk-..."

# HushhMCP signing and encryption keys (generate using python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY="your_64_character_hex_key"
VAULT_ENCRYPTION_KEY="your_64_character_hex_key"
```

### 4\. Run the Agent

Navigate to the agent's directory in your terminal and execute the runner script.

```bash
cd hushh_mcp/agents/addtocalendar/
python run_agent.py
```

The first time you run the agent, you will be prompted to go through the Google OAuth consent flow in your browser. After granting permission, a `token_...json` file will be created in this directory, allowing the agent to run without prompting you again.

```
```