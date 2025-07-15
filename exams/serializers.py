from rest_framework import serializers
from .models import Exam, Question, Option, ExamAttempt, StudentAnswer

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'options']

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        question = Question.objects.create(**validated_data)
        for option_data in options_data:
            Option.objects.create(question=question, **option_data)
        return question

class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Exam
        fields = ['id', 'title', 'created_by', 'created_at', 'questions']
        read_only_fields = ['created_by', 'created_at']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        teacher = self.context['request'].user.teacher  # get Teacher instance from user
        exam = Exam.objects.create(created_by=teacher, **validated_data)
        for question_data in questions_data:
            options_data = question_data.pop('options')
            question = Question.objects.create(exam=exam, **question_data)
            for option_data in options_data:
                Option.objects.create(question=question, **option_data)
        return exam

class OptionStudentViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text']

class QuestionStudentViewSerializer(serializers.ModelSerializer):
    options = OptionStudentViewSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'options']
from rest_framework import serializers
from exams.models import ExamAttempt



class AvailableExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'title', 'created_at']


# class ExamStudentListSerializer(serializers.ModelSerializer):
#     exam = serializers.CharField(source='exam.title')  # Access nested exam.title
#     student = serializers.CharField(source='student.user.username')  # Access nested student.user.username

#     class Meta:
#         model = ExamAttempt
#         fields = ['id', 'exam', 'student', 'attempted_at']

class StudentAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_option_id = serializers.IntegerField()

class ExamAttemptSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()
    answers = StudentAnswerSerializer(many=True)

    def validate(self, data):
        user = self.context['request'].user
        student = getattr(user, 'student', None)
        exam_id = data['exam_id']

        if ExamAttempt.objects.filter(student=student, exam_id=exam_id).exists():
            raise serializers.ValidationError("You have already attempted this exam.")

        return data

    def create(self, validated_data):
        student = self.context['request'].user.student
        exam_id = validated_data['exam_id']
        answers_data = validated_data['answers']

        attempt = ExamAttempt.objects.create(student=student, exam_id=exam_id)

        for answer in answers_data:
            question = Question.objects.get(pk=answer['question_id'])
            option = Option.objects.get(pk=answer['selected_option_id'])

            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=option
            )

        return attempt