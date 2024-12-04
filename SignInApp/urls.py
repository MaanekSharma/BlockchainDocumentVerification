from django.urls import path # type: ignore

from . import views

urlpatterns = [
        path("register/", views.RegisterView, name="registerPage"),
        path("", views.SignInView, name="signInPage"),
        path('success/', views.success, name='success')
]