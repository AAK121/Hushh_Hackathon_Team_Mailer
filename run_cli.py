"""
Relationship Memory Agent - Interactive CLI
Run this script to interact with the agent
"""
import os
import sys
from datetime import datetime, timedelta
import cmd
from typing import Optional
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Import our agent
from test_agent import RelationshipMemoryAgent

# Load environment variables
load_dotenv()

class RelationshipMemoryShell(cmd.Cmd):
    intro = '''
    ╔════════════════════════════════════════════╗
    ║       Relationship Memory Agent CLI         ║
    ╚════════════════════════════════════════════╝
    
    Type 'help' or '?' to list commands.
    Type 'quit' to exit.
    '''
    prompt = '(agent) '

    def __init__(self):
        super().__init__()
        self.agent = RelationshipMemoryAgent()

    def do_add_contact(self, arg):
        """Add a new contact. Usage: add_contact"""
        print("\nAdding new contact:")
        name = input("Name: ").strip()
        email = input("Email (optional - press Enter to skip): ").strip() or None
        phone = input("Phone (optional - press Enter to skip): ").strip() or None
        relationship = input("Relationship (optional - press Enter to skip): ").strip() or None
        
        birthday_str = input("Birthday (YYYY-MM-DD, optional - press Enter to skip): ").strip()
        birthday = None
        if birthday_str:
            try:
                birthday = datetime.strptime(birthday_str, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format. Birthday not set.")

        notes = input("Notes (optional - press Enter to skip): ").strip() or None

        contact = self.agent.create_contact(
            name=name,
            email=email,
            phone=phone,
            relationship=relationship,
            birthday=birthday,
            notes=notes
        )
        print(f"\n✅ Contact added successfully! ID: {contact['id']}")

    def do_add_memory(self, arg):
        """Add a new memory for a contact. Usage: add_memory"""
        try:
            contact_id = int(input("\nContact ID: ").strip())
            summary = input("Memory summary: ").strip()
            detailed_notes = input("Detailed notes (optional - press Enter to skip): ").strip() or None
            sentiment = input("Sentiment (positive/negative/neutral - press Enter to skip): ").strip() or None
            
            tags_input = input("Tags (comma-separated key:value pairs, e.g., 'topic:work,location:office'): ").strip()
            tags = {}
            if tags_input:
                try:
                    for pair in tags_input.split(','):
                        key, value = pair.split(':')
                        tags[key.strip()] = value.strip()
                except ValueError:
                    print("Invalid tags format. Tags will be empty.")
                    tags = {}

            memory = self.agent.add_memory(
                contact_id=contact_id,
                summary=summary,
                detailed_notes=detailed_notes,
                sentiment=sentiment,
                tags=tags
            )
            print(f"\n✅ Memory added successfully! ID: {memory['id']}")
        except ValueError as e:
            print(f"Error: {str(e)}")

    def do_set_reminder(self, arg):
        """Set a new reminder for a contact. Usage: set_reminder"""
        try:
            contact_id = int(input("\nContact ID: ").strip())
            title = input("Reminder title: ").strip()
            description = input("Description (optional - press Enter to skip): ").strip() or None
            
            days_ahead = input("Days from now (default 7): ").strip()
            days_ahead = int(days_ahead) if days_ahead else 7
            scheduled_at = datetime.now() + timedelta(days=days_ahead)

            reminder_type = input("Type (follow-up/birthday/check-in/other - default: follow-up): ").strip() or "follow-up"
            recurrence = input("Recurrence (daily/weekly/monthly/yearly/none - default: none): ").strip() or None

            reminder = self.agent.set_reminder(
                contact_id=contact_id,
                title=title,
                scheduled_at=scheduled_at,
                reminder_type=reminder_type,
                description=description,
                recurrence=recurrence
            )
            print(f"\n✅ Reminder set successfully! Scheduled for: {reminder['scheduled_at'].strftime('%Y-%m-%d')}")
        except ValueError as e:
            print(f"Error: {str(e)}")

    def do_list_contacts(self, arg):
        """List all contacts. Usage: list_contacts"""
        print("\nContacts:")
        # We'll need to add this method to our agent
        contacts = self.agent.get_all_contacts()
        for contact in contacts:
            print(f"\nID: {contact['id']}")
            print(f"Name: {contact['name']}")
            print(f"Email: {contact['email'] or 'N/A'}")
            print(f"Relationship: {contact['relationship'] or 'N/A'}")
            print("-" * 40)

    def do_list_memories(self, arg):
        """List memories for a contact. Usage: list_memories <contact_id>"""
        try:
            contact_id = int(input("\nContact ID: ").strip())
            memories = self.agent.get_contact_memories(contact_id)
            if memories:
                print(f"\nMemories:")
                for memory in memories:
                    print(f"\nSummary: {memory['summary']}")
                    print(f"Sentiment: {memory['sentiment'] or 'N/A'}")
                    if memory['detailed_notes']:
                        print(f"Details: {memory['detailed_notes']}")
                    print("-" * 40)
            else:
                print("No memories found for this contact.")
        except ValueError as e:
            print(f"Error: {str(e)}")

    def do_upcoming_reminders(self, arg):
        """List upcoming reminders. Usage: upcoming_reminders [days]"""
        try:
            days = int(input("\nDays ahead to check (default 7): ").strip() or "7")
            reminders = self.agent.get_upcoming_reminders(days)
            if reminders:
                print(f"\nUpcoming reminders for the next {days} days:")
                for reminder in reminders:
                    print(f"\nTitle: {reminder['title']}")
                    print(f"For: {reminder['contact_name']}")
                    print(f"When: {reminder['scheduled_at'].strftime('%Y-%m-%d')}")
                    print("-" * 40)
            else:
                print(f"No upcoming reminders for the next {days} days.")
        except ValueError as e:
            print(f"Error: {str(e)}")

    def do_search_memories(self, arg):
        """Search memories by sentiment. Usage: search_memories <sentiment>"""
        sentiment = input("\nEnter sentiment to search (positive/negative/neutral): ").strip().lower()
        if sentiment not in ['positive', 'negative', 'neutral']:
            print("Invalid sentiment. Use positive, negative, or neutral.")
            return
        
        memories = self.agent.search_memories_by_sentiment(sentiment)
        if memories:
            print(f"\nMemories with {sentiment} sentiment:")
            for memory in memories:
                print(f"\nSummary: {memory['summary']}")
                print(f"Contact: {memory['contact_name']}")
                print("-" * 40)
        else:
            print(f"No {sentiment} memories found.")

    def do_quit(self, arg):
        """Exit the agent CLI"""
        print("\nGoodbye! 👋")
        return True

    def do_EOF(self, arg):
        """Exit on Ctrl-D (EOF)"""
        print("\nGoodbye! 👋")
        return True

if __name__ == '__main__':
    RelationshipMemoryShell().cmdloop()
