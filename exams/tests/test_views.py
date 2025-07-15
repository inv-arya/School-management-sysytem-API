from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date

from students.models import Student
from teachers.models import Teacher
from exams.models import Exam, Question, Option, ExamAttempt

User = get_user_model()


class ExamViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create teacher and login
        self.teacher_user = User.objects.create_user(username='teacher1', password='pass', role='teacher')
        self.teacher = Teacher.objects.create(user=self.teacher_user, date_of_joining=date.today())

        # Create student
        self.student_user = User.objects.create_user(username='student1', password='pass', role='student')
        self.student = Student.objects.create(
            user=self.student_user,
            assigned_teacher=self.teacher,
            date_of_birth=date(2006, 1, 1),
            admission_date=date(2021, 6, 1)
        )

        # Authenticated clients
        self.teacher_client = APIClient()
        self.teacher_client.force_authenticate(user=self.teacher_user)

        self.student_client = APIClient()
        self.student_client.force_authenticate(user=self.student_user)

    def test_teacher_can_create_exam(self):
        url = reverse('exam-create')
        data = {
            "title": "Physics Test",
            "questions": [
                {
                    "text": "Speed of light?",
                    "options": [
                        {"text": "3x10^8 m/s", "is_correct": True},
                        {"text": "1x10^6 m/s", "is_correct": False},
                        {"text": "None", "is_correct": False},
                        {"text": "Infinity", "is_correct": False},
                    ]
                }
            ]
        }
        response = self.teacher_client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Exam.objects.count(), 1)
        self.assertEqual(Exam.objects.first().questions.count(), 1)

    def test_student_can_view_assigned_exams(self):
        exam = Exam.objects.create(title='Math Quiz', created_by=self.teacher)
        url = reverse('exam-list')
        response = self.student_client.get(url)
        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertEqual(len(response.data['results']), 1)
        
        self.assertEqual(response.data['results'][0]['title'], 'Math Quiz')

    def test_student_can_attempt_exam(self):
        exam = Exam.objects.create(title='Biology Test', created_by=self.teacher)
        question = Question.objects.create(exam=exam, text="Cell unit?")
        option = Option.objects.create(question=question, text="Mitochondria", is_correct=True)

        url = reverse('exam-attempt')
        data = {
            'exam_id': exam.id,
            'answers': [
                {
                    'question_id': question.id,
                    'selected_option_id': option.id
                }
            ]
        }
        response = self.student_client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ExamAttempt.objects.count(), 1)

    def test_prevent_duplicate_exam_attempts(self):
        exam = Exam.objects.create(title='Chemistry Test', created_by=self.teacher)
        question = Question.objects.create(exam=exam, text="H2O?")
        option = Option.objects.create(question=question, text="Water", is_correct=True)

        ExamAttempt.objects.create(exam=exam, student=self.student)

        url = reverse('exam-attempt')
        data = {
            'exam_id': exam.id,
            'answers': [
                {
                    'question_id': question.id,
                    'selected_option_id': option.id
                }
            ]
        }
        response = self.student_client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('already attempted', str(response.data).lower())

    def test_student_can_view_only_available_exams(self):
        # Create multiple exams by the assigned teacher
            exam1 = Exam.objects.create(title='Physics', created_by=self.teacher)
            exam2 = Exam.objects.create(title='Chemistry', created_by=self.teacher)
            exam3 = Exam.objects.create(title='Biology', created_by=self.teacher)

            # Student has already attempted exam1 and exam2
            ExamAttempt.objects.create(student=self.student, exam=exam1)
            ExamAttempt.objects.create(student=self.student, exam=exam2)

            url = reverse('exam-list')  # Should be linked to AvailableExamListView

            response = self.student_client.get(url)
            self.assertEqual(response.status_code, 200)

            # Extract paginated results safely
            exam_list = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
            returned_titles = [exam['title'] for exam in exam_list]

            self.assertEqual(returned_titles, ['Biology'])
