from django.urls import path
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static

from employee_application import views

urlpatterns = [
    path('company/admin/', admin.site.urls),

    # Landing Page
    path('', views.landing_page_view, name='landing_page'),

    # Admin URLs
    path('admin/home/', views.company_admin_dashboard, name='admin_home'),
    path('create/admin/', views.new_employee_register, name='admin_create'),
    path('admin/login/', views.company_admin_login, name='emp_admin_login'),
    path('employee/admin/login/', views.company_admin_login, name='emp_admin_login'),
    path('admin/home/', views.company_admin_dashboard, name='admin_home'),
    path('admin/profile/', views.show_admin_details, name='admin_details'),
    path('admin/profile/update/', views.update_employee_details, name='admin_profile_update'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('manage/employees/', views.list_employee_details, name='get_all_emp_details'),
    path('create/qr/code/<int:emp_id>/', views.generate_qr_for_employee_by_admin, name='generate_qr_code'),
    path('all/employees/attendance/details/', views.get_all_employee_attendance_history, name='all_employees_details'),

    # Employee URLs
    path('employee/create/', views.new_employee_register, name='emp_create'),
    path('emp/login/', views.employee_logic_logic, name='emp_login'),
    path('employee/profile/update/', views.update_employee_details, name='profile_update'),
    path('employee/home/', views.company_employee_dashboard, name='employee_home'),
    path('employee/home/', views.company_employee_dashboard, name='emp_home'),
    path('employee/profile/', views.employee_profile_view, name='employee_profile'),
    path('emp/logout/', views.employee_logout, name='emp_logout'),
    path('employee/attendance/details/', views.get_employee_attendance_history, name='employee_attendance_details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
