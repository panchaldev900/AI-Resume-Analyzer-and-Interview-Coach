import os
from google import genai
import json

def analyze_resume_with_llm(resume_text, jd_text):
    """
    Uses Gemini LLM to comprehensively analyze a resume against a Job Description.
    If the Job Description is empty, it infers the target role and analyzes based on industry standards.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found. Returning fallback data.")
        return 0, ["Python", "Flask"], ["Docker", "AWS"], ["Good formatting"], ["Missing key skills"], ["Add more projects"]

    client = genai.Client(api_key=api_key)

    if jd_text and jd_text.strip():
        jd_context = f"""
        Here is the Job Description the user is applying for:
        {jd_text[:4000]}
        """
    else:
        jd_context = """
        The user has not provided a Job Description. 
        Please infer the target job role based on their resume and analyze the resume against standard industry expectations for that role.
        """

    prompt = f"""
    You are an expert HR recruiter, ATS system, and Career Coach.
    I will provide you with a candidate's resume text and either a specific Job Description or ask you to infer their target role.

    {jd_context}

    Here is the Candidate's Resume:
    {resume_text[:4000]}

    Perform a comprehensive analysis and return the result strictly as a JSON object matching exactly this schema:
    {{
        "ats_score": <integer from 0 to 100 based on how well they fit the JD or industry standard>,
        "matched_skills": ["Skill 1", "Skill 2"], // Skills they possess that are highly relevant
        "missing_skills": ["Skill 3", "Skill 4"], // Critical skills for the role that are missing from their resume
        "strengths": ["Strength 1", "Strength 2"], // 2-3 specific strengths based on their experience and skills
        "weaknesses": ["Weakness 1", "Weakness 2"], // 1-2 specific weaknesses, missing keywords, or experience gaps
        "suggestions": ["Suggestion 1", "Suggestion 2"] // 2-3 actionable suggestions for improving the resume or interview prep
    }}

    IMPORTANT RULES:
    1. Base your "strengths" and "weaknesses" on actual experience checks (e.g. "You list React but have no projects showing it" or "Strong 5 year track record in Backend").
    2. Provide highly personalized actionable suggestions.
    3. Return ONLY the JSON. Do not use markdown formatting like ```json or ```.
    """

    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
        )
        
        response_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(response_text)
        
        return (
            data.get("ats_score", 0),
            data.get("matched_skills", []),
            data.get("missing_skills", []),
            data.get("strengths", []),
            data.get("weaknesses", []),
            data.get("suggestions", [])
        )
    except Exception as e:
        print(f"Error during LLM Analysis: {e}")
        return 0, [], [], ["Error during AI analysis"], ["Could not connect to LLM"], ["Please try again later"]
