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
    path('create/admin/', views.create_new_admin_user, name='admin_create'),
    path('admin/login/', views.company_admin_login, name='emp_admin_login'),
    path('admin/home/', views.company_admin_dashboard, name='admin_home'),
    path('admin/profile/', views.show_admin_details, name='admin_details'),
    path('admin/profile/update/',views.update_admin_details,name='admin_update_profile'),
    path('manage/employees/', views.list_employee_details, name='manage_employees'),
    path('create/qr/code/<int:emp_id>/', views.generate_qr_for_employee_by_admin, name='generate_qr_code'),
    path('all/employees/attendance/details/', views.get_all_employee_attendance_history, name='all_employees_details'),

    # Employee URLs
    path('employee/create/', views.new_employee_register, name='emp_create'),
    path('emp/login/', views.employee_logic_logic, name='emp_login'),
    path('emp/logout/', views.employee_logout_from_system, name='employee_logout'),
    path('emp/logout/confirmation/',views.employee_logout,name='emp_logout'),
    path('employee/profile/update/', views.update_employee_details, name='profile_update'),
    path('emp/home/', views.company_employee_dashboard, name='emp_home'),
    path('employee/profile/', views.employee_profile_view, name='employee_profile'),
    path('emp/attendance/details/', views.get_employee_attendance_history, name='employee_attendance_details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
