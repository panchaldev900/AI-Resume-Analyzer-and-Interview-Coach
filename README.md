# AI Resume Analyzer & Interview Coach

A premium, modern SaaS web application that empowers job seekers to bypass Applicant Tracking Systems (ATS) and ace their technical interviews. Powered by **Google Gemini AI**, this platform analyzes your resume, compares it against job descriptions, and provides an interactive mock interview simulator.

![AI Resume Analyzer Banner](https://via.placeholder.com/1200x400.png?text=AI+Resume+Analyzer+%26+Interview+Coach) *(Replace with actual screenshot)*

## 🚀 Features

*   **Intelligent ATS Scoring:** Upload your PDF resume and a Job Description. The AI calculates a match percentage and extracts matched vs. missing skills.
*   **Actionable Feedback:** Get detailed, personalized insights into your strengths, weaknesses, and actionable suggestions to improve your resume.
*   **Interactive Mock Interviewer:** The AI generates highly targeted interview questions (Technical, Behavioral, HR, System Design) based on the skills in your resume.
*   **Real-time Interview Evaluation:** Type your answers directly into the chat! The AI acts as an HR recruiter to grade your answer out of 10, provides constructive feedback, and shows you an improved "STAR-method" answer.
*   **Downloadable PDF Reports:** Export your complete ATS analysis report to a beautifully formatted PDF.
*   **Dashboard & History:** Secure user authentication allows you to track your past resume analyses over time.
*   **Premium Glassmorphism UI:** A sleek, dark-mode, highly responsive interface designed to feel like a top-tier SaaS product.

## 🛠️ Technology Stack

*   **Frontend:** HTML5, CSS3 (Custom Glassmorphism), Bootstrap 5, Vanilla JavaScript, FontAwesome
*   **Backend:** Python 3.10+, Flask, Flask-Login, Flask-SQLAlchemy
*   **Database:** SQLite
*   **AI Integration:** Google Gemini API (`google-genai`)
*   **Utilities:** PyPDF2 (Resume text extraction), ReportLab (PDF generation), Werkzeug (Password hashing)

## ⚙️ Local Setup & Installation

Follow these steps to run the application locally on your machine.

### 1. Clone the repository
```bash
git clone https://github.com/your-username/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### 2. Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
1. Rename the `.env.example` file to `.env`.
2. Get your free API key from [Google AI Studio](https://aistudio.google.com/).
3. Add your key to the `.env` file:
```env
GEMINI_API_KEY=your_actual_api_key_here
FLASK_SECRET_KEY=your_random_secret_key_here
```
*(Note: Your `.env` file is automatically ignored by git to protect your secrets).*

### 5. Initialize the Database
The SQLite database will be created automatically the first time you run the application.

### 6. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000` to view the app!

## 📂 Project Structure

```text
├── app.py                      # Main Flask application and routing
├── models.py                   # SQLAlchemy Database models
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variables
├── utils/                      # Helper modules
│   ├── ats_calculator.py       # Gemini API integration for resume parsing
│   ├── interview_generator.py  # Gemini API integration for interview chat
│   ├── pdf_parser.py           # PyPDF2 text extraction
│   └── skill_extractor.py      # Basic skill fallback extraction
├── static/                     # Static assets
│   ├── css/style.css           # Custom UI styling and layout
│   └── js/main.js              # Frontend interactivity
├── templates/                  # HTML templates (Jinja2)
│   ├── base.html               # Master layout
│   ├── index.html              # Landing page
│   ├── dashboard.html          # User dashboard
│   └── interview.html          # Interactive Mock Interview UI
└── uploads/                    # Temporary storage for uploaded resumes
```

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/your-username/ai-resume-analyzer/issues).

## 📝 License
This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.
