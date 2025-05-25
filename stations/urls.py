from django.urls import path
from .views import station_List_Fournisseur
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'stations'

urlpatterns = [
    path('station_List_Fournisseur/<str:username>', station_List_Fournisseur.as_view(), name='station_List_Fournisseur'),
    path('add_station/<str:username>', views.add_station, name='add_station'),
    path('delete_station/<int:ID_Station>/<str:username>', views.delete_station, name='delete_station'),
    path('update_station/<int:ID_Station>/<str:username>', views.update_station, name='update_station'),
    path('delete_photo/<int:ID_Station>/<int:photo_id>/<str:username>/', views.delete_photo, name='delete_photo'),
    path('station_List_ProprietaireVE',views.station_List_ProprietaireVE , name='station_List_ProprietaireVE'),
    path('station/<int:ID_Station>/<str:username>/reserve/', views.make_reservation, name='make_reservation'),
    path('reservation/<int:reservation_id>/confirmation/', views.reservation_confirmation, name='reservation_confirmation'),
    path('qrcode/<int:reservation_id>/', views.generate_qr_code, name='generate_qr_code'),
    path('user_reservations/<str:username>/', views.user_reservations, name='user_reservations'),
    path('station/<int:ID_Station>/<str:username>/reservations/', views.reservations, name='reservations'),
    # Change this line to use edit_review instead of add_review
    path('station/<int:ID_Station>/<str:username>/add_review/', views.edit_review, name='add_review'),
    # Keep this line as is
    path('station/<int:ID_Station>/<str:username>/edit_review/', views.edit_review, name='edit_review'),
    path('statistics/<int:ID_Station>/<str:username>/', views.station_statistics, name='station_statistics'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)