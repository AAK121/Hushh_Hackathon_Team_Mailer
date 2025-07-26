from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sys
import json
from typing import Dict, Any
import pandas as pd
import base64
from dotenv import load_dotenv
from mailjet_rest import Client

# Add the parent directories to the path to import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

app = Flask(__name__, static_folder=".", template_folder=".")
CORS(app)


class WebMailerAgent:
    def __init__(self):
        self.conversations = {}
        self.current_email_template = ""

    def generate_email_template(self, user_input: str) -> str:
        """Generate email template based on user input"""
        # Mock AI response - in real implementation, this would call your LLM
        templates = {
            "welcome": """Dear {name},

Welcome to our team! We're excited to have you join us as a new intern.

Your first day will be on {start_date}, and you'll be working with the {department} team. We've prepared an orientation program to help you get started and familiarize yourself with our company culture and processes.

Please bring the following items on your first day:
- Photo ID
- Signed offer letter
- Any required documentation

If you have any questions before your start date, please don't hesitate to reach out to me or our HR team.

Looking forward to working with you!

Best regards,
{sender_name}
{title}
{company_name}""",
            "follow-up": """Dear {name},

Thank you for taking the time to interview for the {position} role at {company_name}. I enjoyed our conversation and was impressed by your experience and enthusiasm.

I wanted to follow up on our discussion and reiterate my strong interest in this position. After learning more about the role and your team's goals, I'm even more excited about the opportunity to contribute to {company_name}.

If you need any additional information from me, please don't hesitate to ask. I look forward to hearing about the next steps in the process.

Thank you again for your time and consideration.

Best regards,
{your_name}""",
            "meeting": """Dear {name},

I hope this email finds you well. I would like to schedule a meeting to discuss {meeting_topic}.

Would you be available for a {duration} meeting on {proposed_date} at {proposed_time}? We can meet at {location} or via video conference, whichever works better for you.

Agenda items will include:
- {agenda_item_1}
- {agenda_item_2}
- {agenda_item_3}

Please let me know if this time works for you, or suggest an alternative that would be more convenient.

Best regards,
{your_name}""",
            "thank-you": """Dear {name},

I wanted to take a moment to express my sincere gratitude for your continued partnership with {company_name}.

Your trust in our services and products means the world to us, and we're committed to delivering the highest level of service and value to support your success.

We look forward to continuing our partnership and finding new ways to serve you better.

Thank you once again for your business and trust.

Warm regards,
{your_name}
{title}
{company_name}""",
        }

        # Simple keyword matching to determine template
        input_lower = user_input.lower()

        if any(word in input_lower for word in ["welcome", "intern", "new", "joining"]):
            template = templates["welcome"]
        elif any(word in input_lower for word in ["follow", "interview"]):
            template = templates["follow-up"]
        elif any(word in input_lower for word in ["meeting", "schedule"]):
            template = templates["meeting"]
        elif any(word in input_lower for word in ["thank", "gratitude"]):
            template = templates["thank-you"]
        else:
            template = templates["welcome"]  # default

        return template

    def update_template_with_feedback(
        self, current_template: str, feedback: str
    ) -> str:
        """Update template based on user feedback"""
        # Mock feedback processing - in real implementation, this would use LLM
        if "formal" in feedback.lower():
            return current_template.replace("Hi", "Dear").replace("Thanks", "Thank you")
        elif "casual" in feedback.lower():
            return current_template.replace("Dear", "Hi").replace("Thank you", "Thanks")
        elif "shorter" in feedback.lower():
            lines = current_template.split("\n")
            return "\n".join(lines[: len(lines) // 2])
        else:
            return current_template + f"\n\n[Updated based on feedback: {feedback}]"


web_agent = WebMailerAgent()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(".", filename)


@app.route("/api/generate-email", methods=["POST"])
def generate_email():
    try:
        data = request.get_json()
        user_input = data.get("user_input", "")
        feedback = data.get("feedback", "")
        current_template = data.get("current_template", "")

        if feedback and current_template:
            # Update existing template based on feedback
            email_template = web_agent.update_template_with_feedback(
                current_template, feedback
            )
        else:
            # Generate new template
            email_template = web_agent.generate_email_template(user_input)

        web_agent.current_email_template = email_template

        return jsonify(
            {
                "success": True,
                "email_template": email_template,
                "message": "Email template generated successfully",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/send-emails", methods=["POST"])
def send_emails():
    try:
        data = request.get_json()
        email_template = data.get("email_template", web_agent.current_email_template)
        recipients = data.get("recipients", [])
        subject = data.get("subject", "Important Message")

        if not email_template:
            return (
                jsonify({"success": False, "error": "No email template provided"}),
                400,
            )

        if not recipients:
            return jsonify({"success": False, "error": "No recipients provided"}), 400

        # Mailjet configuration
        api_key = os.getenv("MJ_APIKEY_PUBLIC")
        secret_key = os.getenv("MJ_APIKEY_PRIVATE")

        if not api_key or not secret_key:
            return (
                jsonify(
                    {"success": False, "error": "Mailjet credentials not configured"}
                ),
                500,
            )

        mailjet = Client(auth=(api_key, secret_key), version="v3.1")
        results = []

        for recipient in recipients:
            try:
                # Format the email content with recipient data
                formatted_content = email_template.format(**recipient)

                message_data = {
                    "From": {"Email": "dragnoid121@gmail.com", "Name": "Hushh Mailer"},
                    "To": [
                        {
                            "Email": recipient.get("email"),
                            "Name": recipient.get("name", "Recipient"),
                        }
                    ],
                    "Subject": subject,
                    "TextPart": formatted_content,
                    "HTMLPart": f"<pre>{formatted_content}</pre>",
                }

                data_payload = {"Messages": [message_data]}
                result = mailjet.send.create(data=data_payload)

                results.append(
                    {
                        "email": recipient.get("email"),
                        "status": result.status_code,
                        "success": result.status_code == 200,
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "email": recipient.get("email"),
                        "status": "error",
                        "success": False,
                        "error": str(e),
                    }
                )

        return jsonify(
            {
                "success": True,
                "results": results,
                "message": f'Email sending completed. {len([r for r in results if r["success"]])} out of {len(results)} emails sent successfully.',
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/process-excel", methods=["POST"])
def process_excel():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        if not file.filename.endswith((".xlsx", ".xls")):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "File must be an Excel file (.xlsx or .xls)",
                    }
                ),
                400,
            )

        # Read Excel file
        df = pd.read_excel(file)

        # Convert to list of dictionaries
        recipients = df.to_dict("records")

        # Validate required columns
        required_columns = ["email"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f'Missing required columns: {", ".join(missing_columns)}',
                    }
                ),
                400,
            )

        return jsonify(
            {
                "success": True,
                "recipients": recipients,
                "count": len(recipients),
                "columns": list(df.columns),
                "message": f"Successfully processed {len(recipients)} recipients",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify(
        {"status": "healthy", "message": "Hushh Mailer Agent API is running"}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
