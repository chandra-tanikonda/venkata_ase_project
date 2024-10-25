
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


def company_admin_login(request):
    """
        Handling the admin login in this screen, getting admin email address and password.
    """
    admin_user = request.user
    # if admin_user.is_active:
    #     return redirect('emp_admin_dashboard')
    if request.method == "POST":
        email_address = request.POST["admin_email"]
        password = request.POST["admin_password"]
        admin_users = Employee.objects.filter(email=email_address)
        admin = admin_users.first()
        if not admin:
            return render(request, 'admin_login.html',
                          {'admin_signup_msg': 'No Admin user found with ' + str(email_address)})

        if not admin.check_password(password):
            return render(request, 'admin_login.html',
                          {'admin_signup_msg': 'Password is incorrect '})
        perform_login(request, admin, company_settings.EMAIL_VERIFICATION, signup=False,
                      redirect_url=None, signal_kwargs=None)
        return redirect('admin_dashboard')
    else:
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


def company_employee_dashboard(request):
    employee = request.user
    print("employee id", employee)
    # Calculate total days worked (total attendance records)
    days_worked = EmployeeAttendanceRecord.objects.filter(employee=employee).count()
    # Get recent attendance (last 5 records for display)
    recent_attendance = EmployeeAttendanceRecord.objects.filter(employee=employee).order_by('-attendance_date').first()
    leaves_taken = EmployeeAttendanceRecord.objects.filter(employee=request.user, status='Leave').count()

    context = {
        'days_worked': days_worked,
        'recent_attendance': recent_attendance,
        'leaves_taken':leaves_taken
    }
    return render(request,'employee_home.html',context)
def list_employee_details(request):
    current_user = request.user

    # Fetch details of all non-superuser employees
    employees = Employee.objects.filter(
        is_superuser=False
    ).values(
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "pk",
        "created",
        "employee_code",
        "is_qr_code_generated"
    )

    context = {
        'employees': employees
    }

    return render(request, 'get_all_employee_details.html', context)


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
    emp.employee_code = "EMP"+str(emp.pk)
    emp.save()
    qr_img = qrcode.make(emp.employee_code)

    # Define the path and filename to save the QR code image
    qr_path = os.path.join(settings.MEDIA_ROOT, 'qr', f"{emp.employee_code}.png")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)

    # Save the image to the filesystem
    qr_img.save(qr_path)

    # Open the saved image and attach it to the model
    with open(qr_path, 'rb') as qr_file:
        emp.qr_code_image.save(f"{emp.employee_code}.png", File(qr_file), save=True)

    emp.is_qr_code_generated = True
    emp.save()
    # Assuming 'get_all_emp_details' is the name of the route to redirect after saving
    return redirect('get_all_emp_details')


def employee_logic_logic(request):
    return render(request,'employee_login_screen.html')


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
            return redirect('employee_home')
    else:
        form = EmployeeAddressUpdateForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'employee_profile_update.html', context)




def show_admin_details(request):
    return render(request, 'admin_details.html')

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
