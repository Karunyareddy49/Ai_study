# Smart Study Buddy - Complete Code Documentation

## 📚 Table of Contents
1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Installation & Setup](#installation--setup)
4. [Understanding the Code](#understanding-the-code)
5. [How Features Work](#how-features-work)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)

---

## 📖 Project Overview

**Smart Study Buddy** is a Flask-based web application that helps students:
- Ask questions and get AI-powered answers
- Take AI-generated quizzes
- Create personalized study schedules for exams (GATE, JEE, NEET, etc.)
- Track study progress with visual progress bars

**Technologies Used:**
- **Backend:** Python, Flask
- **AI:** Google Gemini AI (gemini-2.5-flash)
- **Frontend:** HTML5, CSS3, JavaScript
- **Storage:** JSON files (lightweight database)

---

## 📁 Project Structure

```
smart-study-buddy/
├── app.py                      # Main Flask application (backend logic)
├── .env                        # Environment variables (API key storage)
├── requirements.txt            # Python dependencies
├── ai_cache.json              # Cache for AI responses
├── study_schedules.json       # Stores created study schedules
├── style.css                  # Additional styling
├── templates/                 # HTML pages (frontend)
│   ├── home.html              # Homepage with subject cards
│   ├── study_schedule.html    # Study schedule dashboard
│   ├── create_schedule.html   # Create new schedule form
│   ├── view_schedule.html     # View schedule details
│   ├── subject_page1.html     # Subject-specific page
│   ├── questions.html         # Pre-written questions
│   ├── ask.html               # Ask AI questions
│   ├── answer.html            # Display answers
│   ├── quiz.html              # Quiz interface
│   ├── quiz_result.html       # Quiz results
│   └── error.html             # Error pages
└── README.md                  # This documentation file
```

---

## 🚀 Installation & Setup

### Step 1: Prerequisites
- Python 3.7 or higher installed
- Internet connection (for AI features)

### Step 2: Install Dependencies
```bash
# Navigate to project directory
cd smart-study-buddy

# Install required packages
py -m pip install -r requirements.txt
```

**Packages installed:**
- Flask - Web framework
- google-genai - Google Gemini AI client
- python-dotenv - Environment variable management
- Jinja2 - Template engine
- Werkzeug - WSGI utilities

### Step 3: Get Gemini API Key (Optional but Recommended)
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy your API key

### Step 4: Configure API Key
Open `.env` file and add your key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### Step 5: Run the Application
```bash
py app.py
```

Application will start at: `http://127.0.0.1:5000`

---

## 💻 Understanding the Code

### 1. app.py - Main Application File

#### **Imports & Configuration**

```python
from flask import Flask, render_template, request, redirect, url_for, jsonify
from google import genai
import json
import os
from urllib.parse import quote, unquote
from datetime import datetime, timedelta
from dotenv import load_dotenv
```

**What each import does:**

| Import | Purpose |
|--------|---------|
| `Flask` | Creates the web application |
| `render_template` | Displays HTML pages to users |
| `request` | Accesses form data submitted by users |
| `redirect, url_for` | Navigates between pages |
| `jsonify` | Converts Python data to JSON format |
| `genai` | Connects to Google Gemini AI |
| `json` | Reads/writes JSON files |
| `datetime` | Handles dates and times |
| `load_dotenv` | Loads environment variables from .env |

#### **App Initialization**

```python
# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__, template_folder="templates")

# Initialize Gemini AI client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your_api_key_here":
    print("⚠️  WARNING: GEMINI_API_KEY not set in .env file!")
    client = None  # App runs without AI features
else:
    client = genai.Client(api_key=api_key)
```

**How it works:**
1. Loads `.env` file to get API key
2. Creates Flask application instance
3. Checks if API key exists:
   - **No key** → App runs, but AI features disabled
   - **Key exists** → Connects to Gemini AI

#### **Data Storage Setup**

```python
# Study Schedule Data
if os.path.exists("study_schedules.json"):
    with open("study_schedules.json", "r") as f:
        study_schedules = json.load(f)
else:
    study_schedules = []

# AI Cache
if os.path.exists("ai_cache.json"):
    with open("ai_cache.json", "r") as f:
        ai_cache = json.load(f)
else:
    ai_cache = {}
```

**Purpose:**
- Loads previously saved schedules and AI responses
- Creates empty storage if files don't exist
- Provides persistence across app restarts

### 2. Routes (URL Mapping)

#### **Homepage Route**

```python
@app.route("/")
def home():
    return render_template("home.html", subjects=subjects)
```

**Flow:**
1. User visits `http://127.0.0.1:5000/`
2. Flask calls `home()` function
3. Renders `home.html` template
4. Passes `subjects` list to template

#### **Subject Page Route**

```python
@app.route("/subject/<sub>")
def subject_page(sub):
    return render_template("subject_page1.html", subject=sub)
```

**Flow:**
1. User visits `/subject/Math`
2. `<sub>` captures "Math" as a variable
3. Shows subject page for Math

#### **Ask AI Route**

```python
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
```

**Flow:**
- **GET request** → Shows the question form
- **POST request** → 
  1. Gets question from form
  2. Calls `get_answer()` to get AI response
  3. Displays answer on page

#### **AI Answer Generation**

```python
def get_answer(sub, question):
    # Check if AI is available
    if client is None:
        return "AI features unavailable. Please set GEMINI_API_KEY."
    
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

        # Save in cache
        ai_cache[question] = ans
        with open("ai_cache.json", "w") as f:
            json.dump(ai_cache, f)

        return ans
    except Exception as e:
        print(f"AI generation failed: {e}")
        return "Sorry, the answer could not be generated."
```

**Three-tier answer system:**
1. **Pre-written answers** → Fastest, no AI needed
2. **Cached answers** → Previous AI responses
3. **New AI generation** → Calls Gemini AI for new questions

### 3. Study Schedule Feature

#### **Exam Presets Configuration**

```python
EXAM_PRESETS = {
    "GATE": {
        "name": "GATE (Graduate Aptitude Test in Engineering)",
        "subjects": ["Engineering Mathematics", "General Aptitude", 
                    "Technical Subject", "Data Structures", "Algorithms"],
        "duration_weeks": 24,
        "description": "Comprehensive preparation for GATE exam"
    },
    "JEE": {
        "name": "JEE (Joint Entrance Examination)",
        "subjects": ["Physics", "Chemistry", "Mathematics"],
        "duration_weeks": 52,
        "description": "Complete JEE Main and Advanced preparation"
    },
    # ... more presets
}
```

**Purpose:** 
- Pre-configured study plans for popular exams
- Default subjects and durations
- Easy customization for students

#### **Study Schedule Routes**

##### View All Schedules

```python
@app.route("/study-schedule")
def study_schedule_home():
    """Main study schedule page"""
    return render_template("study_schedule.html", 
                         schedules=study_schedules, 
                         exam_presets=EXAM_PRESETS)
```

**Shows:**
- List of all created schedules
- Exam preset cards
- Create new schedule button

##### Create New Schedule

```python
@app.route("/study-schedule/create", methods=["GET", "POST"])
def create_schedule():
    """Create a new study schedule"""
    if request.method == "POST":
        # Get form data
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
        
        # Create schedule dictionary
        schedule = {
            "id": len(study_schedules) + 1,
            "name": schedule_name,
            "exam_type": exam_type,
            "subjects": subjects,
            "weeks": weeks,
            "hours_per_day": hours_per_day,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "start_date": request.form.get("start_date"),
            "status": "active"
        }
        
        # Try to generate AI study plan
        ai_plan = generate_ai_study_plan(exam_type, subjects, weeks, hours_per_day)
        if ai_plan:
            schedule["ai_plan"] = ai_plan
        
        # Save schedule
        study_schedules.append(schedule)
        save_schedules()
        
        return redirect(url_for("view_schedule", schedule_id=schedule["id"]))
    
    # GET request - show form
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("create_schedule.html", 
                         exam_presets=EXAM_PRESETS, 
                         today=today)
```

**Step-by-step flow:**

1. **GET Request (show form):**
   - User visits `/study-schedule/create`
   - Displays form with exam presets
   - Pre-fills today's date

2. **POST Request (form submission):**
   - Gets all form data (exam type, weeks, subjects, etc.)
   - Checks if using preset or custom
   - Creates schedule dictionary with all details
   - Attempts to generate AI study plan
   - Saves to JSON file
   - Redirects to view the new schedule

##### View Schedule Details

```python
@app.route("/study-schedule/<int:schedule_id>")
def view_schedule(schedule_id):
    """View a specific study schedule"""
    # Find schedule by ID
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
```

**Progress Calculation:**
```
Days Elapsed = Today - Start Date
Current Week = Days Elapsed ÷ 7 + 1
Progress % = (Current Week ÷ Total Weeks) × 100
```

**Example:**
- Start date: Feb 1, 2026
- Today: Feb 27, 2026
- Days elapsed: 26 days
- Current week: 26 ÷ 7 + 1 = 4.7 → Week 5
- Progress: (5 ÷ 24) × 100 = 20.8%

#### **AI Study Plan Generation**

```python
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
```

**How AI plan works:**
1. Sends detailed prompt to Gemini AI
2. AI generates week-by-week study plan
3. Extracts JSON from AI response
4. Returns structured data with daily topics
5. If fails, returns None (app shows generic plan)

### 4. Quiz Generation

```python
def generate_ai_mcqs(subject, num_questions=5, difficulty="medium"):
    if client is None:
        # Return fallback questions if AI unavailable
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
        start = text.find("[")
        end = text.rfind("]") + 1
        
        if start == -1 or end == 0:
            raise ValueError("No JSON array found")

        mcqs = json.loads(text[start:end])

        # Validate each question
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
        return fallback_questions
```

**Validation checks:**
1. Must be a dictionary
2. Must have "question", "options", "answer" keys
3. Must have exactly 4 options
4. Answer must be one of the options

---

## 🎨 Frontend Templates (HTML)

### Jinja2 Template Syntax

#### **Variables**
```html
<h1>{{ schedule.name }}</h1>
<!-- Outputs: GATE Preparation -->
```

#### **Loops**
```html
{% for subject in subjects %}
  <div>{{ subject }}</div>
{% endfor %}

<!-- Outputs:
<div>Math</div>
<div>Science</div>
<div>English</div>
-->
```

#### **Conditionals**
```html
{% if client %}
  <p>AI features enabled!</p>
{% else %}
  <p>AI features disabled</p>
{% endif %}
```

#### **URL Generation**
```html
<a href="{{ url_for('subject_page', sub='Math') }}">Math</a>
<!-- Generates: /subject/Math -->
```

### Template Examples

#### home.html - Homepage
```html
<div class="container">
    <!-- Study Schedule Card -->
    <a class="card" href="/study-schedule">
        <div class="icon">📚</div>
        <div class="title">Study Schedule</div>
        <p>Plan Your Exam Prep</p>
    </a>

    <!-- Subject Cards -->
    {% for sub in subjects %}
    <a class="card" href="{{ url_for('subject_page', sub=sub) }}">
        <div class="icon">{{ icons[loop.index0 % icons|length] }}</div>
        <div class="title">{{ sub }}</div>
        <p>AI Questions & Quizzes</p>
    </a>
    {% endfor %}
</div>
```

#### create_schedule.html - Form with JavaScript

**Form Handling:**
```html
<form method="POST" id="scheduleForm">
    <div class="form-group">
        <label>Select Exam Type</label>
        <div class="preset-selector">
            {% for key, preset in exam_presets.items() %}
            <label class="preset-option" data-preset="{{ key }}">
                <input type="radio" name="exam_type" value="{{ key }}" 
                       onchange="handlePresetChange('{{ key }}')">
                <h3>{{ preset.name.split('(')[0] }}</h3>
                <p>{{ preset.duration_weeks }} weeks</p>
            </label>
            {% endfor %}
        </div>
    </div>

    <div class="form-group">
        <label for="start_date">Start Date</label>
        <input type="date" id="start_date" name="start_date" 
               value="{{ today }}" required>
    </div>

    <button type="submit">🚀 Create Schedule</button>
</form>
```

**JavaScript for Dynamic Subjects:**
```javascript
function addSubject() {
    const input = document.getElementById('newSubject');
    const subject = input.value.trim();
    
    if (subject) {
        addSubjectTag(subject);
        input.value = '';
    }
}

function addSubjectTag(subject) {
    const subjectsList = document.getElementById('subjectsList');
    const tag = document.createElement('div');
    tag.innerHTML = `
        <input type="hidden" name="subjects" value="${subject}">
        <span>${subject}</span>
        <button type="button" onclick="this.parentElement.remove()">×</button>
    `;
    subjectsList.appendChild(tag);
}
```

#### view_schedule.html - Progress Display

**Progress Bar:**
```html
<div class="progress-section">
    <div class="progress-header">
        <h2>📈 Your Progress</h2>
        <span class="progress-percentage">{{ schedule.progress }}%</span>
    </div>
    <div class="progress-bar">
        <div class="progress-fill" style="width: {{ schedule.progress }}%;">
            Week {{ schedule.current_week }}
        </div>
    </div>
    <div class="progress-details">
        <span>Week {{ schedule.current_week }} of {{ schedule.weeks }}</span>
        <span>{{ schedule.weeks - schedule.current_week }} weeks remaining</span>
    </div>
</div>
```

**Weekly Plan Tabs:**
```html
<div class="weekly-plan">
    <h2>📅 Weekly Study Plan</h2>
    
    {% if schedule.ai_plan %}
        <!-- Week tabs -->
        <div class="week-tabs">
            {% for week_plan in schedule.ai_plan[:8] %}
            <button class="week-tab {% if loop.first %}active{% endif %}" 
                    onclick="showWeek({{ loop.index0 }})">
                Week {{ week_plan.week }}
            </button>
            {% endfor %}
        </div>

        <!-- Week content -->
        {% for week_plan in schedule.ai_plan[:8] %}
        <div class="week-content {% if loop.first %}active{% endif %}" 
             id="week{{ loop.index0 }}">
            <h3>{{ week_plan.focus }}</h3>
            
            {% for day, plan in week_plan.daily_schedule.items() %}
            <div class="day-card">
                <h3>{{ day }}</h3>
                <p>{{ plan.subject }} - {{ plan.hours }}h</p>
                <ul>
                    {% for topic in plan.topics %}
                    <li>{{ topic }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </div>
        {% endfor %}
    {% endif %}
</div>

<script>
function showWeek(weekIndex) {
    // Hide all weeks
    document.querySelectorAll('.week-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Show selected week
    document.getElementById('week' + weekIndex).classList.add('active');
}
</script>
```

---

## 🔄 Complete User Flow Examples

### Example 1: Creating a GATE Study Schedule

**Step 1: User Action**
- User clicks "Study Schedule" on homepage
- Browser requests: `GET /study-schedule`

**Step 2: Server Response**
```python
@app.route("/study-schedule")
def study_schedule_home():
    return render_template("study_schedule.html", 
                         schedules=study_schedules,
                         exam_presets=EXAM_PRESETS)
```
- Loads all existing schedules
- Passes exam presets to template
- Renders study schedule dashboard

**Step 3: User Clicks "Create New Schedule"**
- Browser requests: `GET /study-schedule/create`

**Step 4: Server Shows Form**
```python
@app.route("/study-schedule/create", methods=["GET", "POST"])
def create_schedule():
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("create_schedule.html", 
                         exam_presets=EXAM_PRESETS,
                         today=today)
```
- Shows form with exam presets
- Pre-fills today's date

**Step 5: User Fills Form**
- Selects: GATE
- Weeks: 24
- Hours/day: 4
- Subjects: Auto-filled from GATE preset
- Start date: Today

**Step 6: User Submits Form**
- Browser sends: `POST /study-schedule/create` with form data

**Step 7: Server Processes**
```python
if request.method == "POST":
    # Extract data
    exam_type = "GATE"
    weeks = 24
    subjects = ["Math", "Data Structures", ...]
    
    # Create schedule
    schedule = {
        "id": 1,
        "name": "GATE Preparation",
        "subjects": subjects,
        "weeks": 24,
        ...
    }
    
    # Generate AI plan
    ai_plan = generate_ai_study_plan("GATE", subjects, 24, 4)
    schedule["ai_plan"] = ai_plan
    
    # Save
    study_schedules.append(schedule)
    save_schedules()
    
    # Redirect
    return redirect(url_for("view_schedule", schedule_id=1))
```

**Step 8: View Schedule**
- Browser redirects to: `/study-schedule/1`
- Shows schedule with progress bar, subjects, weekly plan

### Example 2: Taking a Quiz

**Step 1: User clicks "Math" subject**
- Request: `GET /subject/Math`
- Shows Math subject page

**Step 2: User clicks "Take Quiz"**
- Request: `GET /ai_quiz/Math`

**Step 3: Server generates questions**
```python
@app.route("/ai_quiz/<sub>", methods=["GET","POST"])
def ai_quiz(sub):
    mcqs = generate_ai_mcqs(sub, num_questions=5)
    return render_template("quiz.html", 
                         subject=sub, 
                         mcqs=mcqs,
                         mcqs_json=json.dumps(mcqs))
```
- Calls AI to generate 5 MCQs
- Displays quiz form

**Step 4: User answers questions**
- Selects answers for all 5 questions
- Clicks "Submit Quiz"

**Step 5: Server calculates score**
```python
if request.method == "POST":
    score = 0
    for i, q in enumerate(mcqs):
        selected = request.form.get(f"q{i}")
        if selected == q.get("answer"):
            score += 1
    
    return render_template("quiz_result.html", 
                         subject=sub, 
                         score=score, 
                         total=5)
```
- Compares user answers with correct answers
- Shows result page: "You scored 4 out of 5!"

---

## 📊 Data Flow Diagram

```
User Browser
    ↓ HTTP Request
Flask App (app.py)
    ↓ Query
JSON Files (study_schedules.json, ai_cache.json)
    ↓ Data
Flask App
    ↓ (if needed) API Call
Google Gemini AI
    ↓ AI Response
Flask App
    ↓ Render
HTML Template (Jinja2)
    ↓ HTTP Response
User Browser
```

---

## 🔧 API Reference

### Routes Summary

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Homepage with subjects |
| `/subject/<sub>` | GET | Subject page |
| `/subject/<sub>/questions` | GET | View pre-written questions |
| `/subject/<sub>/ask` | GET, POST | Ask AI questions |
| `/subject/<sub>/<question>` | GET | Direct question answer |
| `/ai_quiz/<sub>` | GET, POST | Take/submit quiz |
| `/study-schedule` | GET | Study schedule dashboard |
| `/study-schedule/create` | GET, POST | Create schedule form |
| `/study-schedule/<id>` | GET | View schedule details |
| `/study-schedule/<id>/delete` | POST | Delete schedule |

### Helper Functions

#### get_answer(subject, question)
```python
def get_answer(sub, question):
    """
    Gets answer for a question using 3-tier system:
    1. Pre-written answers
    2. Cached AI answers
    3. New AI generation
    
    Args:
        sub (str): Subject name
        question (str): Question text
    
    Returns:
        str: Answer text
    """
```

#### generate_ai_mcqs(subject, num_questions, difficulty)
```python
def generate_ai_mcqs(subject, num_questions=5, difficulty="medium"):
    """
    Generates multiple choice questions using AI
    
    Args:
        subject (str): Subject name
        num_questions (int): Number of questions to generate
        difficulty (str): "easy", "medium", or "hard"
    
    Returns:
        list: Array of MCQ dictionaries with question, options, answer
    """
```

#### generate_ai_study_plan(exam_type, subjects, weeks, hours_per_day)
```python
def generate_ai_study_plan(exam_type, subjects, weeks, hours_per_day=4):
    """
    Generates AI-powered weekly study plan
    
    Args:
        exam_type (str): Type of exam (GATE, JEE, etc.)
        subjects (list): List of subjects to cover
        weeks (int): Duration in weeks
        hours_per_day (int): Daily study hours
    
    Returns:
        list: Array of weekly plan dictionaries or None if failed
    """
```

#### save_schedules()
```python
def save_schedules():
    """
    Saves study schedules to study_schedules.json file
    Called after creating or deleting schedules
    """
    with open("study_schedules.json", "w") as f:
        json.dump(study_schedules, f, indent=2)
```

---

## 🎨 CSS Styling Guide

### Color Scheme

```css
/* Primary Colors */
--primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--card-gradient: linear-gradient(135deg, #6A82FB, #FC5C7D);

/* Neutral Colors */
--text-dark: #2d3748;
--text-light: #718096;
--background-light: #f7fafc;
--border-color: #e2e8f0;

/* Accent Colors */
--accent-blue: #667eea;
--accent-purple: #764ba2;
--accent-red: #FC5C7D;
```

### Responsive Design

```css
/* Desktop */
@media (min-width: 1024px) {
    .container {
        max-width: 1200px;
    }
}

/* Tablet */
@media (max-width: 768px) {
    .schedules-grid {
        grid-template-columns: 1fr;
    }
}

/* Mobile */
@media (max-width: 480px) {
    header h1 {
        font-size: 1.5rem;
    }
}
```

---

## 🐛 Troubleshooting

### Problem 1: App won't start
```
Error: ModuleNotFoundError: No module named 'flask'
```
**Solution:**
```bash
py -m pip install -r requirements.txt
```

### Problem 2: AI features not working
```
Warning: GEMINI_API_KEY not set in .env file!
```
**Solution:**
1. Get API key from https://makersuite.google.com/app/apikey
2. Open `.env` file
3. Replace `your_api_key_here` with actual key
4. Restart app

### Problem 3: 500 Internal Server Error when creating schedule
**Solution:** Check terminal for error message. Common causes:
- Invalid date format
- Missing form fields
- JSON encoding error

**Fix:** Ensure all required fields filled in form

### Problem 4: Schedules not saving
**Solution:**
- Check file permissions for `study_schedules.json`
- Ensure app has write permissions in directory

### Problem 5: Port already in use
```
Error: Address already in use
```
**Solution:**
```bash
# Kill process on port 5000
# Windows PowerShell:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in app.py:
app.run(host="0.0.0.0", port=5001)
```

---

## 🚀 Future Enhancement Ideas

### 1. User Authentication
- Login/signup system
- Individual user accounts
- Personal schedule storage

### 2. Database Integration
- Replace JSON with SQLite or PostgreSQL
- Better data management
- Faster queries

### 3. Advanced Analytics
- Study time tracking
- Performance graphs
- Progress predictions

### 4. Mobile App
- React Native or Flutter
- Push notifications for study reminders
- Offline mode

### 5. Collaboration Features
- Share schedules with friends
- Study groups
- Discussion forums

### 6. More AI Features
- Personalized recommendations
- Adaptive difficulty
- Voice-based questions

---

## 📝 Code Best Practices Used

### 1. Error Handling
```python
try:
    # Attempt AI generation
    response = client.models.generate_content(...)
except Exception as e:
    # Graceful fallback
    print(f"Error: {e}")
    return default_value
```

### 2. Code Organization
- Separate concerns (routes, helpers, data)
- Clear function names
- Comprehensive comments

### 3. Data Validation
```python
# Validate MCQ format
if (isinstance(q, dict) and 
    "question" in q and 
    len(q["options"]) == 4):
    validated_mcqs.append(q)
```

### 4. Security
- Environment variables for API keys
- No hardcoded secrets
- Input validation on forms

### 5. User Experience
- Graceful degradation (app works without AI)
- Loading states
- Clear error messages

---

## 📚 Learning Resources

### Flask Documentation
- Official docs: https://flask.palletsprojects.com/
- Tutorial: https://flask.palletsprojects.com/tutorial/

### Jinja2 Templates
- Documentation: https://jinja.palletsprojects.com/
- Template Designer: https://jinja.palletsprojects.com/templates/

### Google Gemini AI
- AI Studio: https://makersuite.google.com/
- API Docs: https://ai.google.dev/docs

### Python Best Practices
- PEP 8 Style Guide: https://pep8.org/
- Real Python: https://realpython.com/

---

## 📄 License & Credits

**Smart Study Buddy**
- Built with Flask & Gemini AI
- Educational purpose
- Open for learning and modification

---

## 🎯 Summary

This application demonstrates:
✅ Flask web framework basics
✅ REST API design
✅ AI integration (Gemini)
✅ Template rendering (Jinja2)
✅ Data persistence (JSON)
✅ Form handling
✅ Progress tracking
✅ Responsive design

**Key Takeaways:**
1. Flask makes web development simple
2. AI can enhance user experience
3. Good UX works even when features fail
4. JSON works great for small-scale storage
5. Templates separate logic from presentation

---

**Last Updated:** February 27, 2026
**Version:** 1.0
**Author:** Smart Study Buddy Team
