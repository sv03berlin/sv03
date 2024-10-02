from django.urls import path

from clubapp.clubwork import views

urlpatterns = [
    path("", views.clubwork_index, name="clubwork_index"),
    path("all/", views.AllClubworkHistoryView.as_view(), name="clubwork_all"),
    path("add/", views.add_clubwork, name="add_clubwork"),
    path("mod/<int:pk>/", views.mod_clubwork, name="mod_clubwork"),
    path("register_member/<int:pk>/", views.register_user, name="register_member"),
    path("add_own/", views.OwnClubWorkCreate.as_view(), name="add_own_clubwork"),
    path("mod_own/<int:pk>/", views.OwnClubWorkUpdate.as_view(), name="mod_own_clubwork"),
    path("delete/<int:pk>/", views.ClubWorkDelete.as_view(), name="delete_clubwork"),
    path("delete_own/<int:pk>/", views.OwnClubWorkDelete.as_view(), name="delete_own_clubwork"),
    path("register/<int:pk>/", views.register_for_clubwork, name="register"),
    path("unregister/<int:pk>/", views.unregister_for_clubwork, name="unregister"),
    path("approve/", views.approve_clubwork_overview, name="approve_clubwork_overview"),
    path("approve/<int:pk>/", views.approve_clubwork, name="approve_clubwork"),
    path("clubwork_history/", views.ClubworkHistoryView.as_view(), name="clubwork_history"),
    path("clubwork_user_history/", views.UserHistroyView.as_view(), name="clubwork_user_history"),
    path("select_user_mail/<int:pk>/", views.select_users_to_email_about, name="select_user_mail"),
    path("download/<int:year>/", views.download_xlsx_view, name="download"),
    path("update_hours/<int:pk>", views.HourUpdateView.as_view(), name="update_hours"),
    path(
        "unregister_user/<int:clubwork_id>/<int:user_id>",
        views.unregister_user_for_clubwork,
        name="unregister_user_for_clubwork",
    ),
    path(
        "ressort_register_own_clubwork/",
        views.OtherUserClubWorkCreationForm.as_view(),
        name="ressort_register_own_clubwork",
    ),
]
