import google.generativeai as genai
import os
from typing import Dict, Any
from dotenv import load_dotenv

class MemoryLLM:
    def __init__(self):
        # Load API key from environment
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCrzoxJMoFFxF0QhDyJUam5T7Kqew3fyvU')
        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel('gemini-2.5-flash')
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process natural language input and determine the action to take"""
        prompt = f"""
You are a relationship memory assistant. Analyze the user's input and extract ANY relevant information.

User Input: "{user_input}"

Extract information in this format ONLY:
ACTION: [add_contact|add_memory|set_reminder|get_contacts|get_memories|get_reminders]
PARAMS: key1:value1, key2:value2, etc.

Examples:

1. Input: "Add John from Microsoft"
ACTION: add_contact
PARAMS: name:John, company:Microsoft

2. Input: "I met Sarah at Starbucks today"
ACTION: add_memory
PARAMS: contact_name:Sarah, summary:Met at Starbucks today

3. Input: "My friend Tom's email is tom@gmail.com"
ACTION: add_contact
PARAMS: name:Tom, email:tom@gmail.com, relationship:friend

4. Input: "Show my contacts"
ACTION: get_contacts
PARAMS:

Be flexible and extract ANY relevant information from the input, even if incomplete.
Don't require specific keywords or formats. Figure out the intent and relevant data from natural language.
"""
        response = self.llm.generate_content(prompt)
        lines = response.text.strip().split('\n')
        result = {}
        
        for line in lines:
            if line.startswith('ACTION:'):
                result['action'] = line.replace('ACTION:', '').strip()
            elif line.startswith('PARAMS:'):
                # Convert the params string to a dictionary
                params_str = line.replace('PARAMS:', '').strip()
                params = {}
                if params_str:  # Only process if there are params
                    for param in params_str.split(','):
                        if ':' in param:
                            key, value = param.split(':', 1)  # Split on first colon only
                            params[key.strip()] = value.strip()
                result['params'] = params
        
        return result
    
    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """Parse user intent from natural language input"""
        result = self.process_input(user_input)
        action = result.get('action', 'unknown')
        params = result.get('params', {})
        
        # Map actions to consistent format
        action_mapping = {
            'add_contact': 'add_contact',
            'get_contacts': 'show_contacts',
            'add_memory': 'add_memory',
            'get_memories': 'show_memories',
            'set_reminder': 'add_reminder',
            'get_reminders': 'show_reminders'
        }
        
        return {
            'action': action_mapping.get(action, action),
            'search_query': params.get('search_query', ''),
            **params
        }
    
    def extract_contact_info(self, user_input: str) -> Dict[str, Any]:
        """Extract contact information from user input"""
        result = self.process_input(user_input)
        params = result.get('params', {})
        
        return {
            'name': params.get('name', ''),
            'email': params.get('email', ''),
            'phone': params.get('phone', ''),
            'company': params.get('company', ''),
            'location': params.get('location', ''),
            'notes': params.get('notes', '')
        }
    
    def extract_memory_info(self, user_input: str) -> Dict[str, Any]:
        """Extract memory information from user input"""
        result = self.process_input(user_input)
        params = result.get('params', {})
        
        return {
            'contact_name': params.get('contact_name', ''),
            'summary': params.get('summary', user_input),
            'location': params.get('location', ''),
            'date': params.get('date', ''),
            'tags': params.get('tags', '').split(',') if params.get('tags') else []
        }
    
    def extract_reminder_info(self, user_input: str) -> Dict[str, Any]:
        """Extract reminder information from user input"""
        result = self.process_input(user_input)
        params = result.get('params', {})
        
        return {
            'contact_name': params.get('contact_name', ''),
            'title': params.get('title', user_input),
            'date': params.get('date', ''),
            'priority': params.get('priority', 'medium')
        }