from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    attendance = models.FloatField()
    internal_marks = models.FloatField()
    assignment_score = models.FloatField()
    final_exam_score = models.FloatField()
    prediction_result = models.CharField(max_length=100)   # NEW FIELD

    def __str__(self):
        return self.name