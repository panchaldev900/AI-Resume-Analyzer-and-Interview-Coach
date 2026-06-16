import re
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)

# Fallback Predefined skills database in case API fails or is not provided
SKILLS_DB = [
    "python", "java", "c++", "sql", "mysql", "flask", "django", "fastapi", 
    "machine learning", "deep learning", "nlp", "generative ai", "langchain", 
    "tensorflow", "pytorch", "git", "docker", "aws", "html", "css", "javascript", "react",
    "azure", "gcp", "kubernetes", "agile", "scrum", "communication", "leadership", "node.js"
]

def extract_skills(text):
    """
    Extracts skills from a given text.
    Uses Gemini AI if API key is available for dynamic, context-aware extraction.
    Falls back to predefined regex matching if API fails or is unavailable.
    """
    if not text:
        return []

    if client:
        try:
            prompt = f"""
            You are an expert ATS (Applicant Tracking System).
            Analyze the following text and extract all the professional skills mentioned.
            This could be technical skills (programming languages, tools, frameworks), soft skills, or domain expertise.
            
            Text:
            {text[:4000]} # Limit text length to avoid token limits
            
            Format the response strictly as a JSON array of strings representing the skills.
            Example: ["Python", "Machine Learning", "Project Management"]
            Return ONLY the JSON array. Do not include markdown code blocks.
            """
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt,
            )
            # Clean up potential markdown formatting
            response_text = response.text.replace("```json", "").replace("```", "").strip()
            skills = json.loads(response_text)
            
            # Ensure it's a list of strings
            if isinstance(skills, list):
                # Clean up and deduplicate (case-insensitive)
                unique_skills = []
                seen = set()
                for s in skills:
                    if isinstance(s, str) and s.strip():
                        normalized = s.strip().title()
                        if normalized.lower() not in seen:
                            seen.add(normalized.lower())
                            unique_skills.append(normalized)
                return unique_skills
        except Exception as e:
            print(f"Gemini API Skill Extraction failed: {e}. Falling back to Regex.")

    # --- Fallback logic ---
    text_lower = text.lower()
    extracted_skills = set()
    
    for skill in SKILLS_DB:
        escaped_skill = re.escape(skill)
        if skill.isalnum():
            pattern = r'\b' + escaped_skill + r'\b'
            if re.search(pattern, text_lower):
                extracted_skills.add(skill.title() if skill not in ['sql', 'mysql', 'aws', 'html', 'css', 'nlp', 'gcp'] else skill.upper())
        else:
            if skill in text_lower:
                extracted_skills.add(skill.title())
                
    return list(extracted_skills)
