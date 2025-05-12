from flask import Flask, redirect, url_for, render_template, request, jsonify, session
from flask_dance.contrib.google import make_google_blueprint, google
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# Allow HTTP during local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = "Y*&jk!z$H3so2@DFj0a9fh@Sx8H4"  # Replace this with a real secret in prod

# Google OAuth with correct scopes
google_bp = make_google_blueprint(
    client_id="977144993270-6mr972qqs2b5nk0464pipfc7hpeu6br1.apps.googleusercontent.com",
    client_secret="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",
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
)
app.register_blueprint(google_bp, url_prefix="/login")

@app.route('/')
def home():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    user_info = resp.json()

    ALLOWED_USERS = {"nfishenden92@gmail.com", "realneal92@gmail.com"}
    if user_info["email"] not in ALLOWED_USERS:
        return "Access Denied", 403

    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if not google.authorized:
        return jsonify({"status": "unauthorized"}), 401

    data = request.json

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("JobTracker").sheet1

    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("customer_name"),
        data.get("address"),
        data.get("date"),
        data.get("job_description"),
        data.get("payment_status"),
        data.get("notes")
    ], value_input_option='USER_ENTERED')

    return jsonify({"status": "success"}), 200

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
