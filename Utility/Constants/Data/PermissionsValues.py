
# ALL_PERMISSIONS = [
#     'appointment',
#     'email_staff',
#     'products',
#     'brand',
#     'categories',
#     'vendors',
#     'stock',
#     'stock_report',
#     'staff_data',
#     'staff_product_sales',
#     'staff_product_sales',
#     'staff_product_sales',
#     'rewards',
#     'promotions',
#     'vouchers',
#     'membership',
#     'subscriptions',
#     'sale_product',
#     'sale_rewards',
#     'sale_promotions',
#     'sale_vouchers',
#     'sale_membership',
#     'sale_subscriptions',
#     'sale_report_product',
#     'sale_report_rewards',
#     'sale_report_promotions',
#     'sale_report_vouchers',
#     'sale_report_membership',
#     'sale_report_subscriptions',
# ]

ALL_PERMISSIONS = [
    'pos_root_access'
    'mobile_root_access'
    'account_root_access'
    'account_business_setting'
    'account_finance_setting'
    'account_service_management'
    'account_notification_setting'
    'inventory_root_access'
    'inventory_purchase_order'
    'inventory_goods_receipt'
    'inventory_consumption'
    'inventory_stock_transfer'
    'inventory_stock_report'
    'inventory_report'
    'target_control_staff'
    'target_control_store'
    'target_control_service'
    'target_control_retail'
    'reports_root_access'
    'reports_commission'
    'reports_staff'
    'reports_store'
    'reports_service'
    'reports_retail'
    'profile_root_access'
    'profile_list' 
    'product_root_access'
    'client_root_access'
    'client_list'
    'client_profile'
    'client_groups'
    'client_discount'
    'client_loyality'
    'client_reward'
    'client_sharing'
    'employee_root_access'
    'employee_new'
    'employee_payroll'
    'employee_attendance'
    'employee_staff_group'
    'employee_commission'
    'employee_work_schedule'
    'employee_vacation'
    'sales_root_access'
    'sales_apply_offer'
    'calender_appointment'
    'calender_block_time'
    
    'appointment',
    'email_staff',
    'products',
    'brand',
    'categories',
    'vendors',
    'stock',
    'stock_report',
    'staff_data',
    'staff_product_sales',
    'staff_product_sales',
    'staff_product_sales',
    'rewards',
    'promotions',
    'vouchers',
    'membership',
    'subscriptions',
    'sale_product',
    'sale_rewards',
    'sale_promotions',
    'sale_vouchers',
    'sale_membership',
    'sale_subscriptions',
    'sale_report_product',
    'sale_report_rewards',
    'sale_report_promotions',
    'sale_report_vouchers',
    'sale_report_membership',
    'sale_report_subscriptions',
]

