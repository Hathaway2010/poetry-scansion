
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("poem/<int:id>", views.poem, name="poem"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("import_poem", views.import_poem, name="import_poem"),
    path("about", views.about, name="about"),
    path("choose_poem", views.choose_poem, name="choose_poem")
]
