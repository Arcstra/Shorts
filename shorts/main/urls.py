from django.urls import path
from . import views


urlpatterns = [
    path("page/<int:page>", views.mainView, name="main"),
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/code/", views.RegisterCodeView.as_view(), name="registerCode"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/editPassword/", views.EditPasswordView.as_view(), name="editPassword"),
    path("auth/logout/", views.logoutView, name="logout"),
    path("addShort/", views.AddShortView.as_view(), name="addShort"),
    path("profile/", views.getProfileView, name="profile"),
]
