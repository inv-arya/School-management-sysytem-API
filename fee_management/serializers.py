from rest_framework import serializers
from .models import FeePayment,FeeStructure

class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model=FeeStructure
        fields=['grade', 'academic_year', 'tuition_fee', 'library_fee', 'lab_fee', 'fine_per_day']
        def validate_academic_year(self, value):
            try:
                start_year, end_year = map(int, value.split('-'))
                if start_year >= end_year or len(value) != 9:
                    raise serializers.ValidationError("Academic year must be in format 'YYYY-YYYY' with valid years.")
            except ValueError:
                raise serializers.ValidationError("Academic year must be in format 'YYYY-YYYY'.")
            return value

        def validate_tuition_fee(self, value):
            if value <= 0:
                raise serializers.ValidationError("Tuition fee must be positive.")
            return value

        def validate_library_fee(self, value):
            if value < 0:
                raise serializers.ValidationError("Library fee cannot be negative.")
            return value

        def validate_lab_fee(self, value):
            if value < 0:
                raise serializers.ValidationError("Lab fee cannot be negative.")
            return value

        def validate_fine_per_day(self, value):
            if value <= 0:
                raise serializers.ValidationError("Fine per day must be positive.")
            return value

        def validate(self, data):
            if FeeStructure.objects.filter(grade=data['grade'], academic_year=data['academic_year']).exists():
                raise serializers.ValidationError("Fee structure for this grade and academic year already exists.")
            return data