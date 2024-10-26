from django.urls import path
from .views import UserSignupView, UserLoginView

urlpatterns = [
    path("signup/", view=UserSignupView.as_view(), name="user-signup"),
    path("login/", view=UserLoginView.as_view(), name="user-login"),
]
