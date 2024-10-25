
from django.shortcuts import render,redirect
from .forms import EmployeeCreationForm,AdminRegistrationForm
from django.contrib import messages
import random
import pandas
from openpyxl import load_workbook
from django.contrib.auth import login
import datetime
import qrcode

from allauth.account.utils import perform_login
from allauth.account import app_settings as company_settings

from employee_application.models import Employee


# this is view for landing page
def landing_page_view(request):
    # render the landing page template
    return render(request,'landing_page.html')

def admin_home_screen(request):
    return render(request, 'admin_screen_template.html')

def employee_home_screen(request):
    return render(request, 'employee_screen_template.html')
def create_unique_qr_code_for_employee(unique_qr_txt):
    """
    Creating the unique qr code for the employee
    """
    qr_img = qrcode.make(unique_qr_txt)
    qr_img.save(str(unique_qr_txt) + ".png")


from django.shortcuts import render, redirect
from django.contrib.auth import login


def create_new_admin_user(request):
    if request.method == "POST":
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            # Call helper function to create and log in the new admin user
            admin_user = save_and_create_admin_user(request, form)
            return redirect('admin_home')
    else:
        form = AdminRegistrationForm()

    return render(request, 'admin_registration.html', {'form': form})


def save_and_create_admin_user(request, form):
    """
    Helper function to save the admin user and log them in.
    Sets the is_superuser and is_staff flags to True.
    """
    # Save the form without committing to make additional changes
    admin_user = form.save(commit=False)

    # Mark the user as superuser and staff
    admin_user.is_superuser = True
    admin_user.is_staff = True

    # Save the user to the database
    admin_user.save()

    # Log the new user in
    login(request, admin_user)

    return admin_user


from django.contrib.auth import logout

def admin_logout(request):
    logout(request)
    return redirect('emp_admin_login')



def employee_logout(request):
    """
    Logs out the user and redirects to the login page.
    """
    logout(request)
    return redirect('emp_login')  # Redirect to the login page after logging out

def company_admin_login(request):
    """
    Admin login view to authenticate the admin user using email and password.
    """
    # Redirect to dashboard if the user is already logged in and active
    if request.user.is_authenticated and request.user.is_active:
        return redirect('admin_home')

    # Handle POST request for login
    if request.method == "POST":
        email_address = request.POST.get("admin_email")
        password = request.POST.get("admin_password")

        # Validate if the email address is associated with an admin
        try:
            admin_user = Employee.objects.get(email=email_address, is_superuser=True)
        except Employee.DoesNotExist:
            messages.error(request, f"No admin found with email {email_address}")
            return render(request, 'admin_login.html')

        # Validate password for the admin user
        if not admin_user.check_password(password):
            messages.error(request, "Incorrect password")
            return render(request, 'admin_login.html')

        # Log the admin user in and redirect to dashboard
        login(request, admin_user)
        return redirect('admin_home')

    # Render the login page for GET request
    return render(request, 'admin_login.html')

def company_admin_dashboard(request):
    """
    Admin dashboard view
    """
    admin_user = request.user
    if not admin_user.is_active:
        return redirect('emp_admin_login')
        # Query the employee records to calculate the dashboard metrics
    total_employees = Employee.objects.filter(is_superuser=False).count()
    verified_employees = Employee.objects.filter(active_employee=True,is_superuser=False).count()
    pending_verifications = Employee.objects.filter(active_employee=False,is_superuser=False).count()  # Count e
    context = {
        'total_employees': total_employees,
        'verified_employees': verified_employees,
        'pending_verifications': pending_verifications,
    }
    return render(request,'admin_dashboard.html', context)


from datetime import date
def company_employee_dashboard(request):
    employee = request.user
    print("employee id", employee)
    # Calculate total days worked (total attendance records)
    days_worked = EmployeeAttendanceRecord.objects.filter(employee=employee).count()
    # Get recent attendance (last 5 records for display)
    recent_attendance = EmployeeAttendanceRecord.objects.filter(employee=employee).order_by('-attendance_date').first()
    leaves_taken = EmployeeAttendanceRecord.objects.filter(employee=request.user, status='Leave').count()

    # Calculate attendance percentage based on date_of_hire
    if employee.date_of_hire:
        # Calculate total possible working days from date_of_hire to today
        total_days_since_hire = (date.today() - employee.date_of_hire).days
        print("days worked", days_worked)
        print("total_days_since_hire",total_days_since_hire)
        print()
        # Avoid division by zero for new hires
        if total_days_since_hire > 0:
            # Attendance percentage formula
            attendance_percentage = (days_worked / total_days_since_hire) * 100
        else:
            if total_days_since_hire == 0 and days_worked > 0:
                attendance_percentage = (days_worked / 1) * 100
            else:
                attendance_percentage = 0  # Assume 100% if hired today
    else:
        attendance_percentage = 0  # If no hire date is set, assume 0%
    context = {
        'days_worked': days_worked,
        'recent_attendance': recent_attendance,
        'leaves_taken':leaves_taken,'attendance_percentage':attendance_percentage
    }
    return render(request,'employee_home.html',context)
