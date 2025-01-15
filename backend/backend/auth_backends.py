import logging

from django.conf import settings
from django.utils.crypto import get_random_string
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


logger = logging.getLogger(__name__)


class CustomOIDCAuthenticationBackend(OIDCAuthenticationBackend):

    def verify_claims(self, claims):
        if "email" not in claims:
            username = claims.get("preferred_username", claims["sub"])
            claims["email"] = f"{username}@example.com"
        logger.info(f"Claims to verify: {claims}")
        return super().verify_claims(claims)

    def create_user(self, claims):
        user = super().create_user(claims)
        user.username = claims.get("preferred_username", claims["sub"])
        user.first_name = claims.get("given_name", user.username)
        user.last_name = claims.get("family_name", "")
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
