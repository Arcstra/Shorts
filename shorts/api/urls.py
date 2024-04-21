from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views


urlpatterns = [
    path("test/", views.testView, name="test"),
    path("short/", views.shortView, name="short"),
    path("short/<int:id>", views.shortIDView, name="shortID"),
    path("short/client/", views.shortClientView, name="shortClient"),
    path("short/rating/", csrf_exempt(views.ShortRatingView.as_view()), name="shortRating"),
    path("client/", views.clientView, name="client"),
    path("client/<int:id>", views.clientIDView, name="clientID"),
    path("image/<str:name>", views.imageView, name="image"),
    # path("register/", views.registerClientView.as_view(), name="register"),
    path("auth/editPassword/", views.EditPasswordView.as_view(), name="editPassword"),
]
