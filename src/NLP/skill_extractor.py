#input will be text, output will be a list of skills extracted from the text
import re
def extract_skills(text):
    # Define a list of skills to look for
    skills = ['python', 'java', 'c++', 'javascript', 'sql', 'machine learning', 'data analysis', 'communication', 'teamwork', 'problem solving']
    
    # Convert the text to lowercase for case-insensitive matching
    text = text.lower()
    
    # Use regular expressions to find all occurrences of the skills in the text
    extracted_skills = []
    for skill in skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            extracted_skills.append(skill)
    
    return extracted_skills