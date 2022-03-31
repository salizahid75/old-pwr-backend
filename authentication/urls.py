from django.urls import re_path, path

from .views import register_view, login_view, user_view, verify_verification_code, resend_verification_code, logout_view

urlpatterns = [
    re_path('^register/?$', register_view, name="register"),
    re_path('^login/?$', login_view, name="login"),
    re_path('^logout/?$', logout_view, name="logout"),
    re_path("^user/?$", user_view, name="user"),
    re_path("^resend-verification/?$", resend_verification_code, name="resend_verification"),
    re_path('^verify-email/?$', verify_verification_code, name="verify-email")
]