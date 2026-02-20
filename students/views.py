import os
import io
import base64
import joblib
import matplotlib.pyplot as plt

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import Student

# ===============================
# LOAD ML MODEL
# ===============================
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

        # 🎨 RESULT LOGIC WITH COLORS
        if prediction[0] == 1:
            result = "High Chance of Success"
            color = "green"
        else:
            result = "Low Chance of Success"
            color = "red"

        # Save to Database
        Student.objects.create(
            name=name,
            attendance=attendance,
            internal_marks=internal,
            assignment_score=assignment,
            final_exam_score=final,
            prediction_result=result
        )

        # 📊 CREATE COLORED GRAPH
        plt.figure(figsize=(6, 4))
        plt.bar(
            ["Attendance", "Internal", "Assignment", "Final"],
            [attendance, internal, assignment, final],
            color=["blue", "orange", "purple", color]
        )
        plt.ylim(0, 100)
        plt.title("Student Performance Overview")
        plt.ylabel("Marks")
        plt.grid(True)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        image_png = buffer.getvalue()
        graph = base64.b64encode(image_png).decode('utf-8')

        buffer.close()
        plt.close()

        return render(request, "result.html", {
            "result": result,
            "color": color,
            "graph": graph
        })

    return render(request, "home.html")


# ===============================
# TEACHER DASHBOARD
# ===============================
@login_required
def teacher_dashboard(request):

    if not request.user.groups.filter(name='Teacher').exists():
        return redirect('student_dashboard')

    students = Student.objects.all()
    return render(request, "teacher_dashboard.html", {"students": students})


# ===============================
# HISTORY WITH COLORED GRAPH
# ===============================
@login_required
def history(request):

    students = Student.objects.all()

    names = [student.name for student in students]
    scores = [student.final_exam_score for student in students]

    # 🎨 Color based on score
    colors = []
    for score in scores:
        if score <= 40:
            colors.append("red")
        elif score <= 70:
            colors.append("brown")
        else:
            colors.append("green")

    # 📊 Create Improved Graph
    plt.figure(figsize=(8, 5))
    plt.bar(names, scores, color=colors)
    plt.xlabel("Students")
    plt.ylabel("Final Exam Score")
    plt.title("Students Performance History")
    plt.ylim(0, 100)
    plt.xticks(rotation=45)
    plt.grid(axis='y')

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