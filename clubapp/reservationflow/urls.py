from django.urls import path

from . import views

urlpatterns = [
    path("", views.CalendarDetailView.as_view(), name="calendar_month"),
    path("create/", views.ReservationCreateView.as_view(), name="reservation_create"),
    path("list/", views.ReservationsListView.as_view(), name="reservation_list"),
    path("list/staff/", views.StaffReservationsListView.as_view(), name="staff_reservation_list"),
    path("update/<int:pk>/", views.ReservationUpdateView.as_view(), name="reservation_update"),
    path("delete/<int:pk>/", views.ReservationDeleteView.as_view(), name="reservation_delete"),
]
