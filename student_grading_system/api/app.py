"""
COLLEGE STUDENT GRADE CALCULATOR - CREDIT SYSTEM
==================================================
A Flask-based web application for calculating SGPA with:
- Credit-based grading system
- 10-point grade scale
- Automatic SGPA calculation

HOW TO RUN:
1. Install Flask: pip install flask
2. Run: python app.py
3. Open browser: http://127.0.0.1:5000
"""

from flask import Flask, render_template, request, jsonify
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))

# Storage path handling for Vercel / serverless environment
TMP_DATA_FILE = os.path.join('/tmp', 'students_data.json') if os.path.exists('/tmp') else None
ROOT_DATA_FILE = os.path.join(BASE_DIR, 'students_data.json')

# Subject list with credits
SUBJECTS = [
    {"name": "Operating System", "credits": 4},
    {"name": "Computer Organization & Architecture", "credits": 4},
    {"name": "Python Programming", "credits": 3},
    {"name": "OOPS in Java", "credits": 3},
    {"name": "Data Structures & Algorithms", "credits": 4},
    {"name": "Design Thinking", "credits": 2}
]

SUBJECT_NAMES = [s["name"] for s in SUBJECTS]

# Grade mapping
GRADE_MAP = {
    'A': {'min': 90, 'max': 100, 'points': 10, 'label': 'Excellent'},
    'B': {'min': 80, 'max': 89, 'points': 9, 'label': 'Very Good'},
    'C': {'min': 70, 'max': 79, 'points': 8, 'label': 'Good'},
    'D': {'min': 60, 'max': 69, 'points': 7, 'label': 'Above Average'},
    'E': {'min': 50, 'max': 59, 'points': 6, 'label': 'Average'},
    'P': {'min': 40, 'max': 49, 'points': 5, 'label': 'Pass'},
    'F': {'min': 0, 'max': 39, 'points': 0, 'label': 'Fail'}
}

# ============================================================
# DATA MANAGEMENT
# ============================================================

def create_sample_data():
    """Create sample student data"""
    return {
        "students": [
            {
                "id": 1,
                "name": "Alice Johnson",
                "roll_no": "CS2024001",
                "semester": "Fall 2024",
                "subjects": {
                    "Operating System": {"marks": 92, "credits": 4},
                    "Computer Organization & Architecture": {"marks": 85, "credits": 4},
                    "Python Programming": {"marks": 78, "credits": 3},
                    "OOPS in Java": {"marks": 88, "credits": 3},
                    "Data Structures & Algorithms": {"marks": 90, "credits": 4},
                    "Design Thinking": {"marks": 95, "credits": 2}
                }
            },
            {
                "id": 2,
                "name": "Bob Smith",
                "roll_no": "CS2024002",
                "semester": "Fall 2024",
                "subjects": {
                    "Operating System": {"marks": 65, "credits": 4},
                    "Computer Organization & Architecture": {"marks": 70, "credits": 4},
                    "Python Programming": {"marks": 55, "credits": 3},
                    "OOPS in Java": {"marks": 60, "credits": 3},
                    "Data Structures & Algorithms": {"marks": 68, "credits": 4},
                    "Design Thinking": {"marks": 72, "credits": 2}
                }
            },
            {
                "id": 3,
                "name": "Carol Davis",
                "roll_no": "CS2024003",
                "semester": "Fall 2024",
                "subjects": {
                    "Operating System": {"marks": 45, "credits": 4},
                    "Computer Organization & Architecture": {"marks": 38, "credits": 4},
                    "Python Programming": {"marks": 52, "credits": 3},
                    "OOPS in Java": {"marks": 48, "credits": 3},
                    "Data Structures & Algorithms": {"marks": 42, "credits": 4},
                    "Design Thinking": {"marks": 55, "credits": 2}
                }
            }
        ],
        "next_id": 4
    }

def get_data_filepath():
    """Get readable data filepath for serverless or local environments."""
    if TMP_DATA_FILE and os.path.exists(TMP_DATA_FILE):
        return TMP_DATA_FILE
    if os.path.exists(ROOT_DATA_FILE):
        return ROOT_DATA_FILE
    return None

