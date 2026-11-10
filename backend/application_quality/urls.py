from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from application_quality.views import logout, post_logout, user_details

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("backend.urls")),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if settings.IS_OIDC_ENABLED:
    urlpatterns.extend([
        path("oidc/user-details/", user_details, name="user_details"),
        # Overwrite the default logout function to prevent ending the local user session
        # in the case the user decides not to log out ("Back to Application" link)
        path("oidc/logout/", logout, name="oidc_logout"),
        path("oidc/post-logout/", post_logout, name="oidc_post_logout"),
        path("oidc/", include("mozilla_django_oidc.urls")),
    ])
