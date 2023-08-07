from .models import Relationship
from .views_utils import get_request_user_profile


def profile_pic(request):
    """
        Get the profile picture (avatar) for the authenticated user.

        Args:
            request (HttpRequest): The request object representing the current HTTP request.

        Returns:
            dict: A dictionary containing the profile picture (avatar) URL under the key 'profile_pic'.
                  An empty dictionary is returned if the user is not authenticated.
    """
    if request.user.is_authenticated:
        profile = get_request_user_profile(request.user)

        pic = profile.avatar

        return {"profile_pic": pic}
    return {}


def invitations_received_count(request):
    """
       Get the count of invitations received by the authenticated user.

       Args:
           request (HttpRequest): The request object representing the current HTTP request.

       Returns:
           dict: A dictionary containing the count of invitations received by the user under the key
            'invitations_received_count'.
                 An empty dictionary is returned if the user is not authenticated.
   """
    if request.user.is_authenticated:
        profile = get_request_user_profile(request.user)

        result = Relationship.objects.invitations_received(profile).count()

        return {"invitations_received_count": result}
    return {}
