from flask import Flask, render_template, request, jsonify, url_for, redirect, flash, send_file
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import json
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from models import db, Resume, User
from utils.pdf_parser import extract_text_from_pdf
from utils.skill_extractor import extract_skills
from utils.ats_calculator import analyze_resume_with_llm
from utils.interview_generator import generate_interview_questions, evaluate_interview_answer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key_for_saas_app'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/resume_analyzer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max upload

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database'), exist_ok=True)

with app.app_context():
    db.create_all()

# --- HTML Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
            
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('dashboard'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/analyze')
@login_required
def analyze():
    return render_template('analyze.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/interview')
@login_required
def interview():
    return render_template('interview.html')

@app.route('/about')
def about():
    return render_template('about.html')

# --- API Routes ---

@app.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file provided'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    jd_text = request.form.get('job_description', '')
        
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text
        text = extract_text_from_pdf(filepath)
        if not text:
            return jsonify({'error': 'Failed to extract text from PDF'}), 500
            
        # Calculate ATS score and feedback using the new LLM engine
        score, matched, missing, strengths, weaknesses, suggestions = analyze_resume_with_llm(text, jd_text)
        
        feedback_data = {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions
        }
        
        # Save to database
        try:
            new_resume = Resume(
                user_id=current_user.id,
                resume_name=filename,
                ats_score=score,
                extracted_skills=json.dumps({'matched': matched, 'missing': missing}),
                feedback=json.dumps(feedback_data)
            )
            db.session.add(new_resume)
            db.session.commit()
        except Exception as e:
            print(f"Error saving to database: {e}")
        
        return jsonify({
            'ats_score': score,
            'matched_skills': matched,
            'missing_skills': missing,
            'feedback': feedback_data
        })
        
    return jsonify({'error': 'Only PDF files are allowed'}), 400

@app.route('/api/generate_interview', methods=['POST'])
@login_required
def api_generate_interview():
    data = request.json
    if not data or 'skills' not in data:
        return jsonify({'error': 'Missing required skills data'}), 400
        
    skills = data['skills']
    category = data.get('category', 'Technical')
    
    interview_data = generate_interview_questions(skills, [], category=category)
    return jsonify(interview_data)

@app.route('/api/history', methods=['GET'])
@login_required
def api_history():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.upload_date.desc()).all()
    history_data = []
    for r in resumes:
        skills_dict = json.loads(r.extracted_skills) if r.extracted_skills else {'matched': [], 'missing': []}
        history_data.append({
            'id': r.id,
            'resume_name': r.resume_name,
            'upload_date': r.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
            'ats_score': r.ats_score,
            'extracted_skills': skills_dict
        })
    return jsonify(history_data)

@app.route('/api/latest_resume', methods=['GET'])
@login_required
def api_latest_resume():
    latest = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.upload_date.desc()).first()
    if not latest:
        return jsonify({'error': 'No resume found'}), 404
        
    skills_dict = json.loads(latest.extracted_skills) if latest.extracted_skills else {'matched': [], 'missing': []}
    feedback_dict = json.loads(latest.feedback) if latest.feedback else {'strengths': [], 'weaknesses': [], 'suggestions': []}
    
    return jsonify({
        'ats_score': latest.ats_score,
        'matched_skills': skills_dict.get('matched', []),
        'missing_skills': skills_dict.get('missing', []),
        'feedback': feedback_dict
    })

@app.route('/api/download_report', methods=['GET'])
@login_required
def download_report():
    latest = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.upload_date.desc()).first()
    if not latest:
        return jsonify({'error': 'No resume found'}), 404

    # Create PDF in memory
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "AI Resume Analysis Report")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"File: {latest.resume_name}")
    c.drawString(50, height - 100, f"Date: {latest.upload_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Score
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 140, f"ATS Match Score: {latest.ats_score}%")
    
    y = height - 180
    
    # Skills
    skills_dict = json.loads(latest.extracted_skills) if latest.extracted_skills else {}
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Matched Skills:")
    y -= 20
    c.setFont("Helvetica", 10)
    matched = ", ".join(skills_dict.get('matched', []))
    c.drawString(50, y, matched if matched else "None")
    
    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Missing Skills:")
    y -= 20
    c.setFont("Helvetica", 10)
    missing = ", ".join(skills_dict.get('missing', []))
    c.drawString(50, y, missing if missing else "None")
    
    y -= 40
    feedback_dict = json.loads(latest.feedback) if latest.feedback else {}
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Key Suggestions:")
    y -= 20
    c.setFont("Helvetica", 10)
    for sug in feedback_dict.get('suggestions', [])[:5]:
        c.drawString(50, y, f"- {sug}")
        y -= 15

    c.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Resume_Report_{latest.id}.pdf",
        mimetype='application/pdf'
    )

@app.route('/api/evaluate_answer', methods=['POST'])
@login_required
def evaluate_answer():
    data = request.json
    question = data.get('question')
    user_answer = data.get('user_answer')
    
    if not question or not user_answer:
        return jsonify({'error': 'Missing question or user_answer'}), 400
        
    evaluation = evaluate_interview_answer(question, user_answer)
    return jsonify(evaluation)

if __name__ == '__main__':
    app.run(debug=True)