# PERMISSIONS_MODEL_FIELDS = {
#     'appointment' : lambda employee_permission : employee_permission.appointment,
#     'email_staff' : lambda employee_permission : employee_permission.email_staff,
#     'products' : lambda employee_permission : employee_permission.products,
#     'brand' : lambda employee_permission : employee_permission.brand,
#     'categories' : lambda employee_permission : employee_permission.categories,
#     'vendors' : lambda employee_permission : employee_permission.vendors,
#     'stock' : lambda employee_permission : employee_permission.stock,
#     'stock_report' : lambda employee_permission : employee_permission.stock_report,
#     'staff_data' : lambda employee_permission : employee_permission.staff_data,
#     'staff_product_sales' : lambda employee_permission : employee_permission.staff_product_sales,
#     'staff_product_sales' : lambda employee_permission : employee_permission.staff_product_sales,
#     'staff_product_sales' : lambda employee_permission : employee_permission.staff_product_sales,
#     'rewards' : lambda employee_permission : employee_permission.rewards,
#     'promotions' : lambda employee_permission : employee_permission.promotions,
#     'vouchers' : lambda employee_permission : employee_permission.vouchers,
#     'membership' : lambda employee_permission : employee_permission.membership,
#     'subscriptions' : lambda employee_permission : employee_permission.subscriptions,
#     'sale_product' : lambda employee_permission : employee_permission.sale_product,
#     'sale_rewards' : lambda employee_permission : employee_permission.sale_rewards,
#     'sale_promotions' : lambda employee_permission : employee_permission.sale_promotions,
#     'sale_vouchers' : lambda employee_permission : employee_permission.sale_vouchers,
#     'sale_membership' : lambda employee_permission : employee_permission.sale_membership,
#     'sale_subscriptions' : lambda employee_permission : employee_permission.sale_subscriptions,
#     'sale_report_product' : lambda employee_permission : employee_permission.sale_report_product,
#     'sale_report_rewards' : lambda employee_permission : employee_permission.sale_report_rewards,
#     'sale_report_promotions' : lambda employee_permission : employee_permission.sale_report_promotions,
#     'sale_report_vouchers' : lambda employee_permission : employee_permission.sale_report_vouchers,
#     'sale_report_membership' : lambda employee_permission : employee_permission.sale_report_membership,
#     'sale_report_subscriptions' : lambda employee_permission : employee_permission.sale_report_subscriptions,
# }
     
