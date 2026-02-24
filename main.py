import json
from recommendation.reco_engine import generate_recommendations

def main():
    # Load JD
    with open("jd.json", "r") as f:
        jd_data = json.load(f)

    # Load Resume
    with open("resume.json", "r") as f:
        resumes = json.load(f)

    # Ensure resumes is a list
    if isinstance(resumes, dict):
        resumes = [resumes]  # wrap single resume in a list

    all_recommendations = []
    for resume_data in resumes:
        reco = generate_recommendations(resume_data, jd_data)
        all_recommendations.append(reco)

    # --- Change output filename here ---
    output_file = "output_recommendation.json"

    with open(output_file, "w") as f:
        json.dump(all_recommendations, f, indent=4)

    print(f" Completed: Recommendations generated.")
    print(f"Output saved as '{output_file}'")

if __name__ == "__main__":
    main()