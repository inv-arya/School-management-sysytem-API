from django.test import TestCase
from exams.models import Exam, Question, Option, ExamAttempt, StudentAnswer
from teachers.models import Teacher
from students.models import Student
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

class ExamModelTest(TestCase):

    def setUp(self):
        # Create a teacher user
        self.teacher_user = User.objects.create_user(username='teacher1', password='pass1234', role='teacher')
        self.teacher = Teacher.objects.create(user=self.teacher_user,date_of_joining=date.today())

        # Create a student user
        self.student_user = User.objects.create_user(username='student1', password='pass1234', role='student')
        self.student = Student.objects.create(user=self.student_user, assigned_teacher=self.teacher, date_of_birth=date(2005, 1, 1),admission_date=date(2020, 6, 1) )

        # Create an exam
        self.exam = Exam.objects.create(title='Science Test', created_by=self.teacher)

        # Create a question
        self.question = Question.objects.create(exam=self.exam, text='What is H2O?')

        # Create options
        self.option1 = Option.objects.create(question=self.question, text='Water', is_correct=True)
        self.option2 = Option.objects.create(question=self.question, text='Oxygen', is_correct=False)

    def test_exam_creation(self):
        self.assertEqual(self.exam.title, 'Science Test')
        self.assertEqual(self.exam.created_by, self.teacher)

    def test_question_creation(self):
        self.assertEqual(self.question.exam, self.exam)
        self.assertEqual(self.question.text, 'What is H2O?')

    def test_option_creation(self):
        self.assertEqual(self.option1.question, self.question)
        self.assertTrue(self.option1.is_correct)
        self.assertFalse(self.option2.is_correct)

    def test_exam_attempt_creation(self):
        attempt = ExamAttempt.objects.create(student=self.student, exam=self.exam)
        self.assertEqual(attempt.student, self.student)
        self.assertEqual(attempt.exam, self.exam)

    def test_student_answer_creation(self):
        attempt = ExamAttempt.objects.create(student=self.student, exam=self.exam)
        answer = StudentAnswer.objects.create(
            attempt=attempt,
            question=self.question,
            selected_option=self.option1
        )
        self.assertEqual(answer.attempt, attempt)
        self.assertEqual(answer.question, self.question)
        self.assertEqual(answer.selected_option, self.option1)
