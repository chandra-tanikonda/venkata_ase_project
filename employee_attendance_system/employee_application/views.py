
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
        # Capture form data manually
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Basic validation
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'admin_registration.html')

        if Employee.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'admin_registration.html')

        # Create and save the admin user
        admin_user = Employee.objects.create_user(username=username, email=email, password=password1)
        admin_user.first_name = first_name
        admin_user.last_name = last_name
        admin_user.is_staff = True
        admin_user.contact_number = username
        admin_user.is_superuser = True
        admin_user.save()

        # Log the new admin user in
        #login(request, admin_user)
        authenticated_user = authenticate(username=username, password=password1)
        if authenticated_user is not None:
            login(request, authenticated_user)
            print("User session created successfully")
        else:
            print("Authentication failed for new user")
        return redirect('admin_home')

    return render(request, 'admin_registration.html')


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
    verified_employees = Employee.objects.filter(qr_code_created=True,is_superuser=False).count()
    pending_verifications = Employee.objects.filter(qr_code_created=False,is_superuser=False).count()  # Count e
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
    days_worked = EmployeeAttendanceRecord.objects.filter(employee=request.user.pk).count()
    # Get recent attendance (last 5 records for display)
    recent_attendance = EmployeeAttendanceRecord.objects.filter(employee=request.user.pk).order_by('-attendance_date').first()
    leaves_taken = EmployeeAttendanceRecord.objects.filter(employee=request.user.pk, status='Leave').count()

    context = {
        'days_worked': days_worked,
        'recent_attendance': recent_attendance,
        'leaves_taken':leaves_taken
    }
    return render(request,'employee_home.html',context)

def list_employee_details(request):
    # Filter employees based on their QR code creation status
    verified_employees = Employee.objects.filter(is_superuser=False, qr_code_created=True).values(
        "first_name", "last_name", "email", "contact_number", "street_address_1", "street_address_2",
        "city", "state", "identification_number", "pk", "date_of_hire", "employee_identifier"
    )

    unverified_employees = Employee.objects.filter(is_superuser=False, qr_code_created=False).values(
        "first_name", "last_name", "email", "contact_number", "street_address_1", "street_address_2",
        "city", "state", "identification_number", "pk", "date_of_hire", "employee_identifier"
    )

    # Pass both verified and unverified employees to the template
    return render(request, 'all_employee_details.html', {
        'verified_employees': verified_employees,
        'unverified_employees': unverified_employees
    })


import os
from django.conf import settings
from django.core.files import File
import qrcode


def generate_qr_for_employee_by_admin(request, emp_id):
    admin_user = request.user
    if not admin_user.is_active or not admin_user.is_staff:
        return redirect('emp_admin_login')
    try:
        emp = Employee.objects.get(pk=emp_id)
    except Employee.DoesNotExist:
        return redirect('error_page')

    # Generate QR code
    emp.employee_identifier = "EMP"+str(emp.pk)
    emp.active_employee = True
    emp.save()
    qr_img = qrcode.make(emp.employee_identifier)
    qr_path = os.path.join(settings.MEDIA_ROOT, 'qr', f"{emp.employee_identifier}.png")
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    qr_img.save(qr_path)
    with open(qr_path, 'rb') as qr_file:
        emp.qr_image.save(f"{emp.employee_identifier}.png", File(qr_file), save=True)

    emp.qr_code_created = True
    emp.save()
    # Assuming 'get_all_emp_details' is the name of the route to redirect after saving
    return redirect('manage_employees')


def employee_logic_logic(request):
    return render(request,'employee_login_screen.html')


def save_and_login_user(request, form):

    return user


def generate_employee_code():
    random_number = random.randint(111111, 999999)
    return "EMP" + str(random_number)


from openpyxl import load_workbook


from django.utils import timezone

from django.shortcuts import render, redirect
from django.contrib.auth import login,authenticate
from django.contrib import messages
from .models import Employee  # Import the custom Employee model

def new_employee_register(request):
    # Check if the request method is POST to handle form submission
    if request.method == "POST":
        # Retrieve each field directly from the request.POST dictionary
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        employee_identifier = request.POST.get('employee_identifier')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        street_address_1 = request.POST.get('street_address_1')
        street_address_2 = request.POST.get('street_address_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')

        # Perform basic validation
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'employee_creation_screen.html')

        if Employee.objects.filter(username=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'employee_creation_screen.html')

        # Create the new Employee instance
        user = Employee.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )

        # Set additional fields specific to Employee model
        user.identification_number = employee_identifier
        user.contact_number = contact_number
        user.street_address_1 = street_address_1
        user.street_address_2 = street_address_2
        user.city = city
        user.state = state
        user.zip_code = zip_code
        user.nation = "USA"  # Default to USA

        # Set admin privileges if the path indicates admin registration
        if "admin" in request.path:
            user.is_staff = True
            user.is_superuser = True
        else:
            user.date_of_hire = timezone.now().date()  # Set the hire date for regular employees

        # Save the Employee instance with all fields
        user.save()
        print("User details updated successfullly")
        print(user.pk)
        # Log in the user immediately after registration
        # Authenticate and log in the user to ensure session activation
        authenticated_user = authenticate(username=email, password=password1)
        if authenticated_user is not None:
            login(request, authenticated_user)
            print("User session created successfully")
        else:
            print("Authentication failed for new user")

        # Redirect to the appropriate home page based on the user type
        if "admin" in request.path:
            return redirect('admin_home')
        return redirect('emp_home')

    # Render the form for GET requests
    return render(request, 'employee_creation_screen.html')



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
            return redirect('emp_home')
    else:
        form = EmployeeAddressUpdateForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'employee_profile_update.html', context)

from .forms import AdminUpdateForm

def update_admin_details(request):

    if request.method == 'POST':
        form = AdminUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            #request.user.active_employee = True
            request.user.save()
            # You can add a success message here or redirect to another page
            return redirect('admin_home')
    else:
        form = AdminUpdateForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'admin_profile_update.html', context)

def employee_profile_view(request):
    if not request.user.is_active:
        print("employee is not active")
    return render(request,'emp_profile.html')


def show_admin_details(request):
    return render(request, 'admin_profile.html')

# views.py

from django.contrib.auth import logout
def employee_logout_from_system(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('emp_login')  # Replace 'login' with the name of your login page URL

def employee_logout(request):
    return render(request,'employee_logout.html')




from .models import EmployeeAttendanceRecord
def get_all_employee_attendance_history(request):
    values = EmployeeAttendanceRecord.objects.all()
    return render(request, 'show_all_employees_attendance_records.html',
                  {'values': values})

def get_employee_attendance_history(request):
    values = EmployeeAttendanceRecord.objects.filter(employee=request.user)
    return render(request, 'show_employees_attendance_records.html',
                  {'values': values})
