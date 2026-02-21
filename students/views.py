import os
import io
import base64
import joblib
import matplotlib.pyplot as plt

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet

from .models import Student


# ===============================
# SAFE MODEL LOADING
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "model.pkl")

model = None
if os.path.exists(model_path):
    model = joblib.load(model_path)


# ===============================
# HOME REDIRECT
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

        # ✅ ML if available, otherwise fallback logic
        if model:
            prediction = model.predict([[attendance, internal, assignment, final]])
            result = "High Chance of Success" if prediction[0] == 1 else "Low Chance of Success"
        else:
            average = (attendance + internal + assignment + final) / 4
            result = "High Chance of Success" if average >= 50 else "Low Chance of Success"

        color = "green" if "High" in result else "red"

        student = Student.objects.create(
            name=name,
            attendance=attendance,
            internal_marks=internal,
            assignment_score=assignment,
            final_exam_score=final,
            prediction_result=result
        )

        request.session['last_student_id'] = student.id

        # 📊 GRAPH
        plt.figure(figsize=(6, 4))
        plt.bar(
            ["Attendance", "Internal", "Assignment", "Final"],
            [attendance, internal, assignment, final],
        )
        plt.ylim(0, 100)
        plt.title("Student Performance Overview")

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
# HISTORY PAGE
# ===============================
@login_required
def history(request):

    students = Student.objects.all()
    total_students = students.count()

    if total_students == 0:
        return render(request, "history.html", {
            "students": students,
            "graph": None,
            "total_students": 0,
            "avg_score": 0,
            "high_count": 0,
            "low_count": 0
        })

    names = [student.name for student in students]
    scores = [student.final_exam_score for student in students]

    avg_score = round(sum(scores) / total_students, 2)

    high_count = students.filter(prediction_result="High Chance of Success").count()
    low_count = students.filter(prediction_result="Low Chance of Success").count()

    plt.figure(figsize=(10, 5))
    plt.bar(names, scores)
    plt.ylim(0, 100)
    plt.xticks(rotation=45)
    plt.title("Students Performance History")

    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png).decode('utf-8')

    buffer.close()
    plt.close()

    return render(request, "history.html", {
        "students": students,
        "graph": graph,
        "total_students": total_students,
        "avg_score": avg_score,
        "high_count": high_count,
        "low_count": low_count
    })


# ===============================
# PDF DOWNLOAD
# ===============================
@login_required
def download_pdf(request):

    student_id = request.session.get('last_student_id')

    if not student_id:
        return redirect('student_dashboard')

    student = Student.objects.get(id=student_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Student_Report.pdf"'

    doc = SimpleDocTemplate(response)
    elements = []

    styles = getSampleStyleSheet()
    style = styles["Normal"]

    elements.append(Paragraph("<b>Student Performance Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph(f"Name: {student.name}", style))
    elements.append(Paragraph(f"Attendance: {student.attendance}", style))
    elements.append(Paragraph(f"Internal Marks: {student.internal_marks}", style))
    elements.append(Paragraph(f"Assignment Score: {student.assignment_score}", style))
    elements.append(Paragraph(f"Final Exam Score: {student.final_exam_score}", style))
    elements.append(Paragraph(f"Prediction Result: {student.prediction_result}", style))

    doc.build(elements)

    return response


# ===============================
# DELETE STUDENT
# ===============================
@login_required
def delete_student(request, student_id):
    student = Student.objects.get(id=student_id)
    student.delete()
    return redirect('history')


# ===============================
# EDIT STUDENT
# ===============================
@login_required
def edit_student(request, student_id):
    student = Student.objects.get(id=student_id)

    if request.method == "POST":
        student.name = request.POST.get("name")
        student.attendance = request.POST.get("attendance")
        student.internal_marks = request.POST.get("internal")
        student.assignment_score = request.POST.get("assignment")
        student.final_exam_score = request.POST.get("final")
        student.save()

        return redirect('history')

    return render(request, "edit_student.html", {
        "student": student
    })