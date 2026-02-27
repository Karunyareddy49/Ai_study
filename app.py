from flask import Flask, render_template, request, redirect, url_for, jsonify
from google import genai
import json
import os
from urllib.parse import quote, unquote
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, template_folder="templates")

# ===== CREATE FLASK APP WITH EXPLICIT PATHS =====

# --------------------------
# Initialize Gemini client
# --------------------------
api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your_api_key_here":
    print("⚠️  WARNING: GEMINI_API_KEY not set in .env file!")
    print("   Get your API key from: https://makersuite.google.com/app/apikey")
    print("   Add it to the .env file")
    client = None  # Allow app to run but AI features will be disabled
else:
    client = genai.Client(api_key=api_key)

    client = genai.Client(api_key=api_key)

# --------------------------
# Study Schedule Data
# --------------------------
if os.path.exists("study_schedules.json"):
    with open("study_schedules.json", "r") as f:
        study_schedules = json.load(f)
else:
    study_schedules = []

# Exam presets with suggested subjects and duration
EXAM_PRESETS = {
    "GATE": {
        "name": "GATE (Graduate Aptitude Test in Engineering)",
        "subjects": ["Engineering Mathematics", "General Aptitude", "Technical Subject", "Data Structures", "Algorithms"],
        "duration_weeks": 24,
        "description": "Comprehensive preparation for GATE exam"
    },
    "JEE": {
        "name": "JEE (Joint Entrance Examination)",
        "subjects": ["Physics", "Chemistry", "Mathematics"],
        "duration_weeks": 52,
        "description": "Complete JEE Main and Advanced preparation"
    },
    "NEET": {
        "name": "NEET (National Eligibility cum Entrance Test)",
        "subjects": ["Physics", "Chemistry", "Biology (Botany)", "Biology (Zoology)"],
        "duration_weeks": 48,
        "description": "Medical entrance exam preparation"
    },
    "CAT": {
        "name": "CAT (Common Admission Test)",
        "subjects": ["Quantitative Ability", "Verbal Ability", "Data Interpretation", "Logical Reasoning"],
        "duration_weeks": 32,
        "description": "MBA entrance exam preparation"
    },
    "UPSC": {
        "name": "UPSC Civil Services",
        "subjects": ["History", "Geography", "Polity", "Economy", "Science & Technology", "Current Affairs"],
        "duration_weeks": 52,
        "description": "Civil Services examination preparation"
    },
    "Custom": {
        "name": "Custom Exam Preparation",
        "subjects": [],
        "duration_weeks": 12,
        "description": "Create your own study schedule"
    }
}

# --------------------------
# Subjects and pre-written questions (added some common ones)
# --------------------------
subjects = ["Math", "Science", "English", "Electronics"]

questions = {
    "Math": {
        "What is 2+2?": "2+2 = 4",
        "What is 10-3?": "10-3 = 7",
        "What is correlation?": "Correlation measures the relationship between two variables."
    },
    "Science": {
        "What is H2O?": "H2O is water",
        "Which planet is nearest to the sun?": "Mercury",
        "What is Ohm's law?": "Ohm's law states that V = IR, where V is voltage, I is current, and R is resistance."
    },
    "English": {
        "Synonym of happy?": "Joyful",
        "Antonym of fast?": "Slow"
    },
    "Electronics": {
        "What does LED stand for?": "Light Emitting Diode",
        "What is the unit of electric current?": "Ampere"
    }
}

# --------------------------
# AI Cache
# --------------------------
if os.path.exists("ai_cache.json"):
    with open("ai_cache.json", "r") as f:
        ai_cache = json.load(f)
else:
    ai_cache = {}

# --------------------------
# Helper to get answer with subject-aware prompt and logging
# --------------------------

def get_answer(sub, question):
    # Check if AI is available
    if client is None:
        return "AI features are currently unavailable. Please set your GEMINI_API_KEY in the .env file."
    
    # 1. Check pre-written questions
    ans = questions.get(sub, {}).get(question)
    if ans:
        return ans

    # 2. Check cache
    if question in ai_cache:
        return ai_cache[question]

    # 3. Generate AI answer
    try:
        prompt = f"Answer this question in simple terms for a student in {sub}: {question}"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        ans = response.text.strip()
        print(f"AI output for '{question}': {ans}")  # Debug log

        # Save in cache
        ai_cache[question] = ans
        with open("ai_cache.json", "w") as f:
            json.dump(ai_cache, f)

        return ans if ans else "Sorry, AI could not generate an answer."

    except Exception as e:
        print(f"AI generation failed for '{question}': {e}")
        return "Sorry, the answer could not be generated."

