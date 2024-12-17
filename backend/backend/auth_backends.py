from django.conf import settings
from django.utils.crypto import get_random_string
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
import logging

logger = logging.getLogger(__name__)


class CustomOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = super().create_user(claims)
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.username = claims.get("preferred_username", claims["sub"])
        logger.info(f"Creating user with username '{user.username}'")
        user.save()
        return user


def logout_next_url(request):
    url = (
        f'{settings.OIDC_OP_USER_ENDPOINT.replace("userinfo", "logout")}'
        "?response_type=code"
        f"&client_id={settings.OIDC_RP_CLIENT_ID}"
        f"&post_logout_redirect_uri={settings.OIDC_POST_LOGOUT_REDIRECT_URL}"
        f"&state={get_random_string(32)}"
    )
    logger.info("Logout next URL: %s", url)
    return url