PERMISSIONS_MODEL_FIELDS = {
    
    'appointment' : lambda employee_permission : employee_permission.appointment,
    'email_staff' : lambda employee_permission : employee_permission.email_staff,
    'products' : lambda employee_permission : employee_permission.products,
    'brand' : lambda employee_permission : employee_permission.brand,
    'categories' : lambda employee_permission : employee_permission.categories,
    'vendors' : lambda employee_permission : employee_permission.vendors,
    'stock' : lambda employee_permission : employee_permission.stock,
    'stock_report' : lambda employee_permission : employee_permission.stock_report,
    'staff_data' : lambda employee_permission : employee_permission.staff_data,
    'staff_product_sales' : lambda employee_permission : employee_permission.staff_product_sales,
    'staff_product_sales' : lambda employee_permission : employee_permission.staff_product_sales,
    'staff_product_sales' : lambda employee_permission : employee_permission.staff_product_sales,
    'rewards' : lambda employee_permission : employee_permission.rewards,
    'promotions' : lambda employee_permission : employee_permission.promotions,
    'vouchers' : lambda employee_permission : employee_permission.vouchers,
    'membership' : lambda employee_permission : employee_permission.membership,
    'subscriptions' : lambda employee_permission : employee_permission.subscriptions,
    'sale_product' : lambda employee_permission : employee_permission.sale_product,
    'sale_rewards' : lambda employee_permission : employee_permission.sale_rewards,
    'sale_promotions' : lambda employee_permission : employee_permission.sale_promotions,
    'sale_vouchers' : lambda employee_permission : employee_permission.sale_vouchers,
    'sale_membership' : lambda employee_permission : employee_permission.sale_membership,
    'sale_subscriptions' : lambda employee_permission : employee_permission.sale_subscriptions,
    'sale_report_product' : lambda employee_permission : employee_permission.sale_report_product,
    'sale_report_rewards' : lambda employee_permission : employee_permission.sale_report_rewards,
    'sale_report_promotions' : lambda employee_permission : employee_permission.sale_report_promotions,
    'sale_report_vouchers' : lambda employee_permission : employee_permission.sale_report_vouchers,
    'sale_report_membership' : lambda employee_permission : employee_permission.sale_report_membership,
    'sale_report_subscriptions' : lambda employee_permission : employee_permission.sale_report_subscriptions,
    
    'pos_root_access': lambda employee_permission : employee_permission.pos_root_access,
    'mobile_root_access' :  lambda employee_permission : employee_permission.mobile_root_access,
    'account_root_access': lambda employee_permission : employee_permission.account_root_access,
    'account_business_setting':  lambda employee_permission : employee_permission.account_business_setting,
    'account_finance_setting':  lambda employee_permission : employee_permission.account_finance_setting,
    'account_service_management': lambda employee_permission : employee_permission.account_service_management,
    'account_notification_setting':  lambda employee_permission : employee_permission.account_notification_setting,
    'inventory_root_access':  lambda employee_permission : employee_permission.inventory_root_access,
    'inventory_purchase_order':  lambda employee_permission : employee_permission.inventory_purchase_order,
    
    'inventory_goods_receipt': lambda employee_permission : employee_permission.inventory_goods_receipt,
    'inventory_consumption':  lambda employee_permission : employee_permission.inventory_consumption,
    'inventory_stock_transfer':  lambda employee_permission : employee_permission.inventory_stock_transfer,
    'inventory_stock_report':  lambda employee_permission : employee_permission.inventory_stock_report,
    'inventory_report': lambda employee_permission : employee_permission.inventory_report,
    'target_control_staff': lambda employee_permission : employee_permission.target_control_staff,
    'target_control_store':  lambda employee_permission : employee_permission.target_control_store,
    'target_control_service':  lambda employee_permission : employee_permission.target_control_service,
    
    'target_control_retail':  lambda employee_permission : employee_permission.target_control_retail,
    'reports_root_access':  lambda employee_permission : employee_permission.reports_root_access,
    'reports_commission':  lambda employee_permission : employee_permission.reports_commission,
    'reports_staff': lambda employee_permission : employee_permission.reports_staff,
    'reports_store': lambda employee_permission : employee_permission.reports_store,
    'reports_service':  lambda employee_permission : employee_permission.reports_service,
    
    'reports_retail':  lambda employee_permission : employee_permission.reports_retail,
    'profile_root_access':  lambda employee_permission : employee_permission.profile_root_access,
    'profile_list' :  lambda employee_permission : employee_permission.profile_list,
    'product_root_access':  lambda employee_permission : employee_permission.product_root_access,
    'client_root_access':  lambda employee_permission : employee_permission.client_root_access,
    'client_list': lambda employee_permission : employee_permission.client_list,
    
    'client_list': lambda employee_permission : employee_permission.client_list,
    'client_list': lambda employee_permission : employee_permission.client_list,
    
    'client_profile' : lambda employee_permission : employee_permission.client_profile,
    'client_groups' : lambda employee_permission : employee_permission.client_groups,
    'client_discount' : lambda employee_permission : employee_permission.client_discount,
    'client_reward' : lambda employee_permission : employee_permission.client_reward,
    'client_loyality' : lambda employee_permission : employee_permission.client_loyality,
    'client_sharing' : lambda employee_permission : employee_permission.client_sharing,
    
    'employee_root_access' : lambda employee_permission : employee_permission.employee_root_access,
    'employee_new' : lambda employee_permission : employee_permission.employee_new,
    'employee_payroll' : lambda employee_permission : employee_permission.employee_payroll,
    'employee_attendance' : lambda employee_permission : employee_permission.employee_attendance,
    'employee_staff_group' : lambda employee_permission : employee_permission.employee_staff_group,
    'employee_reports' : lambda employee_permission : employee_permission.employee_reports,
    'employee_commission' : lambda employee_permission : employee_permission.employee_commission,
    'employee_work_schedule' : lambda employee_permission : employee_permission.employee_work_schedule,
    
    'employee_vacation' : lambda employee_permission : employee_permission.employee_vacation,
    'sales_root_access' : lambda employee_permission : employee_permission.sales_root_access,
    'sales_apply_offer' : lambda employee_permission : employee_permission.sales_apply_offer,
    'calender_root_access' : lambda employee_permission : employee_permission.calender_root_access,
    'calender_appointment' : lambda employee_permission : employee_permission.calender_appointment,
    'calender_block_time' : lambda employee_permission : employee_permission.calender_block_time,
}