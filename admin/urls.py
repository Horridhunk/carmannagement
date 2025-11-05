from django.urls import path
from . import views

app_name = 'carwash_admin'

urlpatterns = [
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),
    path('dashboard/', views.admin_dashboard_view, name='dashboard'),
    path('base/', views.admin_base_view, name='base'),  # Base template view
    path('clients/', views.manage_clients_view, name='manage_clients'),
    path('clients/delete/<int:client_id>/', views.delete_client_view, name='delete_client'),
    path('washers/', views.manage_washers_view, name='manage_washers'),
    path('washers/add/', views.add_washer_view, name='add_washer'),
    path('washers/edit/<int:washer_id>/', views.edit_washer_view, name='edit_washer'),
    path('washers/delete/<int:washer_id>/', views.delete_washer_view, name='delete_washer'),
    path('washers/toggle/<int:washer_id>/', views.toggle_washer_status_view, name='toggle_washer_status'),
    path('orders/', views.manage_orders_view, name='manage_orders'),
    path('orders/assign/<int:order_id>/', views.assign_washer_view, name='assign_washer'),
    path('orders/cancel/<int:order_id>/', views.cancel_order_view, name='cancel_order'),
    path('appointments/', views.manage_appointments_view, name='manage_appointments'),
    path('appointments/cancel/<int:appointment_id>/', views.cancel_appointment_admin_view, name='cancel_appointment'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('', views.admin_dashboard_view, name='dashboard'),  # Default admin page
]