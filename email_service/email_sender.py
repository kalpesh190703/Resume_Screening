"""Email sender module using Gmail SMTP."""
import smtplib
from typing import List, Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .config import SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT
from .email_template import generate_email_content


def send_email(
    candidate_email: str,
    candidate_name: str,
    score: float,
    threshold: float,
    missing_skills: List[str],
    suggestions: List[str],
    job_title: str = "",
    strengths: List[str] = None,
    experience_gap: str = "",
    overall_assessment: str = ""
) -> Dict[str, str]:
    """Send an email notification to a candidate if score is below threshold.

    Args:
        candidate_email: Recipient email address.
        candidate_name: Candidate full name.
        score: Resume score.
        threshold: Required threshold.
        missing_skills: List of missing skills.
        suggestions: List of improvement suggestions.

    Returns:
        Dict with status and message.
    """
    if score >= threshold:
        return {"status": "Not Required", "message": "Score above threshold"}

    subject, body = generate_email_content(
        candidate_name, score, threshold, missing_skills, suggestions,
        job_title=job_title,
        strengths=strengths,
        experience_gap=experience_gap,
        overall_assessment=overall_assessment
    )

    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = candidate_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    server = None
    try:
        # Connect to Gmail SMTP server with TLS
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()

        # Login and send
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, candidate_email, message.as_string())

        return {"status": "Success", "message": "Email sent successfully"}
    except Exception as exc:
        return {"status": "Failed", "message": f"Failed to send email: {exc}"}
    finally:
        # Ensure server is closed properly
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass
