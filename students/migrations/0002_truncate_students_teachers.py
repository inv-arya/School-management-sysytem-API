

from django.db import migrations

def truncate_students_teachers(apps, schema_editor):
    Student = apps.get_model('students', 'Student')
    #Teacher = apps.get_model('teachers', 'Teacher')

    # Delete all records
    Student.objects.all().delete()
    #Teacher.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),  # Update with correct last migration

        
    ]

    operations = [
        migrations.RunPython(truncate_students_teachers),
    ]
