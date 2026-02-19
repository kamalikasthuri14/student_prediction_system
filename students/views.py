import os
import io
import base64
import joblib
import matplotlib.pyplot as plt

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import Student

# Load ML Model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "model.pkl")
model = joblib.load(model_path)


# ===============================
# HOME REDIRECTION (Role Based)
# ===============================
@login_required
def home(request):
    if request.user.groups.filter(name='Teacher').exists():
        return redirect('teacher_dashboard')
    return redirect('student_dashboard')


# ===============================
# STUDENT DASHBOARD
# ===============================
@login_required
def student_dashboard(request):

    if request.method == "POST":
        name = request.POST.get("name")
        attendance = float(request.POST.get("attendance"))
        internal = float(request.POST.get("internal"))
        assignment = float(request.POST.get("assignment"))
        final = float(request.POST.get("final"))

        # ML Prediction
        prediction = model.predict([[attendance, internal, assignment, final]])

        if prediction[0] == 1:
            result = "High Chance of Success"
        else:
            result = "Low Chance of Success"

        # Save to Database
        Student.objects.create(
            name=name,
            attendance=attendance,
            internal_marks=internal,
            assignment_score=assignment,
            final_exam_score=final,
            prediction_result=result
        )

        return render(request, "result.html", {"result": result})

    return render(request, "home.html")


# ===============================
# TEACHER DASHBOARD
# ===============================
@login_required
def teacher_dashboard(request):

    # Only Teachers can view this
    if not request.user.groups.filter(name='Teacher').exists():
        return redirect('student_dashboard')

    students = Student.objects.all()
    return render(request, "teacher_dashboard.html", {"students": students})


# ===============================
# HISTORY WITH GRAPH
# ===============================
@login_required
def history(request):

    students = Student.objects.all()

    names = [student.name for student in students]
    scores = [student.final_exam_score for student in students]

    # Create Graph
    plt.figure()
    plt.bar(names, scores)
    plt.xlabel("Students")
    plt.ylabel("Final Exam Score")

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png).decode('utf-8')

    buffer.close()
    plt.close()

    return render(request, "history.html", {
        "students": students,
        "graph": graph
    })