# --------------------------
# Study Schedule Helper Functions
# --------------------------
def save_schedules():
    """Save study schedules to JSON file"""
    with open("study_schedules.json", "w") as f:
        json.dump(study_schedules, f, indent=2)

def generate_ai_study_plan(exam_type, subjects, weeks, hours_per_day=4):
    """Generate AI-powered study plan"""
    if client is None:
        return None
    
    try:
        prompt = f"""
Create a detailed {weeks}-week study schedule for {exam_type} exam preparation.
Subjects to cover: {', '.join(subjects)}
Study hours per day: {hours_per_day}

Provide a week-by-week breakdown with:
- Topics to cover each week
- Daily time allocation for each subject
- Revision periods
- Mock test schedules

Format as JSON array with weekly plans:
[
  {{
    "week": 1,
    "focus": "Foundation Building",
    "daily_schedule": {{
      "Monday": {{"subject": "Subject 1", "topics": ["Topic A", "Topic B"], "hours": 4}},
      "Tuesday": {{"subject": "Subject 2", "topics": ["Topic C"], "hours": 4}}
    }}
  }}
]
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        text = response.text.strip()
        start = text.find("[")
        end = text.rfind("]") + 1
        if start != -1 and end > 0:
            return json.loads(text[start:end])
        return None
    except Exception as e:
        print(f"AI study plan generation failed: {e}")
        return None

# --------------------------
# AI MCQs
def generate_ai_mcqs(subject, num_questions=5, difficulty="medium"):
    if client is None:
        # Return fallback questions if AI is not available
        return [
            {
                "question": f"Sample {subject} question {i + 1}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A"
            }
            for i in range(num_questions)
        ]
    
    prompt = f"""
You are an expert exam question setter.

Generate {num_questions} {difficulty} difficulty multiple-choice questions
for a Level 3 quiz on the subject: {subject}.

STRICT RULES:
- EXACTLY 4 options per question
- Answer MUST be one of the options
- No explanations
- No markdown, no backticks
- Output ONLY valid JSON

JSON format:
[
  {{
    "question": "Question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Option A"
  }}
]
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        # --- Safe JSON extraction ---
        start = text.find("[")
        end = text.rfind("]") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON array found in AI output")

        mcqs = json.loads(text[start:end])

        # --- Validation ---
        validated_mcqs = []
        for q in mcqs:
            if (
                isinstance(q, dict)
                and "question" in q
                and "options" in q
                and "answer" in q
                and isinstance(q["options"], list)
                and len(q["options"]) == 4
                and q["answer"] in q["options"]
            ):
                validated_mcqs.append(q)

        if not validated_mcqs:
            raise ValueError("All MCQs failed validation")

        return validated_mcqs

    except Exception as e:
        print("AI MCQs generation failed:", e)

        # --- Guaranteed fallback (never crashes demo) ---
        return [
            {
                "question": f"Sample {subject} question {i + 1}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A"
            }
            for i in range(num_questions)
        ]
# --------------------------
# Routes
# --------------------------

@app.route("/")
def home():
    return render_template("home.html", subjects=subjects)

@app.route("/subject/<sub>")
def subject_page(sub):
    return render_template("subject_page1.html", subject=sub)

@app.route("/subject/<sub>/questions")
def view_questions(sub):
    sub_questions = questions.get(sub, {})
    return render_template(
        "questions.html",
        subject=sub,
        questions=sub_questions
    )
@app.route("/ai")
def ask_ai():
    try:
        if client is None:
            return "<h2>Gemini API not configured. AI features unavailable.</h2>"
        # Example AI call
        response = client.generate_text(prompt="Hello from Smart Study Buddy!")
        return f"<h2>AI Response:</h2><p>{response.text}</p>"
    except Exception as e:
        # Log error
        print("ERROR in /ai route:", e)
        return "<h2>Internal Server Error in AI route</h2>"
