# Resume Similarity Scorer

This tool calculates the similarity between a resume and a job description based on weighted criteria.

## Features
- **Skill Match (40%)**: Calculates the percentage of required skills present in the resume.
- **Tools Match (10%)**: Calculates the percentage of required tools present in the resume.
- **Experience Match (30%)**: Compares the candidate's experience years against the JD's requirements.
- **Keyword Relevance (20%)**: Matches JD keywords against the resume's skills, education, and name.

## Setup
1. Ensure Python 3.11 is installed.
2. The project includes a virtual environment in `venv/`.
3. Activate the environment:
   ```powershell
   .\venv\Scripts\activate
   ```

## Usage
Run the `scorer.py` script with the paths to your resume and JD JSON files, followed by the threshold percentage.

```bash
python scorer.py <resume_json_path> <jd_json_path> <threshold_percentage>
```

### Example
```bash
python scorer.py resume.json jd.json 70
```

## JSON Structure
The resumes and JDs should follow this structure:

```json
{
  "name": "Candidate Name",
  "email": "email@example.com",
  "skills": ["Skill 1", "Skill 2"],
  "tools": ["Tool 1", "Tool 2"],
  "education": "Degree Info",
  "experience_years": 5,
  "keywords": ["Keyword 1"]
}
```

## Output
The script outputs a JSON object containing:
- **Resume score**: The final weighted score.
- **JD score**: The baseline score (100%).
- **missing_skills**: List of skills required by the JD but missing from the resume.
- **threshold_met**: Boolean indicating if the score meets the user's threshold.
