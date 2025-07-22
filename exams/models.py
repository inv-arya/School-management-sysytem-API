from django.db import models
from teachers.models import Teacher
from students.models import Student

class Exam(models.Model):
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='exams')
    created_at = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.PositiveIntegerField()
    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return f"Q: {self.text[:50]}"


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Option: {self.text[:50]} (Correct: {self.is_correct})"


class ExamAttempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_attempts')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    attempted_at = models.DateTimeField(auto_now_add=True)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    score = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('student', 'exam')  

    def __str__(self):
        return f"{self.student.user.username} attempt for {self.exam.title}"


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE)

    def __str__(self):
        return f"Answer to {self.question.text[:30]} by {self.attempt.student.user.username}"



