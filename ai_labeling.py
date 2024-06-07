import requests
from requests.auth import HTTPBasicAuth
from groq import Groq
import re
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Load environment variables from .env file
JIRA_URL = os.getenv("JIRA_API_URL")
JIRA_EMAIL = os.getenv("JIRA_API_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize the Groq client with an API key
client = Groq(api_key=GROQ_API_KEY)

def ai_labeling(combined_info):
    """Generate labels using AI."""
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI specialized in labeling JIRA tickets. "
                    "Your task is to analyze the semantics and key issues of each ticket to propose relevant and specific labels. "
                    "Respond only with words separated by commas. Avoid using 'obvious' words (project name, issuetype, bug, priority, task...). "
                    "Focus on context, functionality, and specific components involved. Consider the project's domain and common themes. "
                    "Provide labels that capture the essence of the ticket's subject, actions, and objectives."
                )
            },
            {
                "role": "user",
                "content": combined_info,
            }
        ],
        model="llama3-8b-8192",
        temperature=0.3,
        max_tokens=256,
        top_p=1,
        stop=None,
        stream=False,
    )

    labels = response.choices[0].message.content
    print(f"Generated labels: {labels}")
    return labels

def add_label(label_string, issue_key):
    """Add labels to a JIRA issue, replacing '-' with '_' and spaces between labels with '_'."""
    url = f"{JIRA_URL}/rest/api/2/issue/{issue_key}"
    
    # Replace '-' with '_' and handle spaces between labels
    label_string = re.sub(r'(?<=\w)-|-(?=\w)', '_', label_string)
    labels = [re.sub(r'\s+', '_', label.strip()) for label in label_string.split(',')]
    
    payload = {
        "update": {
            "labels": [{"add": label} for label in labels]
        }
    }
    
    headers = {"Content-Type": "application/json"}
        
    response = requests.put(
        url, data=json.dumps(payload), headers=headers, 
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    )
    
    if response.status_code == 204:
        print(f"Labels successfully added to issue {issue_key}.")
    else:
        print(f"Error {response.status_code}: {response.text}")

def main():
    combined_info = (
        "Summary: Fix login issues\n"
        "Description: Users are unable to log in to the system. The login page is unresponsive and throws an error message. "
        "Project: MyProject, Issue Type: Bug"
    )
    
    labels = ai_labeling(combined_info)
    add_label(labels, "MYPROJECT-123")

if __name__ == '__main__':
    main()