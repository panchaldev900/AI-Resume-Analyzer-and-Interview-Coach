document.addEventListener('DOMContentLoaded', () => {
    
    // --- Analyze Page Logic ---
    const analyzeForm = document.getElementById('analyzeForm');
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Basic Validation
            if (!analyzeForm.checkValidity()) {
                e.stopPropagation();
                analyzeForm.classList.add('was-validated');
                return;
            }

            const resumeFile = document.getElementById('resumeFile').files[0];
            const jobDescription = document.getElementById('jobDescription').value;
            const analyzeBtn = document.getElementById('analyzeBtn');
            const loadingOverlay = document.getElementById('loadingOverlay');

            // Show Loading State
            analyzeBtn.disabled = true;
            analyzeBtn.querySelector('.btn-text').classList.add('d-none');
            analyzeBtn.querySelector('.spinner-border').classList.remove('d-none');
            analyzeForm.classList.add('d-none');
            loadingOverlay.classList.remove('d-none');

            try {
                // Step 1: Upload and Parse Resume
                const formData = new FormData();
                formData.append('resume', resumeFile);
                
                const uploadRes = await fetch('/upload_resume', {
                    method: 'POST',
                    body: formData
                });
                
                const uploadData = await uploadRes.json();
                
                if (!uploadRes.ok) throw new Error(uploadData.error || 'Upload failed');

                // Step 2: Analyze Resume against JD
                const analyzePayload = {
                    resume_skills: uploadData.skills,
                    job_description: jobDescription,
                    filename: uploadData.filename
                };

                const analyzeRes = await fetch('/analyze_resume', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(analyzePayload)
                });

                const analyzeData = await analyzeRes.json();
                
                if (!analyzeRes.ok) throw new Error(analyzeData.error || 'Analysis failed');

                // Store results in sessionStorage to pass to dashboard
                sessionStorage.setItem('analysisResults', JSON.stringify(analyzeData));
                
                // Redirect to dashboard
                window.location.href = '/dashboard';

            } catch (error) {
                alert('Error: ' + error.message);
                // Reset UI
                analyzeBtn.disabled = false;
                analyzeBtn.querySelector('.btn-text').classList.remove('d-none');
                analyzeBtn.querySelector('.spinner-border').classList.add('d-none');
                analyzeForm.classList.remove('d-none');
                loadingOverlay.classList.add('d-none');
            }
        });
    }

    // --- Dashboard Page Logic ---
    const dashboardContainer = document.getElementById('atsScoreCircle');
    if (dashboardContainer) {
        const resultsStr = sessionStorage.getItem('analysisResults');
        if (!resultsStr) {
            window.location.href = '/analyze';
            return;
        }

        const data = JSON.parse(resultsStr);
        
        // Render ATS Score
        const circle = document.getElementById('atsScoreCircle');
        const scoreText = document.getElementById('atsScoreText');
        const scoreMessage = document.getElementById('atsScoreMessage');
        
        let score = data.ats_score;
        circle.style.setProperty('--value', score);
        scoreText.innerText = `${score}%`;
        
        if (score >= 80) {
            circle.style.setProperty('--progress-color', 'var(--success)');
            scoreMessage.innerText = "Excellent Match!";
            scoreMessage.className = 'mb-0 fw-bold fs-5 text-success';
        } else if (score >= 50) {
            circle.style.setProperty('--progress-color', 'var(--warning)');
            scoreMessage.innerText = "Good Match";
            scoreMessage.className = 'mb-0 fw-bold fs-5 text-warning';
        } else {
            circle.style.setProperty('--progress-color', 'var(--danger)');
            scoreMessage.innerText = "Low Match";
            scoreMessage.className = 'mb-0 fw-bold fs-5 text-danger';
        }

        // Render Matched Skills
        const matchedContainer = document.getElementById('matchedSkills');
        matchedContainer.innerHTML = '';
        if (data.matched_skills.length > 0) {
            data.matched_skills.forEach(skill => {
                matchedContainer.innerHTML += `<span class="skill-badge success"><i class="fa-solid fa-check text-success opacity-75"></i> ${skill}</span>`;
            });
        } else {
            matchedContainer.innerHTML = '<span class="text-muted small w-100 p-2 text-center rounded" style="background: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.1);">No matching skills found in resume.</span>';
        }

        // Render Missing Skills
        const missingContainer = document.getElementById('missingSkills');
        missingContainer.innerHTML = '';
        if (data.missing_skills.length > 0) {
            data.missing_skills.forEach(skill => {
                missingContainer.innerHTML += `<span class="skill-badge danger"><i class="fa-solid fa-xmark text-danger opacity-75"></i> ${skill}</span>`;
            });
        } else if (data.matched_skills.length === 0 && data.ats_score === 0) {
            missingContainer.innerHTML = '<span class="text-muted small w-100 p-2 text-center rounded" style="background: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.1);">No skills extracted from Job Description.</span>';
        } else {
            missingContainer.innerHTML = '<span class="text-success small w-100 p-2 text-center rounded" style="background: var(--success-bg); border: 1px dashed rgba(16, 185, 129, 0.3);"><i class="fa-solid fa-party-horn me-2"></i>You have all required skills!</span>';
        }

        // Render Feedback
        const strengthsList = document.getElementById('strengthsList');
        strengthsList.innerHTML = '';
        if (data.strengths && data.strengths.length > 0) {
            data.strengths.forEach(s => strengthsList.innerHTML += `<li><i class="fa-solid fa-check-circle text-success mt-1"></i> <span>${s}</span></li>`);
        } else {
            strengthsList.innerHTML = `<li><i class="fa-solid fa-info-circle text-muted mt-1"></i> <span>No significant strengths identified against this specific JD.</span></li>`;
        }
        
        const weaknessesList = document.getElementById('weaknessesList');
        weaknessesList.innerHTML = '';
        if (data.weaknesses && data.weaknesses.length > 0) {
            data.weaknesses.forEach(w => weaknessesList.innerHTML += `<li><i class="fa-solid fa-circle-xmark text-danger mt-1"></i> <span>${w}</span></li>`);
        } else {
            weaknessesList.innerHTML = `<li><i class="fa-solid fa-star text-warning mt-1"></i> <span>No major weaknesses found!</span></li>`;
        }

        const suggestionsList = document.getElementById('suggestionsList');
        suggestionsList.innerHTML = '';
        if (data.suggestions && data.suggestions.length > 0) {
            data.suggestions.forEach(s => suggestionsList.innerHTML += `<li><i class="fa-solid fa-arrow-right text-primary mt-1"></i> <span>${s}</span></li>`);
        }
    }

    // --- Interview Page Logic ---
    const interviewContainer = document.getElementById('interviewContent');
    if (interviewContainer) {
        const resultsStr = sessionStorage.getItem('analysisResults');
        if (!resultsStr) {
            window.location.href = '/analyze';
            return;
        }

        const data = JSON.parse(resultsStr);
        const loadingDiv = document.getElementById('interviewLoading');
        
        // Fetch questions
        fetch('/generate_questions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                missing_skills: data.missing_skills,
                matched_skills: data.matched_skills
            })
        })
        .then(res => res.json())
        .then(qData => {
            loadingDiv.classList.add('d-none');
            interviewContainer.classList.remove('d-none');
            
            // Populate Tech Questions
            const techAcc = document.getElementById('techQuestionsAcc');
            qData.technical_questions.forEach((q, i) => {
                techAcc.innerHTML += `
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="headingTech${i}">
                            <button class="accordion-button collapsed fw-semibold" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTech${i}">
                                Q${i+1}: ${q}
                            </button>
                        </h2>
                        <div id="collapseTech${i}" class="accordion-collapse collapse" data-bs-parent="#techQuestionsAcc">
                            <div class="accordion-body">
                                Think about concrete examples from your past experience. If this touches on a missing skill, focus on how you would learn or approach the problem logically.
                            </div>
                        </div>
                    </div>
                `;
            });

            // Populate HR Questions
            const hrAcc = document.getElementById('hrQuestionsAcc');
            qData.hr_questions.forEach((q, i) => {
                hrAcc.innerHTML += `
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="headingHr${i}">
                            <button class="accordion-button collapsed fw-semibold" type="button" data-bs-toggle="collapse" data-bs-target="#collapseHr${i}">
                                Q${i+1}: ${q}
                            </button>
                        </h2>
                        <div id="collapseHr${i}" class="accordion-collapse collapse" data-bs-parent="#hrQuestionsAcc">
                            <div class="accordion-body">
                                Use the STAR method (Situation, Task, Action, Result) to structure your answer. Be honest and show your willingness to grow.
                            </div>
                        </div>
                    </div>
                `;
            });

            // Populate Feedback
            document.getElementById('aiFeedbackText').innerText = qData.ai_feedback;
        })
        .catch(err => {
            loadingDiv.innerHTML = `<h5 class="text-danger">Failed to generate questions: ${err.message}</h5>`;
        });
    }

});
