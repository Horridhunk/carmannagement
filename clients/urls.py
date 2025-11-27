from django.urls import path
from . import views

app_name = 'clients'
urlpatterns = [
    path('', views.index_view, name='home'),  # Root URL goes to index page
    path('home/', views.home_view, name='home_links'),  # System links page
    path('clients/', views.clients, name='clients'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('guest-login/', views.guest_login_view, name='guest_login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('index/', views.index_view, name='index'),
    path('services/', views.services_view, name='services'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uuid:token>/', views.reset_password_view, name='reset_password'),
    path('vehicles/', views.manage_vehicles_view, name='manage_vehicles'),
    path('vehicles/add/', views.add_vehicle_view, name='add_vehicle'),
    path('book-wash/', views.book_wash_view, name='book_wash'),
    path('track-order/<int:order_id>/', views.track_order_view, name='track_order'),
    path('order-history/', views.order_history_view, name='order_history'),
    path('schedule/', views.schedule_appointment_view, name='schedule_appointment'),
    path('appointments/', views.my_appointments_view, name='my_appointments'),
    path('appointments/cancel/<int:appointment_id>/', views.cancel_appointment_view, name='cancel_appointment'),
    path('appointments/reschedule/<int:appointment_id>/', views.reschedule_appointment_view, name='reschedule_appointment'),
    path('reviews/add/<int:order_id>/', views.add_review_view, name='add_review'),
    path('reviews/', views.view_reviews_view, name='view_reviews'),
    path('profile/', views.client_profile_view, name='profile'),
]
