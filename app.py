from flask import Flask, render_template, request, send_file
import requests
import time
import csv
import io

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

def check_username_status(username):
    url = f"https://www.instagram.com/{username}/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return "Active"
        elif response.status_code == 404:
            return "Not Found or Banned"
        elif response.status_code == 429:
            return "Rate Limited"
        else:
            return f"Unknown ({response.status_code})"
    except requests.RequestException as e:
        return f"Error: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        usernames = request.form['usernames'].splitlines()
        for username in usernames:
            username = username.strip()
            if username:
                status = check_username_status(username)
                results.append((username, status))
                time.sleep(1)
    return render_template('index.html', results=results)

@app.route('/download', methods=['POST'])
def download():
    data = request.form.get('csvdata')
    if not data:
        return "No data to download."
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Username', 'Status'])
    for line in data.strip().split('\n'):
        writer.writerow(line.split(','))
    output.seek(0)
    return send_file(io.BytesIO(output.read().encode()), mimetype='text/csv', as_attachment=True, download_name='results.csv')

if __name__ == '__main__':
    app.run(debug=True)
