import json
from flask import Flask, request
from ai_labeling import ai_labeling
from ai_labeling import add_label
from dotenv import load_dotenv
import os

load_dotenv()

# Load environment variables from .env file
JIRA_URL = os.getenv("JIRA_API_URL")
JIRA_EMAIL = os.getenv("JIRA_API_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# Initialize the Flask application
app = Flask(__name__)

@app.route('/webhook-handler', methods=['POST'])
def webhook_handler():
    """Main route for handling JIRA webhooks."""
    data = request.json
    print(json.dumps(data, indent=4))
    
    issue_event_type = data.get('webhookEvent')
    if issue_event_type == 'jira:issue_created':
        handle_issue_created(data)
    elif issue_event_type == 'jira:issue_updated':
        handle_issue_updated(data)

    return 'OK', 200

@app.route('/debug-info', methods=['GET'])
def debug_info():
    """Debug route to display hosting information."""
    return f'This server is running at: {request.host_url}', 200

def handle_issue_created(data):
    """Handle JIRA issue creation events."""
    issue_key = data['issue']['key']
    fields = data['issue']['fields']
    summary = fields.get('summary', '')
    description = fields.get('description', '')
    project_name = fields['project']['name']
    issue_type = fields['issuetype']['name']
    
    combined_info = (
        f"Summary: {summary}\n"
        f"Description: {description}\n"
        f"Project: {project_name}, Issue Type: {issue_type}"
    )
    
    labels = ai_labeling(combined_info)
    add_label(labels, issue_key)

    print(f'Issue created: {issue_key}')
    print(f'Combined Info: {combined_info}')

def handle_issue_updated(data):
    """Handle JIRA issue update events."""
    issue_key = data['issue']['key']
    print(f'Issue updated: {issue_key}')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
