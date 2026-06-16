import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json

load_dotenv()

# Configure Gemini API if key is available
api_key = os.getenv("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)

def generate_interview_questions(skills, unused_arg=None, category='Technical'):
    """
    Generates personalized interview questions based on the candidate's skills and the requested category.
    """
    if client:
        try:
            prompt = f"""
            You are an expert technical interviewer and career coach.
            The candidate has the following skills: {', '.join(skills) if skills else 'None listed'}
            
            Based on this profile, generate 3 highly personalized interview questions for the category: {category}.
            
            Return the response strictly as a JSON object with this exact structure:
            {{
                "questions": [
                    {{"question": "Question text here", "suggested_answer": "Brief advice or suggested approach to answer this question"}}
                ]
            }}
            Return ONLY the JSON. Do not include markdown code blocks.
            """
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt,
            )
            # Clean up response
            response_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(response_text)
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return simulate_interview_questions(skills, category)
    else:
        return simulate_interview_questions(skills, category)

def simulate_interview_questions(skills, category):
    """Fallback method to generate questions when no API key is present."""
    questions = []
    
    if category == 'Technical':
        for skill in skills[:3]:
            questions.append({
                "question": f"Can you explain a challenging project where you successfully utilized {skill}?",
                "suggested_answer": f"Use the STAR method to describe a specific scenario where you used {skill} to solve a complex problem."
            })
    elif category == 'Behavioral':
        questions = [
            {"question": "Tell me about a time you had to adapt to a significant change at work.", "suggested_answer": "Focus on your flexibility and positive attitude during the transition."},
            {"question": "Describe a situation where you disagreed with a team member. How did you handle it?", "suggested_answer": "Highlight your communication and conflict resolution skills."}
        ]
    else:
        questions = [
            {"question": "Where do you see your career heading in the next 3 to 5 years?", "suggested_answer": "Align your goals with the potential growth path of the company."},
            {"question": "Why do you want to work for our company?", "suggested_answer": "Show that you've researched the company and align with its mission."}
        ]
        
    return {
        "questions": questions
    }
