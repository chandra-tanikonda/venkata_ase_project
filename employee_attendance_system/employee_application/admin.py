from django.contrib import admin
from .models import Employee,EmployeeAttendanceRecord

# Register your models here.
admin.site.register(Employee)
admin.site.register(EmployeeAttendanceRecord)
admin.site.site_header = "Company Employee Attendance System"
admin.site.site_title = "Attendance Portal"
admin.site.index_title = "Welcome to company attendance management system"
