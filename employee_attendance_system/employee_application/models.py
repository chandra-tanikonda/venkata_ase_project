from django.db import models


from django.contrib.auth.models import AbstractUser
from django.db import models


from django.contrib.auth.models import AbstractUser
from django.db import models

class Employee(AbstractUser):
    """
    This model stores employee information for attendance tracking and other personal details.
    It extends the AbstractUser class to include custom fields like employee code, contact details,
    and QR code-related information.
    """
    staff_id = models.AutoField(primary_key=True)  # Unique identifier for each employee
    employee_identifier = models.CharField(max_length=20, null=True, blank=True)  # Custom employee code
    contact_number = models.CharField(max_length=12, null=True, blank=True)  # Employee contact phone number
    first_name = models.CharField(max_length=45, null=True, blank=True)  # Employee first name
    last_name = models.CharField(max_length=45, null=True, blank=True)  # Employee last name
    qr_code_created = models.BooleanField(default=False)  # Status of QR code generation for the employee
    created_at = models.DateTimeField(auto_now_add=True)  # Record creation date
    updated_at = models.DateTimeField(auto_now=True)  # Record last modified date
    street_address_1 = models.CharField(max_length=120, null=True, blank=True)  # First line of address
    street_address_2 = models.CharField(max_length=120, null=True, blank=True)  # Second line of address (optional)
    city = models.CharField(max_length=50, null=True, blank=True)  # City or town of residence
    state = models.CharField(max_length=20, null=True, blank=True)  # State or province of residence
    zip_code = models.CharField(max_length=10, null=True, blank=True)  # Zip code for the address
    nation = models.CharField(max_length=50, null=True, blank=True)  # Country of residence
    qr_image = models.ImageField(upload_to='qr_images/', null=True, blank=True)  # Uploaded image of the QR code
    active_employee = models.BooleanField(default=False)  # Status of employment (active/inactive)
    identification_number = models.CharField(max_length=15, null=True, blank=True)  # National ID or SSN
    job_title = models.CharField(max_length=100, null=True, blank=True)  # Employee's current job title
    date_of_hire = models.DateField(null=True, blank=True)  # Date when the employee was hired

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_identifier})"


from django import forms

class UpdateEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_identifier', 'contact_number', 'first_name', 'last_name',
            'street_address_1', 'street_address_2', 'city', 'state',
            'zip_code', 'nation'
        ]



ATTENDANCE_STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Leave', 'Leave'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Half-day', 'Half-day'),
    ]

class EmployeeAttendanceRecord(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey('Employee',on_delete=models.CASCADE, related_name='attendance_records')
    attendance_date = models.DateField()
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS_CHOICES, default='Present')  # Status field added
    class Meta:
        unique_together = ('employee', 'attendance_date')
        ordering = ['attendance_date']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'

