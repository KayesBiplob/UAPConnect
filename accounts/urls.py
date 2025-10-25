# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("home/",views.home, name= "accounts_home"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),

    

    # forgot-password flow
    path("forgot-password/", views.send_password_reset_link,
         name="reset_password_via_email"),
    path("reset-password-confirm/", views.verify_password_reset_link,
         name="reset_password_confirm"),
    path("set-new-password/", views.set_new_password, name="set_new_password"),

    # account verification
    path("verify-account/", views.verify_account, name="verify_account"),
]
