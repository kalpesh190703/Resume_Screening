"""Email service configuration.

Environment variables (loaded from a .env file via python-dotenv):
- SENDER_EMAIL: Gmail address used to send notifications.
- SENDER_PASSWORD: Gmail App Password used for SMTP authentication.
"""
import os

from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