def list_employee_details(request):
    employees = Employee.objects.filter(is_superuser=False).values(
        "first_name","last_name","email","contact_number","street_address_1","street_address_2",
        "city","state","identification_number",
        "pk","date_of_hire",
        "employee_identifier",
        "qr_code_created"
    )
    return render(request, 'all_employee_details.html', {'employees':employees})


import os
from django.conf import settings
from django.core.files import File
import qrcode


def generate_qr_for_employee_by_admin(request, emp_id):
    admin_user = request.user
    if not admin_user.is_active or not admin_user.is_staff:
        # Assuming 'emp_admin_login' is the name of your login route
        return redirect('emp_admin_login')
    try:
        emp = Employee.objects.get(pk=emp_id)
    except Employee.DoesNotExist:
        # Handle the case where the Employee does not exist
        # Redirect or show an error message
        return redirect('error_page')  # Replace 'error_page' with actual error page route name

    # Generate QR code
    emp.employee_identifier = "group13_employee"+str(emp.pk)
    emp.save()
    qr_img = qrcode.make(emp.employee_identifier)

    # Define the path and filename to save the QR code image
    qr_path = os.path.join(settings.MEDIA_ROOT, 'qr', f"{emp.employee_identifier}.png")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)

    # Save the image to the filesystem
    qr_img.save(qr_path)

    # Open the saved image and attach it to the model
    with open(qr_path, 'rb') as qr_file:
        emp.qr_image.save(f"{emp.employee_identifier}.png", File(qr_file), save=True)

    emp.qr_code_created = True
    emp.active_employee = True
    emp.save()
    # Assuming 'get_all_emp_details' is the name of the route to redirect after saving
    return redirect('get_all_emp_details')


def employee_logic_logic(request):
    return render(request,'employee_login.html')


def save_and_login_user(request, form):

    return user


def generate_employee_code():
    random_number = random.randint(111111, 999999)
    return "EMP" + str(random_number)


from openpyxl import load_workbook


from django.utils import timezone

def new_employee_register(request):
    if request.method == "POST":
        post_form = EmployeeCreationForm(request.POST)
        if post_form.is_valid():
            print("form is valid")
            # Save the user instance and log in the user after registration
            user = post_form.save(commit=False)
            if "admin" in request.path:
                user.is_staff = True
                user.is_superuser = True
            else:
                user.date_of_hire = timezone.now().date()
            user.nation = "USA"
            user.save()
            login(request, user)
            if "admin" in request.path:
                return redirect('admin_home')
            return redirect('emp_home')
        else:
            print("form has errors:", post_form.errors.as_data())
    else:
        post_form = EmployeeCreationForm()

    return render(request, 'employee_creation_screen.html', {'form': post_form})


from .forms import EmployeeAddressUpdateForm


def update_employee_details(request):

    if request.method == 'POST':
        form = EmployeeAddressUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            #request.user.active_employee = True
            request.user.save()
            # You can add a success message here or redirect to another page
            if "admin" in request.path:
                return redirect('admin_home')
            return redirect('employee_home')
    else:
        form = EmployeeAddressUpdateForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'employee_profile_update.html', context)




def show_admin_details(request):
    return render(request, 'admin_profile.html')

def employee_profile_view(request):
    return render(request,'emp_profile.html')

from .models import EmployeeAttendanceRecord
def get_all_employee_attendance_history(request):
    values = EmployeeAttendanceRecord.objects.all()
    return render(request, 'show_all_employees_attendance_records.html',
                  {'values': values})

def get_employee_attendance_history(request):
    values = EmployeeAttendanceRecord.objects.filter(employee=request.user)
    return render(request, 'show_employees_attendance_records.html',
                  {'values': values})
