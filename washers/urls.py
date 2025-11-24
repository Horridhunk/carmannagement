from django.urls import path
from . import views

app_name = 'washers'
urlpatterns = [
    path('auth/', views.washer_auth_view, name='auth'),
    path('signup/', views.washer_signup_view, name='signup'),
    path('login/', views.washer_login_view, name='login'),
    path('logout/', views.washer_logout_view, name='logout'),
    path('dashboard/', views.washer_dashboard_view, name='dashboard'),
    path('start-wash/<int:order_id>/', views.start_wash_view, name='start_wash'),
    path('complete-wash/<int:order_id>/', views.complete_wash_view, name='complete_wash'),
    path('toggle-availability/', views.toggle_availability_view, name='toggle_availability'),
    path('profile/', views.washer_profile_view, name='profile'),
    path('debug-password/', views.debug_password_view, name='debug_password'),
    path('completed-orders/', views.washer_completed_orders_view, name='completed_orders'),
]