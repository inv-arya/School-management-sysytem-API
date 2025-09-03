import magic
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import Assignment,Submission
from students.models import Student
from .serializers import AssignmentSerializer,StudentAssignmentSerializer,SubmissionSerializer, OverdueSubmissionSerializer
from datetime import datetime
from django.utils import timezone
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from io import BytesIO
from rest_framework.pagination import PageNumberPagination

class AssignmentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user=self.request.user
        print(user.role)
        if user.role != 'teacher':
            return Response({"error": "Only teachers can create assignments"}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data.copy()
        data['created_by'] = user.teacher.id
        
        
        try:
            deadline = datetime.fromisoformat(data['deadline'])
            if deadline < timezone.now():
                return Response({"error": "Deadline must be in the future"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid deadline format"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if 'reference_files' in request.FILES:
            file = request.FILES['reference_files']
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(file.read())
            allowed_types = [
                'application/pdf',
                'image/jpeg', 'image/png',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'application/vnd.ms-powerpoint',
            ]
            if file_type not in allowed_types:
                return Response({"error": f"Invalid file type: {file_type}"}, status=status.HTTP_400_BAD_REQUEST)
            file.seek(0)  
        
        serializer = AssignmentSerializer(data=data)
        if serializer.is_valid():
            assignment=serializer.save(created_by=user.teacher)
            students = Student.objects.filter(grade=assignment.grade)
            for student in students:
                Submission.objects.get_or_create(
                    student=student,
                    assignment=assignment,
                    defaults={'status': 0}
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssignmentListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        paginator = PageNumberPagination()
        paginator.page_size = 5

        sort_by = request.query_params.get('sort_by', None)
        order = request.query_params.get('order', 'desc')  
        sort_field = None

        if user.role == 'teacher':
            try:
                teacher = user.teacher
            except AttributeError:
                return Response({"error": "User is not associated with a Teacher profile"}, status=status.HTTP_400_BAD_REQUEST)
            
            assignments = Assignment.objects.filter(created_by=teacher)
            serializer_class = AssignmentSerializer
            
        elif user.role == 'student':
            try:
                student = user.student
            except AttributeError:
                return Response({"error": "User is not associated with a Student profile"},
                                status=status.HTTP_400_BAD_REQUEST)

            assignments = Assignment.objects.filter(grade=student.grade)

            subject = request.query_params.get("subject", None)
            if subject:
                assignments = assignments.filter(subject__iexact=subject)

            serializer_class = StudentAssignmentSerializer   
            serializer_context = {"student": student}  
            if sort_by == 'deadline':
                sort_field = 'deadline'
            elif sort_by == 'status':
                
                assignments_with_status = []
                for assignment in assignments:
                    submission, _ = Submission.objects.get_or_create(
                        student=student,
                        assignment=assignment,
                        defaults={'status': 0}
                    )
                    if submission.status != 1 and assignment.deadline < timezone.now():
                        submission.status = 2
                        submission.save()
                    assignments_with_status.append({
                        'assignment': assignment,
                        'status': submission.status
                    })
                
                assignments_with_status.sort(
                    key=lambda x: x['status'],
                    reverse=(order == 'desc')
                )
                assignments = [item['assignment'] for item in assignments_with_status]    
            
        else:
            assignments = Assignment.objects.all()
            serializer_class = AssignmentSerializer
            serializer_context = {}

        if sort_field:
            order_prefix = '-' if order == 'desc' else ''
            assignments = assignments.order_by(f"{order_prefix}{sort_field}")
            
        page = paginator.paginate_queryset(assignments, request)
        serializer = serializer_class(page, many=True, context=locals())

        return paginator.get_paginated_response(serializer.data)   
        
    
class AssignmentDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssignmentSerializer
    queryset = Assignment.objects.all()

    def get_object(self):
        try:
            assignment = Assignment.objects.get(pk=self.kwargs['pk'])
        except Assignment.DoesNotExist:
            return None
         
        if self.request.user.role == 'student':
            if assignment.grade != self.request.user.student.grade:
                return None
        return assignment

    def validate_request(self, data, files):
        
        
        if "deadline" in data:
            try:
                deadline = datetime.fromisoformat(data["deadline"])
                if timezone.is_naive(deadline):   
                    deadline = timezone.make_aware(deadline, timezone.get_current_timezone())
                if deadline < timezone.now():
                    return {"error": "Deadline must be in the future"}
            except ValueError:
                return {"error": "Invalid deadline format"}

        
        if "reference_files" in files:
            file = files["reference_files"]
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(file.read())
            allowed_types = [
                "application/pdf",
                "image/jpeg", "image/png",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "application/vnd.ms-powerpoint",
            ]
            if file_type not in allowed_types:
                return {"error": f"Invalid file type: {file_type}"}
            file.seek(0)

        return None

    def put(self, request, pk):
        
        assignment = self.get_object()
        if not assignment:
            return Response({"error": "Not authorized or Assignment not found"}, status=status.HTTP_404_NOT_FOUND)
        if assignment.deadline < timezone.now():
            return Response({"error": "Assignment deadline has passed. Editing not allowed."}, status=status.HTTP_400_BAD_REQUEST)
        error = self.validate_request(request.data, request.FILES)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(assignment, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        assignment = self.get_object()
        if not assignment:
            return Response({"error": "Not authorized or Assignment not found"}, status=status.HTTP_404_NOT_FOUND)
        if assignment.deadline < timezone.now():
            return Response({"error": "Assignment deadline has passed. Editing not allowed."}, status=status.HTTP_400_BAD_REQUEST)
        error = self.validate_request(request.data, request.FILES)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        assignment = self.get_object()
        if not assignment:
            return Response({"error": "Not authorized or Assignment not found"}, status=status.HTTP_404_NOT_FOUND)

        assignment.delete()
        return Response({"message": "Assignment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
class AssignmentSubjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        
        if user.role != "student":
            return Response({"error": "Only students can view subjects"},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            student = user.student
        except AttributeError:
            return Response({"error": "User is not associated with a Student profile"},
                            status=status.HTTP_400_BAD_REQUEST)

        
        subjects = Assignment.objects.filter(grade=student.grade) \
                                     .values_list("subject", flat=True) \
                                     .distinct()
        paginator = PageNumberPagination()
        paginator.page_size = 5 
        result_page = paginator.paginate_queryset(list(subjects), request)

        return paginator.get_paginated_response(result_page)

class SubmissionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        if request.user.role not in ['student', 'teacher']:
            return Response({"error": "Only students or teachers can update submissions"}, status=status.HTTP_403_FORBIDDEN)

        if request.user.role == 'student':
            
            try:
                student = request.user.student
            except AttributeError:
                return Response({"error": "User is not associated with a Student profile"}, status=status.HTTP_400_BAD_REQUEST)
            
            assignment_id = request.data.get('assignment_id')
            if not assignment_id:
                return Response({"error": "assignment_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                assignment = Assignment.objects.get(id=assignment_id)
            except Assignment.DoesNotExist:
                return Response({"error": "Assignment not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if assignment.grade != student.grade:
                return Response({"error": "Assignment does not belong to student's grade"}, status=status.HTTP_403_FORBIDDEN)
            
            if assignment.deadline < timezone.now():
                return Response({"error": "Assignment deadline has passed"}, status=status.HTTP_400_BAD_REQUEST)
            
            if 'submission_file' not in request.FILES:
                return Response({"error": "submission_file is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            file = request.FILES['submission_file']
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(file.read())
            allowed_types = [
                'application/pdf',
                'image/jpeg', 'image/png',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'application/vnd.ms-powerpoint',
            ]
            if file_type not in allowed_types:
                return Response({"error": f"Invalid file type: {file_type}"}, status=status.HTTP_400_BAD_REQUEST)
            file.seek(0)
            
            try:
                submission = Submission.objects.get(student=student, assignment=assignment)
            except Submission.DoesNotExist:
                return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)
            
            submission.submission_files = file
            submission.submitted_at = timezone.now()
            submission.status = 1
            submission.save()
            
            serializer = SubmissionSerializer(submission)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:  
            
            try:
                teacher = request.user.teacher
            except AttributeError:
                return Response({"error": "User is not associated with a Teacher profile"}, status=status.HTTP_400_BAD_REQUEST)
            
            submission_id = request.data.get('submission_id')
            if not submission_id:
                return Response({"error": "submission_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                submission = Submission.objects.get(id=submission_id)
            except Submission.DoesNotExist:
                return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if submission.assignment.created_by != teacher:
                return Response({"error": "Not authorized to update marks for this submission"}, status=status.HTTP_403_FORBIDDEN)
            
            marks = request.data.get('marks')
            if marks is None:
                return Response({"error": "marks is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                marks = float(marks)
                if marks < 0 or marks > submission.assignment.max_marks:
                    return Response({"error": f"Marks must be between 0 and {submission.assignment.max_marks}"}, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                return Response({"error": "Invalid marks value"}, status=status.HTTP_400_BAD_REQUEST)
            
            submission.marks = marks
            submission.save()
            
            serializer = SubmissionSerializer(submission)
            return Response(serializer.data, status=status.HTTP_200_OK)   


class TeacherAssignmentSubmissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if request.user.role != 'teacher':
            return Response({"error": "Only teachers can view assignment submissions"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            teacher = request.user.teacher
        except AttributeError:
            return Response({"error": "User is not associated with a Teacher profile"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            assignment = Assignment.objects.get(id=pk)
        except Assignment.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if assignment.created_by != teacher:
            return Response({"error": "Not authorized to view submissions for this assignment"}, status=status.HTTP_403_FORBIDDEN)
        
        submissions = Submission.objects.filter(assignment=assignment, status=1)
        paginator = PageNumberPagination()
        paginator.page_size = 5   
        result_page = paginator.paginate_queryset(submissions, request)

        serializer = SubmissionSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class SubmissionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assignment_id):
        if request.user.role != 'student':
            return Response({"error": "Only students can view submission details"}, status=status.HTTP_403_FORBIDDEN)

        try:
            student = request.user.student
        except AttributeError:
            return Response({"error": "User is not associated with a Student profile"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            submission = Submission.objects.get(student=student, assignment_id=assignment_id)
        except Submission.DoesNotExist:
            return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubmissionSerializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OverdueSubmissionListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, assignment_id):
        try:
            assignment = Assignment.objects.get(id=assignment_id , deadline__lt=timezone.now())
        except Assignment.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=status.HTTP_404_NOT_FOUND)

        Submission.objects.filter(
            assignment_id=assignment_id,
            status=0
        ).update(status=2)  

        overdue_submissions = Submission.objects.filter(assignment_id=assignment_id, status=2).select_related('student')

        paginator = PageNumberPagination()
        paginator.page_size = 5   
        result_page = paginator.paginate_queryset(overdue_submissions, request)
        serializer = OverdueSubmissionSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class OverdueSubmissionExportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, assignment_id):
        print("111111111111")
        format_type = request.query_params.get('formats', 'excel').lower()
        print(format_type)
        if format_type not in ['excel', 'pdf']:
            return Response({"error": "Invalid format. Use 'excel' or 'pdf'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=status.HTTP_404_NOT_FOUND)

        overdue_submissions = Submission.objects.filter(assignment_id=assignment_id, status=2).select_related('student')
        serializer = OverdueSubmissionSerializer(overdue_submissions, many=True)
        data = serializer.data

        print(data)
        if not data:
            print("No overdue submissions found")
            return Response({"error": "No overdue submissions found"}, status=status.HTTP_404_NOT_FOUND)

        if format_type == 'excel':
            wb = Workbook()
            ws = wb.active
            ws.title = f"Overdue Submissions - Assignment {assignment_id}"
            ws.append(["Student Name"])
            for submission in data:
                ws.append([submission['student_name']])

            buffer = BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            response = HttpResponse(
                buffer,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename=overdue_submissions_{assignment_id}.xlsx'
            return response

        else:  
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(100, 750, f"Overdue Submissions for Assignment: {assignment.title}")
            y = 700
            for  submission in data:
                c.drawString(100, y, submission['student_name'])
                y -= 20
                if y < 50:
                    c.showPage()
                    y = 750
            c.save()
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename=overdue_submissions_{assignment_id}.pdf'
            return response
        


        