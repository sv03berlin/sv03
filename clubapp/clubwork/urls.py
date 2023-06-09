from django.urls import path

from clubapp.clubwork import views

urlpatterns = [
    path("", views.clubwork_index, name="clubwork_index"),
    path("add/", views.add_clubwork, name="add_clubwork"),
    path("mod/<int:pk>/", views.mod_clubwork, name="mod_clubwork"),
    path("add_own/", views.add_own_clubwork, name="add_own_clubwork"),
    path("mod_own/<int:pk>/", views.mod_own_clubwork, name="mod_own_clubwork"),
    path("register/<int:pk>/", views.register_for_clubwork, name="register"),
    path("unregister/<int:pk>/", views.unregister_for_clubwork, name="unregister"),
    path("approve/", views.approve_clubwork_overview, name="approve_clubwork_overview"),
    path("approve/<int:pk>/", views.approve_clubwork, name="approve_clubwork"),
    path("clubwork_history/", views.history, name="clubwork_history"),
    path("clubwork_user_history/", views.user_history, name="clubwork_user_history"),
]
