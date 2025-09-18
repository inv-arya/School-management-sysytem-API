from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from fee_management.models import FeePayment, FeeStructure
from students.models import Student
import logging

logger = logging.getLogger('fee_management')

class Command(BaseCommand):
    help='create FeePayment entries for students in specific grade and academic year'

    def add_arguments(self, parser):
        parser.add_argument('--grade',type=str,required=True,help='Grade')
        parser.add_argument('--academic_year',type=str,required=True,help='Academic year')
        parser.add_argument('--due_days',type=int,default=30,help='Days from now for due date')

    def handle(self, *args, **options):
        grade=options['grade']
        academic_year=options['academic_year']
        due_days=options['due_days']

        #Get feestructure

        try:
            fee_structure=FeeStructure.objects.get(grade=grade,academic_year=academic_year)
        except FeeStructure.DoesNotExist:
            self.stdout.write*(self.style.ERROR(f'NO FeeStructure found for grade {grade} and academic year {academic_year}'))
            return
        
        #Get students in this grade

        students=Student.objects.filter(grade=grade,status='active')

        #calculate base amount

        amount=(fee_structure.tuition_fee+fee_structure.library_fee+fee_structure.lab_fee)
        due_date=timezone.now().date() + timedelta(days=due_days)

        created_count=0
        for student in students:

            #check if Feepayment already exist for this student and structure

            if not FeePayment.objects.filter(student=student,fee_structure=fee_structure).exists():
                fee_payment=FeePayment(
                    student=student,
                    fee_structure=fee_structure,
                    amount=amount,
                    total_amount=amount,
                    due_date=due_date,
                    status=0
                )
                fee_payment.save()
                created_count+=1
                logger.info(f"created FeePayment {fee_payment.transaction_id} for {student}")
            else:
                self.stdout.write(self.style.WARNING(f'FeePayment already exist for {student}'))
        self.stdout.write(self.style.SUCCESS(f'created {created_count}'))