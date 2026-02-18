import matplotlib.pyplot as plt
import io
import urllib, base64
import joblib
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "model.pkl")
model = joblib.load(model_path)
from django.shortcuts import render
from .models import Student

def home(request):
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

        # Save to database
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
def history(request):
    students = Student.objects.all()

    names = [student.name for student in students]
    scores = [student.final_exam_score for student in students]

    plt.figure()
    plt.bar(names, scores)
    plt.xlabel("Students")
    plt.ylabel("Final Exam Score")

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    plt.close()

    return render(request, "history.html", {"students": students, "graph": graph})