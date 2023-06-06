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

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html>
    <head>
        <title>Mandrill Link Decoder</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                text-align: center;
            }
            form {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            textarea {
                width: 100%;
                height: 100px;
                margin-bottom: 20px;
                padding: 10px;
                box-sizing: border-box;
                resize: none;
            }
            button {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                cursor: pointer;
            }
            button:hover {
                background-color: #3e8e41;
            }
            .result-table-container {
                width: 100%;
                overflow-x: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                text-align: left;
                padding: 8px;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            .error {
              color:red
          }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Mandrill Link Decoder</h1>
            <form id="form">
                <textarea id="mandrill-link" placeholder="Enter Mandrill link here..."></textarea>
                <button type="submit">Decode</button>
            </form>
          <div class="error"></div>
          <table>
              <tr>
                  <th>Decoded URLs</th>
              </tr>
          </table>
          <div class="result-table-container">
              <table id="result-table">
              </table>
          </div>
        </div>
        <script>
          function showError(message) {
              var errorDiv = document.querySelector('.error');
              errorDiv.textContent = message
          }

          function clearError() {
              showError('')
          }

          document.getElementById('form').addEventListener('submit', function(event) {
              event.preventDefault();
              
              var mandrillLink = document.getElementById('mandrill-link').value;

              clearError()

              fetch('/decode', {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json'
                  },
                  body: JSON.stringify({
                      mandrill_url: mandrillLink
                  })
              })
                  .then(function(response) {
                      if (!response.ok) throw Error(response.statusText)
                      return response.json();
                  })
                  .then(function(data) {
                      var resultTable = document.getElementById('result-table');
                      var newRow = resultTable.insertRow(-1);
                      var newCell = newRow.insertCell(0);
                      newCell.innerHTML = '<a href="' + data.url + '" target="_blank" rel="noreferrer">' + data.url + '</a>';
                  })
                  .catch(function(error) {
                      showError('An error occurred. Please check that the input URL is in the correct format.')
                  });
          });
        </script>
    </body>
</html>
"""

@app.route('/decode', methods=['POST'])
def decode():
    data = request.get_json()
    mandrill_url = data['mandrill_url']
    url = extract_url(mandrill_url)
    return {'url': url}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

