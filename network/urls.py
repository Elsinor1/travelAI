
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<int:user_id>", views.display_user, name="display_user"),
    path("following", views.following, name="following"),

    # API's
    path("follow/<int:user_id>", views.follow_user, name="follow_user"),
    path("like/<int:post_id>", views.like_post, name="like_post"),
    path("save/<int:post_id>", views.edit_post, name="save_edit"),
]
