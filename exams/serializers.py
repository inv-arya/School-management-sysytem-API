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

    def validate(self, data):
        options = data.get('options', [])

        
        if len(options) != 4:
            raise serializers.ValidationError("Each question must have exactly 4 options.")

        
        correct_options = [opt for opt in options if opt.get('is_correct')]
        if not correct_options:
            raise serializers.ValidationError("At least one option must be marked as correct.")

        return data

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
        fields = ['id', 'title', 'created_by', 'created_at', 'duration_minutes','questions']
        read_only_fields = ['created_by', 'created_at']

    def validate_duration_minutes(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be a positive number.")
        return value

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
    
    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)

        
        instance.title = validated_data.get('title', instance.title)
        instance.duration_minutes = validated_data.get('duration_minutes', instance.duration_minutes)
        instance.save()

        if questions_data is not None:
            
            instance.questions.all().delete()

            for question_data in questions_data:
                options_data = question_data.pop('options')
                question = Question.objects.create(exam=instance, **question_data)
                for option_data in options_data:
                    Option.objects.create(question=question, **option_data)

        return instance

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
        fields = ['id', 'title', 'created_at','duration_minutes']
        
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
        
        exam = Exam.objects.get(pk=exam_id)
        total_questions = exam.questions.count()
        correct_count = 0


        attempt = ExamAttempt.objects.create(student=student, exam_id=exam_id)

        for answer in answers_data:
            question = Question.objects.get(pk=answer['question_id'])
            if question.exam_id != exam.id:
                raise serializers.ValidationError("Question does not belong to this exam.")
            option = Option.objects.get(pk=answer['selected_option_id'])

            if option.is_correct:
                correct_count += 1

            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=option
            )
        attempt.total_questions = total_questions
        attempt.correct_answers = correct_count
        attempt.score = round((correct_count / total_questions) * 100, 2)
        attempt.save()    

        return attempt