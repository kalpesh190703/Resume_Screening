# Resume Similarity Scoring System

This project calculates similarity scores between resumes and job descriptions (JD) using a weighted scoring model.

## Features
- **Virtual Environment**: Set up with Python 3.11.
- **Weighted Scoring Model**:
  - **Skill Match (50%)**: Based on intersection of resume skills and JD skills.
  - **Experience Match (30%)**: Based on the candidate's years of experience relative to the minimum required.
  - **Keyword Relevance (20%)**: Based on fixed keywords in JD compared against resume text.
- **Threshold Validation**: Compares the final score against a user-defined threshold.
- **Structured JSON Output**: Provides complete matching details in a machine-readable format.

## Fixed JSON Structure
The system expects resumes in the following format:
```json
{
  "name": "string",
  "email": "string",
  "skills": ["skill1", "skill2"],
  "education": "string",
  "experience_years": number
}
```

Job Descriptions should follow this format:
```json
{
  "skills": ["skill1", "skill2"],
  "min_experience_years": number,
  "keywords": ["keyword1", "keyword2"]
}
```

## Setup and Usage

1. **Activate Virtual Environment**:
   ```powershell
   .\venv\Scripts\activate
   ```

2. **Run the Scorer**:
   ```powershell
   python scorer.py <resume_json_path> <jd_json_path> <threshold_percentage>
   ```

### Example
```powershell
python scorer.py resume.json jd.json 50
```

## Output Format
The tool outputs a structured JSON object:
```json
{
  "candidate_name": "John Doe",
  "skill_match_percentage": 60.0,
  "experience_match_percentage": 80.0,
  "keyword_relevance_score": 33.33,
  "final_score": 60.67,
  "missing_skills": [
    "kubernetes",
    "cloud computing"
  ],
  "threshold": 50.0,
  "status": "Passed"
}
```
