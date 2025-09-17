from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from assignment.models import Assignment, Submission
from students.models import Student
from django.conf import settings

class Command(BaseCommand):
    help = 'Send email reminders for upcoming and overdue assignments'

    def handle(self, *args, **kwargs):
        self.stdout.write("Running send_assignment_reminders command")
        now = timezone.now()
        upcoming_deadline = now + timedelta(hours=24)
        
        
        assignments = Assignment.objects.filter(deadline__lte=upcoming_deadline, deadline__gt=now)
        self.stdout.write(f"Found {assignments.count()} upcoming assignments")
        for assignment in assignments:
            students = Student.objects.filter(grade=assignment.grade)
            for student in students:
                if not student.email:
                    self.stdout.write(self.style.WARNING(f"No email for student {student.first_name} {student.last_name}"))
                    continue
                submission = Submission.objects.filter(student=student, assignment=assignment).first()
                if not submission or submission.status == 0:  
                    subject = f"Reminder: Assignment '{assignment.title}' Due Soon"
                    message = (
                        f"Dear {student.first_name},\n\n"
                        f"The assignment '{assignment.title}' is due on {assignment.deadline.strftime('%Y-%m-%d %H:%M')}.\n"
                        f"Please submit it before the deadline.\n\n"
                        f"Regards,\nSchool Management System"
                    )
                    try:
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [student.email],
                            fail_silently=False,  
                        )
                        self.stdout.write(self.style.SUCCESS(f"Sent reminder to {student.email} for assignment {assignment.id}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed to send reminder to {student.email}: {str(e)}"))
        
        overdue_assignments = Assignment.objects.filter(deadline__lt=now)  
        for assignment in overdue_assignments:
            submissions = Submission.objects.filter(assignment=assignment).exclude(status=1)  
            for submission in submissions:
                if submission.status != 2:  
                    submission.status = 2
                    submission.save()
                    self.stdout.write(self.style.WARNING(
                        f"Marked submission {submission.id} (student: {submission.student.email}) as overdue"
                    ))
        
        overdue_submissions = Submission.objects.filter(status=2)
        self.stdout.write(f"Found {overdue_submissions.count()} overdue submissions")
        for submission in overdue_submissions:
            student = submission.student
            if not student.email:
                self.stdout.write(self.style.WARNING(f"No email for student {student.first_name} {student.last_name}"))
                continue
            subject = f"Overdue: Assignment '{submission.assignment.title}'"
            message = (
                f"Dear {student.first_name},\n\n"
                f"The assignment '{submission.assignment.title}' was due on {submission.assignment.deadline.strftime('%Y-%m-%d %H:%M')}.\n"
                f"Please submit it as soon as possible.\n\n"
                f"Regards,\nSchool Management System"
            )
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [student.email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f"Sent overdue reminder to {student.email} for assignment {submission.assignment.id}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to send overdue reminder to {student.email}: {str(e)}"))