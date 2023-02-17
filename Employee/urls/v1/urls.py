from django.urls import path, include

from Employee.views.v1 import views

urlpatterns = [
    #Employee
    path('get_single_employee/', views.get_single_employee),
    path('get_employees/', views.get_Employees),
    path('create_employee/', views.create_employee),
    path('delete_employee/', views.delete_employee),
    path('update_employee/', views.update_employee),
    path('search_employee/', views.search_employee),
    path('import_employee/', views.import_employee),

    path('delete_all_employees/', views.delete_all_employees),
    path('check_email_employees/', views.check_email_employees),
    

    #Staff GROUP URLS 
    path('create_staff_group/', views.create_staff_group),
    path('import_staff_group/', views.import_staff_group),
    path('get_staff_group/', views.get_staff_group),
    path('update_staff_group/', views.update_staff_group),
    path('delete_staff_group/', views.delete_staff_group),
    
    #Attendence
    path('get_attendence/', views.get_attendence),
    path('get_attendence_device/', views.get_attendence_device),
    path('create_attendence/', views.create_attendence),
    path('update_attendence/', views.update_attendence),
    path('delete_attendence/', views.delete_attendence),
    path('import_attendance/', views.import_attendance),
    
    #Payroll
    path('create_payroll/', views.create_payroll),
    path('get_payrolls/', views.get_payrolls),
    path('get_payrol_working/', views.get_payrol_working),
    path('get_payrol_working_device/', views.get_payrol_working_device),
    path('delete_payroll/', views.delete_payroll),
    
    #commssion
    path('get_commission/', views.get_commission),
    path('get_employee_commission/', views.get_employee_commission),
    path('create_commission/', views.create_commission),
    path('delete_commission/', views.delete_commission),
    path('update_commision/', views.update_commision),
    
    #Create Asset
    path('create_asset/', views.create_asset),
    path('get_asset/', views.get_asset),
    path('delete_asset/', views.delete_asset), 
    path('update_asset/', views.update_asset), 
    
    #Working Schedule
    path('working_schedule/', views.working_schedule),
    path('single_employee_schedule/', views.single_employee_schedule),
    
    #Generate ID
    path('generate_id/', views.generate_id),
    
    #Vacations For Employee
    # path('create_vacation/', views.create_vacation),
    # path('get_vacation/', views.get_vacation),
    # path('delete_vacation/', views.delete_vacation),
    # path('update_vacation/', views.update_vacation),
    
    path('create_vacation/', views.create_vacation_emp),
    path('get_vacation/', views.get_workingschedule),
    path('delete_vacation/', views.delete_workingschedule),
    path('update_vacation/', views.update_workingschedule),
    
    #Working Schecule for Employee
    path('create_workingschedule/', views.create_workingschedule),
   # path('get_workingschedule/', views.get_workingschedule),
    path('get_workingschedule/', views.working_schedule),
    path('delete_workingschedule/', views.delete_workingschedule), 
    path('update_workingschedule/', views.update_workingschedule), 
    
    #Create User Account
    path('create_employe_account/', views.create_employe_account),
    path('employee_login/', views.employee_login),
    path('forget_password/', views.forgot_password),
    path('verify_email/', views.verify_email),
    path('resend_password/', views.resend_password),
    
    #Employee Mobile app
    path('get_employee_device/', views.get_employee_device),
    path('get_single_employee_vacation/', views.get_single_employee_vacation),
    
    #Set_passeord
    path('set_password/', views.set_password),
    
]