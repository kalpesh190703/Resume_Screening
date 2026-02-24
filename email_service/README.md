# Email Service

## Purpose
Send automated candidate notifications via Gmail SMTP when a resume score is below a threshold.

## Setup
1. Install dependencies:
   `python -m pip install -r requirements.txt`
2. Configure environment variables in project root `.env`:
   `SENDER_EMAIL=your_email_here`
   `SENDER_PASSWORD=your_app_password_here`

## Inputs (Required)
- `candidate_email` (str): Recipient email address.
- `candidate_name` (str): Candidate full name.
- `score` (float): Resume score.
- `threshold` (float): Required threshold.
- `missing_skills` (list[str]): Missing skills list (can be empty).
- `suggestions` (list[str]): Improvement suggestions list (can be empty).

## When Email Is Sent
- Email is sent only if `score < threshold`.
- If `score >= threshold`, no email is sent and the caller receives a `Not Required` status.

## Return Format
- `{"status": "Success" | "Failed" | "Not Required", "message": "<details>"}`

## How To Call
- Import: `from email_service import send_email`

## Libraries Used
- Standard library: `smtplib`, `email.mime`
- External: `python-dotenv`
