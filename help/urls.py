from django.urls import path
from . import views

app_name = 'help'

urlpatterns = [
    path('', views.help_home, name='help_home'),
    path('faq/', views.faq_list, name='faq_list'),
    path('tutorials/', views.tutorial_list, name='tutorial_list'),
    path('tutorials/<int:tutorial_id>/', views.tutorial_detail, name='tutorial_detail'),
    path('troubleshooting/', views.troubleshooting_list, name='troubleshooting_list'),
    path('support/', views.support_home, name='support_home'),
    path('support/create/', views.create_ticket, name='create_ticket'),
    path('support/ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    # Ajoutez cette URL à la fin de urlpatterns
    path('permission-denied/', views.permission_denied, name='permission_denied'),
    path('admin/tickets/', views.admin_tickets, name='admin_tickets'),
    path('admin/tickets/<int:ticket_id>/', views.admin_ticket_detail, name='admin_ticket_detail'),
]