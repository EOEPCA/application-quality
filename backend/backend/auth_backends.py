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
