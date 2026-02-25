import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json



from nlp.skill_extractor import process_resumes, process_jd

from scoring.scorer import calculate_scores

from recommendation.recommender import generate_recommendations

from email_service.email_sender import send_email


INPUT_DIR = "data/input"
OUTPUT_DIR = "data/output"
THRESHOLD_SCORE = 70


def main(threshold):



    print("\n=== AI Resume Ranking System ===\n")
    # STEP 1: Extract resumes and JD
    print("Extracting resumes using Groq...")
    resumes = process_resumes()
    print("Extracting job description...")
    jd = process_jd()
    if not jd:
        print("❌ No JD found. Exiting.")
        return []
    # STEP 2: Score resumes and generate recommendations
    results = []
    for resume in resumes:
        score_result = calculate_scores(resume, jd, threshold)
        score = score_result.get("resume_score", 0)
        recommendations = generate_recommendations(resume, jd)
        email = resume.get("email", "")
        filename = resume.get("name", "")
        email_status = "Not Sent"
        if score < threshold and email:
            send_email(
                candidate_email=email,
                candidate_name=filename,
                score=score,
                threshold=threshold,
                missing_skills=recommendations.get("missing_skills", []),
                suggestions=recommendations.get("recommendations", [])
            )
            email_status = "Sent"
        results.append({
            "filename": filename,
            "email": email,
            "score": score,
            "email_status": email_status,
            "recommendations": recommendations
        })
    # STEP 3: Rank resumes
    results.sort(key=lambda x: x["score"], reverse=True)
    print("\n=== FINAL RANKING ===\n")
    for rank, r in enumerate(results, 1):
        print(f"Rank {rank}: {r['filename']}")
        print(f"Score: {r['score']}")
        print(f"Email Status: {r['email_status']}")
        print("-" * 40)
    return results

if __name__ == "__main__":
    main(THRESHOLD_SCORE)