from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TEAMS_WEBHOOK_URL = 'https://outlook.office.com/webhook/YOUR_TEAMS_WEBHOOK_URL_HERE'

@app.route('/bitbucket-webhook', methods=['POST'])
def bitbucket_webhook():
    event_key = request.headers.get('X-Event-Key')
    data = request.get_json()

    # Only handle pull request created events
    if event_key != 'pullrequest:created':
        return jsonify({'message': f'Ignored event: {event_key}'}), 200

    try:
        pr = data['pullrequest']
        title = pr['title']
        author = pr['author']['display_name']
        source_branch = pr['source']['branch']['name']
        destination_branch = pr['destination']['branch']['name']
        pr_link = pr['links']['html']['href']

        teams_payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": f"New PR: {title}",
            "themeColor": "0078D7",
            "sections": [{
                "activityTitle": "**New Pull Request Created**",
                "activitySubtitle": f"**Author:** {author}",
                "facts": [
                    { "name": "Title", "value": title },
                    { "name": "Source Branch", "value": source_branch },
                    { "name": "Destination Branch", "value": destination_branch },
                    { "name": "Link", "value": f"[View PR]({pr_link})" }
                ],
                "markdown": True
            }]
        }

        response = requests.post(TEAMS_WEBHOOK_URL, json=teams_payload)
        response.raise_for_status()

        return jsonify({'message': 'Notification sent to Teams'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