@app.route("/subject/<sub>/ask", methods=["GET","POST"])
def ask_ai2(sub):
    answer = None
    question = None

    if request.method == "POST":
        question = request.form["question"]
        answer = get_answer(sub, question)

    return render_template(
        "ask.html",
        subject=sub,
        question=question,
        answer=answer
    )


@app.route("/subject/<sub>/<question>")
def direct_question(sub, question):
    question = unquote(question)
    ans = get_answer(sub, question)
    return render_template("answer.html", subject=sub, question=question, answer=ans)

@app.route("/ai_quiz/<sub>", methods=["GET","POST"])
def ai_quiz(sub):
    if request.method == "POST":
        mcqs_json = request.form.get("mcqs_json","[]")
        try:
            mcqs = json.loads(mcqs_json)
        except:
            mcqs = []

        score = 0
        for i, q in enumerate(mcqs):
            selected = request.form.get(f"q{i}")
            if selected == q.get("answer"):
                score += 1

        return render_template("quiz_result.html", subject=sub, score=score, total=len(mcqs))

    mcqs = generate_ai_mcqs(sub, num_questions=5)
    return render_template("quiz.html", subject=sub, mcqs=mcqs, mcqs_json=json.dumps(mcqs))

# --------------------------
# Study Schedule Routes
# --------------------------

@app.route("/study-schedule")
def study_schedule_home():
    """Main study schedule page"""
    return render_template("study_schedule.html", 
                         schedules=study_schedules, 
                         exam_presets=EXAM_PRESETS)

@app.route("/study-schedule/create", methods=["GET", "POST"])
def create_schedule():
    """Create a new study schedule"""
    if request.method == "POST":
        exam_type = request.form.get("exam_type")
        custom_name = request.form.get("custom_name", "")
        weeks = int(request.form.get("weeks", 12))
        hours_per_day = int(request.form.get("hours_per_day", 4))
        subjects = request.form.getlist("subjects")
        
        # Get preset or use custom
        if exam_type in EXAM_PRESETS and exam_type != "Custom":
            preset = EXAM_PRESETS[exam_type]
            schedule_name = preset["name"]
            if not subjects:
                subjects = preset["subjects"]
        else:
            schedule_name = custom_name or "Custom Study Plan"
        
        # Create schedule
        schedule = {
            "id": len(study_schedules) + 1,
            "name": schedule_name,
            "exam_type": exam_type,
            "subjects": subjects,
            "weeks": weeks,
            "hours_per_day": hours_per_day,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "start_date": request.form.get("start_date", datetime.now().strftime("%Y-%m-%d")),
            "status": "active"
        }
        
        # Try to generate AI study plan
        ai_plan = generate_ai_study_plan(exam_type, subjects, weeks, hours_per_day)
        if ai_plan:
            schedule["ai_plan"] = ai_plan
        
        study_schedules.append(schedule)
        save_schedules()
        
        return redirect(url_for("view_schedule", schedule_id=schedule["id"]))
    
    # Pass today's date to the template
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("create_schedule.html", exam_presets=EXAM_PRESETS, today=today)

@app.route("/study-schedule/<int:schedule_id>")
def view_schedule(schedule_id):
    """View a specific study schedule"""
    schedule = next((s for s in study_schedules if s["id"] == schedule_id), None)
    if not schedule:
        return "Schedule not found", 404
    
    # Calculate progress
    start_date = datetime.strptime(schedule["start_date"], "%Y-%m-%d")
    current_date = datetime.now()
    days_elapsed = (current_date - start_date).days
    current_week = min(days_elapsed // 7 + 1, schedule["weeks"])
    progress = min((current_week / schedule["weeks"]) * 100, 100)
    
    schedule["current_week"] = current_week
    schedule["progress"] = round(progress, 1)
    
    return render_template("view_schedule.html", schedule=schedule)

@app.route("/study-schedule/<int:schedule_id>/delete", methods=["POST"])
def delete_schedule(schedule_id):
    """Delete a study schedule"""
    global study_schedules
    study_schedules = [s for s in study_schedules if s["id"] != schedule_id]
    save_schedules()
    return redirect(url_for("study_schedule_home"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html",
                           code=404,
                           message="Page not found 😕"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template("error.html",
                           code=500,
                           message="Something went wrong on our side 😓 Please try again."), 500
# --------------------------
# Run app
# --------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)