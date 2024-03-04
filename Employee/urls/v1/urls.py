from django.urls import path, include

from Employee.views.v1 import views
from rest_framework.routers import DefaultRouter
from Employee.views.v1.views import *

router = DefaultRouter()
router.register('giftcards', views.GiftCardViewSet, basename='giftcard')

urlpatterns = [
    # Employee
    path('', include(router.urls)),
    path('get_single_employee/', views.get_single_employee),
    path('get_employees_mainpage/', views.get_employees_mainpage),
    path('get_employees/', views.get_Employees),
    path('get_gift_card/',views.get_gift_card),
    path('get_employees_dropdown/', views.get_Employees_dropdown),
    path('get_employees_dashboard/', views.get_employees_dashboard),
    path('update_gift_card/', views.update_gift_card),
    path('create_employee/', views.create_employee),
    path('delete_employee/', views.delete_employee),
    path('update_employee/', views.update_employee),
    path('update_employee_device/', views.update_employee_device),
    path('search_employee/', views.search_employee),
    path('import_employee/', views.import_employee),

    path('create_weekend/', views.create_weekend_management),
    path('update_weekend/', views.update_weekend_management),
    path('get_weekend/', views.get_weekend_management),
    path('delete_weekend/', views.delete_weekend_management),

    path('delete_all_employees/', views.delete_all_employees),
    path('check_email_employees/', views.check_email_employees),

    # Staff GROUP URLS
    path('create_staff_group/', views.create_staff_group),
    path('import_staff_group/', views.import_staff_group),
    path('get_staff_group/', views.get_staff_group),
    path('update_staff_group/', views.update_staff_group),
    path('delete_staff_group/', views.delete_staff_group),

    # Attendence
    path('get_attendence/', views.get_attendence),

    path('get_attendence_device/', views.get_attendence_device),
    path('create_attendence/', views.create_attendence),
    path('update_attendence/', views.update_attendence),
    path('delete_attendence/', views.delete_attendence),
    path('import_attendance/', views.import_attendance),

    # Payroll
    path('create_sallaryslip/', views.create_sallaryslip),
    path('get_payrolls/', views.get_payrolls),
    path('get_payrol_working/', views.get_payrol_working),
    path('get_payrol_working_device/', views.get_payrol_working_device),
    path('delete_payroll/', views.delete_payroll),

    # commssion
    path('get_commission/', views.get_commission),
    path('get_employee_commission/', views.get_employee_commission),
    path('create_commission/', views.create_commission),
    path('delete_commission/', views.delete_commission),
    path('update_commision/', views.update_commision),

    # Create Asset
    path('create_asset/', views.create_asset),
    path('get_asset/', views.get_asset),
    path('delete_asset/', views.delete_asset),
    path('update_asset/', views.update_asset),

    # Working Schedule
    path('working_schedule/', views.get_workingschedule),
    path('single_employee_schedule/', views.single_employee_schedule),

    # Generate ID
    path('generate_id/', views.generate_id),
    path('get_detail_from_code/',views.get_detail_from_code),

    # Vacations For Employee
    # path('create_vacation/', views.create_vacation),
    # path('get_vacation/', views.get_vacation),
    # path('delete_vacation/', views.delete_vacation),
    # path('update_vacation/', views.update_vacation),
    path('update_vacation_status/', views.update_vacation_status),

    path('create_vacation/', views.create_vacation_emp),
    path('get_vacation/', views.get_vacations),
    path('delete_vacation/', views.delete_workingschedule),
    path('delete_all_vacation/', views.delete_all_vacation),
    path('update_vacation/', views.update_workingschedule),

    # Absence for Employee
    path('create_absence/', views.create_absence),
    path('get_absence/', views.get_absence),
    path('delete_absence/', views.delete_absence),
    path('update_absence/', views.update_absence),
    # Working Schecule for Employee
    path('create_workingschedule/', views.create_workingschedule),
    path('get_workingschedule/', views.get_workingschedule),
    path('delete_all_data/', views.get_workingschedule),
    path('del_all_avaliable',views.del_all_avaliable),
    path('delete_workingschedule/', views.delete_workingschedule),
    path('delete_lieu_day/', views.delete_leo_day),
    path('update_workingschedule/', views.update_workingschedule),
    path('delete_all__workingschedule/', views.delete_all__workingschedule),

    # Create User Account
    path('create_employe_account/', views.create_employe_account),
    path('employee_login/', views.employee_login),
    path('employee_logout/', views.employee_logout),
    path('forget_password/', views.forgot_password),
    path('verify_email/', views.verify_email),
    path('resend_password/', views.resend_password),

    # Employee Mobile app
    path('get_employee_device/', views.get_employee_device),
    path('get_single_employee_vacation/', views.get_single_employee_vacation),

    # Set_passeord
    path('set_password/', views.set_password),
    path('check_employee_existance/', views.check_employee_existance),
    
    # Employee Comments
    path('get-employee-comment-list/', EmployeeCommentView.as_view()),
    path('create-employee-comment/', EmployeeCommentView.as_view()),
]
