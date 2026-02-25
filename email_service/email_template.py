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
    job_title: str = "",
    strengths: List[str] = None,
    experience_gap: str = "",
    overall_assessment: str = ""
) -> Tuple[str, str]:
    """Generate email subject and body for a candidate.

    Args:
        candidate_name: Candidate full name.
        score: Resume score.
        threshold: Required threshold.
        missing_skills: List of missing skills.
        suggestions: List of improvement suggestions.
        job_title: Job title/domain.
        strengths: List of strengths.
        experience_gap: Experience gap string.
        overall_assessment: Overall assessment string.

    Returns:
        (subject, body) tuple.
    """
    status = "Below Threshold" if score < threshold else "Meets/Above Threshold"
    strengths = strengths or []

    subject = f"Resume Screening Result for {job_title}" if job_title else "Resume Screening Result"
    body = (
        f"Hello {candidate_name},\n\n"
        f"Thank you for your interest in the position{' for ' + job_title if job_title else ''}. Here are your screening results:\n\n"
        f"Resume Score: {score}\n"
        f"Threshold: {threshold}\n"
        f"Status: {status}\n\n"
        f"Strengths:\n{_format_list(strengths)}\n\n"
        f"Missing Skills:\n{_format_list(missing_skills)}\n\n"
        f"Improvement Suggestions:\n{_format_list(suggestions)}\n\n"
        f"Experience Gap: {experience_gap}\n\n"
        f"Overall Assessment: {overall_assessment}\n\n"
        "Best regards,\n"
        "Recruitment Team\n"
    )
    return subject, body
