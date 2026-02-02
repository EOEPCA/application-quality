import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse


logger = logging.getLogger(__name__)


@login_required
def user_details(request):
    user_id = request.session["_auth_user_id"]
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
