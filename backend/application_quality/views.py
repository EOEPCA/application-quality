import logging

from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, HASH_SESSION_KEY, SESSION_KEY
from django.contrib.auth.models import AnonymousUser, User
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.module_loading import import_string
from http import HTTPStatus


logger = logging.getLogger(__name__)


def user_details(request):
    user_id = request.session.get("_auth_user_id", None)
    if user_id is None:
        message = "User not authenticated"
        logging.error(message)
        return JsonResponse({"error": message}, status=HTTPStatus.UNAUTHORIZED)
    
    logging.info("Retrieving details of user with ID %s", user_id)
    user = User.objects.get(pk=user_id)
    user_info = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'is_admin': user.is_staff,
        'is_superuser': user.is_superuser,
    }
    return JsonResponse(user_info)


def logout(request):
    # Replaces the default logout function to prevent ending the local user session
    # in the case the user decides not to log out ("Back to Application" link)
    logging.info("Custom logout %s", request)
    logout_url = settings.LOGOUT_REDIRECT_URL
    if request.user.is_authenticated:
        # Build the OP logout URL first: it may need the stored id_token
        logout_from_op = settings.OIDC_OP_LOGOUT_URL_METHOD
        if logout_from_op:
            logout_url = import_string(logout_from_op)(request)
    return HttpResponseRedirect(logout_url)


def post_logout(request):
    # Called by redirection after logout confirmation in OIDC Provider.
    logging.info("Custom post-logout %s", request)
    if request.user.is_authenticated:
        # Drop the Django auth keys and the OIDC tokens/state, keep the rest
        for key in (SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY):
            request.session.pop(key, None)
        for key in [k for k in request.session.keys() if k.startswith("oidc_")]:
            del request.session[key]
        request.user = AnonymousUser()

    return HttpResponseRedirect(settings.PUBLIC_URL)
