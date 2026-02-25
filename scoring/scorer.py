import json
import sys
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables and initialize Groq client
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    client = None
else:
    try:
        client = Groq(api_key=api_key)
    except Exception:
        client = None

def get_matches_with_llm(resume_items, jd_items, item_type="skills"):
    """
    Uses Groq LLM to perform semantic matching between resume items and JD requirements.
    """
    if not jd_items:
        return set(), []
    
    if not resume_items:
        return set(), list(jd_items)

    # Fallback if client is not initialized
    if not client:
        resume_set = {i.lower().strip() for i in resume_items}
        jd_set_map = {i.lower().strip(): i for i in jd_items}
        matched_keys = resume_set.intersection(set(jd_set_map.keys()))
        matched = [jd_set_map[k] for k in matched_keys]
        missing = [i for i in jd_items if i not in matched]
        return set(matched), missing

    prompt = f"""
    COMPARE THE FOLLOWING CANDIDATE '{item_type}' WITH THE REQUIRED '{item_type}' FROM THE JOB DESCRIPTION.
    
    IDENTIFY WHICH REQUIRED '{item_type}' ARE PRESENT BASED ON SEMANTIC MEANING.
    FOR EXAMPLE:
    - "SQL" matches "PostgreSQL", "MySQL", or "NoSQL".
    - "REST API" matches "Web Services" or "Flask".
    - "Django" might be matched if the candidate has strong "Python" and "Backend" experience but prioritize direct mentions.
    
    Candidate {item_type}: {", ".join(resume_items)}
    Required {item_type}: {", ".join(jd_items)}
    
    CRITICAL: YOU MUST RETURN A JSON OBJECT WITH STRONGLY THESE TWO KEYS:
    1. "matched": a list of specific items EXACTLY AS THEY APPEAR in the "Required {item_type}" list that the candidate demonstrates.
    2. "missing": a list of specific items EXACTLY AS THEY APPEAR in the "Required {item_type}" list that the candidate is missing.
    
    DO NOT ADD NEW ITEMS. ONLY USE ITEMS FROM THE "Required {item_type}" LIST.
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        matched_llm = result.get("matched", [])
        
        # Ensure we only return items that were actually in the JD list (case-insensitive check but preserve original)
        jd_lower_map = {i.lower().strip(): i for i in jd_items}
        
        final_matched = []
        for item in matched_llm:
            if item.lower().strip() in jd_lower_map:
                final_matched.append(jd_lower_map[item.lower().strip()])
                
        final_matched = list(set(final_matched))
        missing = [i for i in jd_items if i not in final_matched]
        
        return set(final_matched), missing
    except Exception:
        # Fallback to exact matching
        resume_set = {i.lower().strip() for i in resume_items}
        jd_set_map = {i.lower().strip(): i for i in jd_items}
        
        matched_keys = resume_set.intersection(set(jd_set_map.keys()))
        matched = [jd_set_map[k] for k in matched_keys]
        missing = [i for i in jd_items if i not in matched]
        
        return set(matched), missing

def calculate_scores(resume_data, jd_data, threshold):
    # helper to clean and get lists
    def get_list(data, key):
        items = data.get(key, [])
        if isinstance(items, str):
            items = [items]
        return [str(i).strip() for i in items]

    # 1. Skill Match (40%)
    resume_skills = get_list(resume_data, 'skills')
    jd_skills = get_list(jd_data, 'skills')
    
    if not jd_skills:
        skill_score = 1.0
        missing_skills = []
    else:
        matched_skills, missing_skills = get_matches_with_llm(resume_skills, jd_skills, "skills")
        skill_score = len(matched_skills) / len(jd_skills)
    
    # 2. Tools Match (10%)
    resume_tools = get_list(resume_data, 'tools')
    jd_tools = get_list(jd_data, 'tools')
    
    if not jd_tools:
        tools_score = 1.0
    else:
        matched_tools, _ = get_matches_with_llm(resume_tools, jd_tools, "tools")
        tools_score = len(matched_tools) / len(jd_tools)

    # 3. Experience Match (30%)
    resume_exp = resume_data.get('experience_years') or resume_data.get('experience years', 0)
    jd_min_exp = jd_data.get('experience_years') or jd_data.get('experience years', 0)
    
    if jd_min_exp == 0:
        exp_score = 1.0
    else:
        exp_score = min(1.0, float(resume_exp) / float(jd_min_exp))
        
    # 4. Keyword Relevance (20%)
    jd_keywords = get_list(jd_data, 'keywords')
    if not jd_keywords:
        jd_keywords = jd_skills + jd_tools

    if not jd_keywords:
        keyword_score = 1.0
    else:
        # Include resume-level keywords if present
        resume_keywords = get_list(resume_data, 'keywords')
        
        resume_context = [
            str(resume_data.get('name', "")),
            str(resume_data.get('education', "")),
            ", ".join(resume_skills),
            ", ".join(resume_tools),
            ", ".join(resume_keywords) # Fix: Added resume-level keywords to the context
        ]
        matched_keywords, _ = get_matches_with_llm(resume_context, jd_keywords, "keywords")
        keyword_score = len(matched_keywords) / len(jd_keywords) if jd_keywords else 1.0
        
    final_score = (skill_score * 0.40) + \
                  (tools_score * 0.10) + \
                  (exp_score * 0.30) + \
                  (keyword_score * 0.20)
    
    return {
        "resume_score": round(final_score * 100, 2),
        "jd_score": 100.0,
        "missing_skills": missing_skills,
        "is_above_threshold": (final_score * 100) >= threshold,
        "details": {
            "skill_match": round(skill_score * 100, 2),
            "tools_match": round(tools_score * 100, 2),
            "experience_match": round(exp_score * 100, 2),
            "keyword_relevance": round(keyword_score * 100, 2)
        }
    }

def main():
    if len(sys.argv) < 4:
        print("Usage: python scorer.py <resume_json_path> <jd_json_path> <threshold_percentage>")
        sys.exit(1)
        
    resume_path = sys.argv[1]
    jd_path = sys.argv[2]
    try:
        threshold = float(sys.argv[3])
    except ValueError:
        sys.exit(1)
        
    try:
        with open(resume_path, 'r') as f:
            resume_data_raw = json.load(f)
        with open(jd_path, 'r') as f:
            jd_data = json.load(f)
            
        # Handle list of resumes or single resume
        resumes = resume_data_raw if isinstance(resume_data_raw, list) else [resume_data_raw]
        
        all_results = []
        for res in resumes:
            results = calculate_scores(res, jd_data, threshold)
            all_results.append({
                "candidate": res.get("name", "Unknown"),
                "Resume score": f"{results['resume_score']}%",
                "JD score": f"{results['jd_score']}%",
                "missing_skills": results['missing_skills'],
                "threshold_met": results['is_above_threshold'],
                "details": results['details']
            })
            
        print("\n--- Similarity Calculation Results (LLM Powered) ---")
        print(json.dumps(all_results if len(all_results) > 1 else all_results[0], indent=4))

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
