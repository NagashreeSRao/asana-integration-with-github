from flask import Flask, request, jsonify
import hmac
import hashlib
import json
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

GITHUB_SECRET = b'your_github_webhook_secret'
ASANA_PAT = '2/1210539226965314/1210540834382719:ce69cf12351fd57531886c74ba16dcd2'
ASANA_PROJECT_ID = '1210539703260435'

def is_valid_signature(payload_body, signature):
    mac = hmac.new(GITHUB_SECRET, msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = 'sha256=' + mac.hexdigest()
    return hmac.compare_digest(expected_signature, signature)

@app.route('/webhook', methods=['POST'])
def github_webhook():
    signature = request.headers.get('X-Hub-Signature-256')
    if not is_valid_signature(request.data, signature):
        return "Invalid signature", 400

    payload = request.json
    if payload['action'] == 'opened':
        issue = payload['issue']
        title = issue['title']
        body = issue.get('body', '')
        url = issue['html_url']
        creator = issue['user']['login']

        description = body + "\n\nGitHub URL: " + url

        create_asana_task(name=title, description=description, assignee=None)

    return jsonify({'status': 'success'}), 200

def create_asana_task(name, description, assignee=None, due_date=None):
    url = 'https://app.asana.com/api/1.0/tasks'