def load_students():
    """Load student data from JSON file. Create new if doesn't exist."""
    filepath = get_data_filepath()
    if not filepath:
        data = create_sample_data()
        save_students(data)
        return data
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except Exception:
        data = create_sample_data()
        save_students(data)
        return data

def save_students(data):
    """Save student data to JSON file."""
    filepath = TMP_DATA_FILE if TMP_DATA_FILE else ROOT_DATA_FILE
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    except OSError:
        if TMP_DATA_FILE and filepath != TMP_DATA_FILE:
            try:
                with open(TMP_DATA_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass

def get_grade(marks):
    """Get grade, grade points, and label based on marks."""
    for grade, info in GRADE_MAP.items():
        if info['min'] <= marks <= info['max']:
            return grade, info['points'], info['label']
    return "F", 0, "Fail"

def calculate_sgpa(subjects):
    """Calculate SGPA from subject marks and credits."""
    if not subjects:
        return 0, "N/A", "No Data", 0, 0, []
    
    total_points = 0
    total_credits = 0
    earned_credits = 0
    failed_subjects = []
    
    for subject_name, subject_data in subjects.items():
        # Handle both formats
        if isinstance(subject_data, dict):
            marks = subject_data.get('marks', 0)
            credits = subject_data.get('credits', 0)
        else:
            # Old format: just marks
            marks = subject_data
            credits = 3  # default
        
        grade, points, label = get_grade(marks)
        total_points += points * credits
        total_credits += credits
        
        if grade != 'F':
            earned_credits += credits
        else:
            failed_subjects.append(subject_name)
    
    sgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0
    
    # Determine overall grade based on SGPA
    if sgpa >= 9.0:
        overall_grade = "A+"
        status = "Excellent"
    elif sgpa >= 8.0:
        overall_grade = "A"
        status = "Very Good"
    elif sgpa >= 7.0:
        overall_grade = "B+"
        status = "Good"
    elif sgpa >= 6.0:
        overall_grade = "B"
        status = "Satisfactory"
    elif sgpa >= 5.0:
        overall_grade = "C"
        status = "Average"
    elif sgpa >= 4.0:
        overall_grade = "D"
        status = "Below Average"
    else:
        overall_grade = "F"
        status = "Needs Improvement"
    
    return sgpa, overall_grade, status, total_credits, earned_credits, failed_subjects

def get_subject_averages(students):
    """Calculate average marks for each subject."""
    subject_totals = {s["name"]: 0 for s in SUBJECTS}
    subject_counts = {s["name"]: 0 for s in SUBJECTS}
    
    for student in students:
        for subj_name, subj_data in student.get('subjects', {}).items():
            if subj_name in subject_totals:
                if isinstance(subj_data, dict):
                    marks = subj_data.get('marks', 0)
                else:
                    marks = subj_data
                subject_totals[subj_name] += marks
                subject_counts[subj_name] += 1
    
    averages = {}
    for subj in subject_totals:
        if subject_counts[subj] > 0:
            averages[subj] = round(subject_totals[subj] / subject_counts[subj], 1)
        else:
            averages[subj] = 0
    
    return averages

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    """Main page - displays the grading dashboard."""
    data = load_students()
    students = data.get('students', [])
    
    # Calculate statistics for each student
    student_performance = []
    for student in students:
        sgpa, grade, status, total_credits, earned_credits, failed = calculate_sgpa(student.get('subjects', {}))
        student_performance.append({
            'id': student.get('id', 0),
            'name': student.get('name', 'Unknown'),
            'roll_no': student.get('roll_no', 'N/A'),
            'semester': student.get('semester', 'N/A'),
            'sgpa': sgpa,
            'grade': grade,
            'status': status,
            'total_credits': total_credits,
            'earned_credits': earned_credits,
            'failed_subjects': failed,
            'subjects': student.get('subjects', {})
        })
    
    # Statistics
    total_students = len(students)
    all_sgpas = [p['sgpa'] for p in student_performance if p['sgpa'] > 0]
    avg_sgpa = round(sum(all_sgpas) / len(all_sgpas), 2) if all_sgpas else 0
    
    # Top performer
    top_student = max(student_performance, key=lambda x: x['sgpa']) if student_performance and any(p['sgpa'] > 0 for p in student_performance) else None
    
    # Needs improvement
    needs_improvement = len([p for p in student_performance if p['sgpa'] < 4.0 and p['sgpa'] > 0])
    
    # Subject averages
    subject_avg = get_subject_averages(students)
    
    return render_template('index.html',
                         students=student_performance,
                         total_students=total_students,
                         avg_sgpa=avg_sgpa,
                         top_student=top_student,
                         needs_improvement=needs_improvement,
                         subject_avg=subject_avg,
                         subjects=SUBJECTS,
                         grade_map=GRADE_MAP)

@app.route('/add', methods=['POST'])
def add_student():
    """Add a new student."""
    data = load_students()
    
    name = request.form.get('name')
    roll_no = request.form.get('roll_no')
    semester = request.form.get('semester')
    
    # Get subject marks
    subjects = {}
    for subj in SUBJECT_NAMES:
        marks = request.form.get(f'marks_{subj}')
        credits = next((s["credits"] for s in SUBJECTS if s["name"] == subj), 0)
        subjects[subj] = {"marks": int(marks) if marks else 0, "credits": credits}
    
    new_student = {
        "id": data.get('next_id', 1),
        "name": name,
        "roll_no": roll_no,
        "semester": semester,
        "subjects": subjects
    }
    
    data['students'].append(new_student)
    data['next_id'] = data.get('next_id', 1) + 1
    
    save_students(data)
    return jsonify({"success": True, "student": new_student})

@app.route('/delete/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student."""
    data = load_students()
    data['students'] = [s for s in data['students'] if s.get('id') != student_id]
    save_students(data)
    return jsonify({"success": True})

@app.route('/edit/<int:student_id>', methods=['PUT'])
def edit_student(student_id):
    """Edit a student."""
    data = load_students()
    
    for student in data['students']:
        if student.get('id') == student_id:
            student['name'] = request.form.get('name')
            student['roll_no'] = request.form.get('roll_no')
            student['semester'] = request.form.get('semester')
            
            for subj in SUBJECT_NAMES:
                marks = request.form.get(f'marks_{subj}')
                if marks:
                    if subj in student['subjects']:
                        if isinstance(student['subjects'][subj], dict):
                            student['subjects'][subj]['marks'] = int(marks)
                        else:
                            student['subjects'][subj] = {"marks": int(marks), "credits": next((s["credits"] for s in SUBJECTS if s["name"] == subj), 0)}
                    else:
                        student['subjects'][subj] = {"marks": int(marks), "credits": next((s["credits"] for s in SUBJECTS if s["name"] == subj), 0)}
            break
    
    save_students(data)
    return jsonify({"success": True})

@app.route('/stats')
def get_stats():
    """API endpoint for statistics."""
    data = load_students()
    students = data.get('students', [])
    
    performance = []
    for student in students:
        sgpa, grade, status, total_credits, earned_credits, failed = calculate_sgpa(student.get('subjects', {}))
        performance.append({
            'id': student.get('id', 0),
            'name': student.get('name', 'Unknown'),
            'sgpa': sgpa,
            'grade': grade,
            'status': status
        })
    
    total = len(performance)
    valid_sgpas = [p['sgpa'] for p in performance if p['sgpa'] > 0]
    avg = round(sum(valid_sgpas) / len(valid_sgpas), 2) if valid_sgpas else 0
    
    sorted_students = sorted(performance, key=lambda x: x['sgpa'], reverse=True)
    top_performers = [{'name': s['name'], 'sgpa': s['sgpa']} for s in sorted_students[:5] if s['sgpa'] > 0]
    
    subject_avg = get_subject_averages(students)
    needs = len([p for p in performance if 0 < p['sgpa'] < 4.0])
    
    return jsonify({
        "total_students": total,
        "average_sgpa": avg,
        "subject_averages": subject_avg,
        "top_performers": top_performers,
        "needs_improvement": needs
    })

# ============================================================
# RUN THE APP
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🎓 COLLEGE STUDENT GRADE CALCULATOR")
    print("📚 Credit System - SGPA Calculator")
    print("=" * 60)
    print("\n📖 Subjects:")
    for s in SUBJECTS:
        print(f"   • {s['name']} ({s['credits']} credits)")
    print("\n" + "=" * 60)
    print("🌐 Open: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)