# app.py
# Main Flask application for Job Tracker
# Comments are provided throughout for learning and debugging!

from flask import Flask, redirect, url_for, render_template, request, jsonify, session
from flask_dance.contrib.google import make_google_blueprint, google
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file (keeps secrets out of code)
load_dotenv()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for local/dev; never do this for production

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Flask needs a secret key for sessions

# (Optional) Enforce HTTPS when running on Render.com (production)
if os.getenv("RENDER", ""):
    try:
        from flask_sslify import SSLify
        sslify = SSLify(app)
    except ImportError:
        print("⚠️ flask-sslify not found, skipping SSL enforcement.")

# Google OAuth setup: allows users to login with Google accounts
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
)
app.register_blueprint(google_bp, url_prefix="/login")

# Main page route
@app.route('/')
def home():
    # If user not logged in with Google, redirect to login
    if not google.authorized:
        return redirect(url_for("google.login"))
    try:
        # Get user info from Google
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            return "Failed to fetch user info", 500
        user_info = resp.json()

        # Check if email is allowed (basic access control)
        ALLOWED_USERS = set(os.getenv("ALLOWED_USERS", "").split(","))
        if user_info["email"] not in ALLOWED_USERS:
            return "Access Denied", 403

        # If logged in and authorized, show the job entry form (index.html)
        return render_template('index.html')
    except TokenExpiredError:
        # OAuth token expired, clear session and ask user to login again
        session.clear()
        return redirect(url_for("google.login"))
    except Exception as e:
        # Any other error for debugging
        print(f"Unexpected error in home(): {e}")
        return "An unexpected error occurred.", 500

# Job submission endpoint (AJAX POST from frontend)
@app.route('/submit', methods=['POST'])
def submit():
    if not google.authorized:
        return jsonify({"status": "unauthorized"}), 401

    data = request.json  # Parse incoming JSON data from the job form

    # Set up Google Sheets API scopes
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]

    # Authenticate to Google using service account credentials (from .env/credentials.json)
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"),
        scope
    )
    client = gspread.authorize(creds)
    sheet = client.open("JobTracker").sheet1  # Open your Google Sheet by name

    # Append new row to the Google Sheet with form data
    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("customer_name"),
        data.get("address"),
        data.get("date"),
        data.get("job_description"),
        data.get("payment_status"),
        data.get("notes")
    ], value_input_option='USER_ENTERED')

    return jsonify({"status": "success"}), 200  # Success response to JS

# Simple logout: clears session
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))

# Health check route for Render.com (can be used for uptime monitoring)
@app.route('/healthz')
def healthz():
    return "OK", 200

# Only run the app if executing directly (not when importing in tests)
if __name__ == "__main__":
    app.run(debug=True)
