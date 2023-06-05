from flask import Flask, request
import base64
import json
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

def extract_url(mandrill_url):
    parsed_url = urlparse(mandrill_url)
    query = parse_qs(parsed_url.query)
    p = query.get('p', [''])[0]

    # Add padding if necessary
    missing_padding = len(p) % 4
    if missing_padding:
        p += '=' * (4 - missing_padding)

    decoded_p = base64.b64decode(p).decode('utf-8')
    json_p = json.loads(decoded_p)

    # Extract the URL from the decoded JSON object
    url = json.loads(json_p['p'])['url']

    return url

@app.route('/decode', methods=['POST'])
def decode():
    data = request.get_json()
    mandrill_url = data['mandrill_url']
    url = extract_url(mandrill_url)
    return {'url': url}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

