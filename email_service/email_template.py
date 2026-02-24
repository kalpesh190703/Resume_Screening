"""Email template generator for candidate notifications."""
from typing import List, Tuple


def _format_list(items: List[str]) -> str:
    """Return a clean, human-readable list string."""
    if not items:
        return "None"
    return "\n".join(f"- {item}" for item in items)


def generate_email_content(
    candidate_name: str,
    score: float,
    threshold: float,
    missing_skills: List[str],
    suggestions: List[str],
) -> Tuple[str, str]:
    """Generate email subject and body for a candidate.

    Args:
        candidate_name: Candidate full name.
        score: Resume score.
        threshold: Required threshold.
        missing_skills: List of missing skills.
        suggestions: List of improvement suggestions.

    Returns:
        (subject, body) tuple.
    """
    status = "Below Threshold" if score < threshold else "Meets/Above Threshold"

    subject = "Resume Screening Result"
    body = (
        f"Hello {candidate_name},\n\n"
        "Thank you for your interest in the position. Here are your screening results:\n\n"
        f"Resume Score: {score}\n"
        f"Threshold: {threshold}\n"
        f"Status: {status}\n\n"
        "Missing Skills:\n"
        f"{_format_list(missing_skills)}\n\n"
        "Improvement Suggestions:\n"
        f"{_format_list(suggestions)}\n\n"
        "Best regards,\n"
        "Recruitment Team\n"
    )

    return subject, body
