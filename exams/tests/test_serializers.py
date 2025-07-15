from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from students.models import Student
from teachers.models import Teacher
from exams.models import Exam, Question, Option, ExamAttempt
from exams.serializers import (
    ExamSerializer,
    ExamAttemptSerializer,
    # ExamStudentListSerializer
)

User = get_user_model()


class ExamSerializerTest(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(username='teacher', password='pass', role='teacher')
        self.teacher = Teacher.objects.create(user=self.teacher_user, date_of_joining=date.today())

    def test_exam_creation_with_nested_questions_and_options(self):
        request = APIRequestFactory().post('/')
        request.user = self.teacher_user

        data = {
            'title': 'Science Test',
            'questions': [
                {
                    'text': 'What is H2O?',
                    'options': [
                        {'text': 'Water', 'is_correct': True},
                        {'text': 'Oxygen', 'is_correct': False},
                        {'text': 'Hydrogen', 'is_correct': False},
                        {'text': 'Carbon', 'is_correct': False},
                    ]
                },
                {
                    'text': 'What planet do we live on?',
                    'options': [
                        {'text': 'Mars', 'is_correct': False},
                        {'text': 'Earth', 'is_correct': True},
                        {'text': 'Venus', 'is_correct': False},
                        {'text': 'Jupiter', 'is_correct': False},
                    ]
                }
            ]
        }

        serializer = ExamSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        exam = serializer.save()

        self.assertEqual(exam.questions.count(), 2)
        self.assertEqual(exam.questions.first().options.count(), 4)


class ExamAttemptSerializerTest(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(username='teach', password='pass', role='teacher')
        self.teacher = Teacher.objects.create(user=self.teacher_user, date_of_joining=date.today())

        self.student_user = User.objects.create_user(username='student', password='pass', role='student')
        self.student = Student.objects.create(
            user=self.student_user,
            assigned_teacher=self.teacher,
            date_of_birth=date(2005, 1, 1),
            admission_date=date(2021, 6, 1)
        )

        self.exam = Exam.objects.create(title='Math Test', created_by=self.teacher)
        self.question = Question.objects.create(text='2+2?', exam=self.exam)
        self.option = Option.objects.create(text='4', is_correct=True, question=self.question)

        # First attempt (existing one to trigger duplicate attempt check)
        ExamAttempt.objects.create(exam=self.exam, student=self.student)

    def test_duplicate_exam_attempt_validation(self):
        request = APIRequestFactory().post('/')
        request.user = self.student_user

        data = {
            'exam_id': self.exam.id,
            'answers': [
                {
                    'question_id': self.question.id,
                    'selected_option_id': self.option.id
                }
            ]
        }

        serializer = ExamAttemptSerializer(data=data, context={'request': request})
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn('You have already attempted this exam.', str(context.exception))


# class ExamStudentListSerializerTest(TestCase):
#     def setUp(self):
#         self.teacher_user = User.objects.create_user(username='teacher', password='pass', role='teacher')
#         self.teacher = Teacher.objects.create(user=self.teacher_user, date_of_joining=date.today())

#         self.student_user = User.objects.create_user(username='student1', password='pass', role='student')
#         self.student = Student.objects.create(
#             user=self.student_user,
#             assigned_teacher=self.teacher,
#             date_of_birth=date(2006, 1, 1),
#             admission_date=date(2022, 5, 10)
#         )

#         self.exam = Exam.objects.create(title='Geography Quiz', created_by=self.teacher)
#         self.attempt = ExamAttempt.objects.create(exam=self.exam, student=self.student)

#     def test_exam_student_list_serializer_structure(self):
#         serializer = ExamStudentListSerializer(instance=self.attempt)
#         data = serializer.data

#         self.assertIn('id', data)
#         self.assertIn('exam', data)
#         self.assertIn('student', data)
#         self.assertEqual(data['exam'], self.exam.title)
#         self.assertEqual(data['student'], self.student.user.username)
