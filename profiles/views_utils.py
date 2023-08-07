from django.shortcuts import redirect

from .forms import ProfileModelForm
from .models import Message, Profile, Relationship


def get_request_user_profile(request_user):
    """
        Retrieve the user's profile associated with the given request user.

        Args:
            request_user (User): The user for whom to retrieve the profile.

        Returns:
            Profile: The user's profile.
    """
    user = Profile.objects.get(user=request_user)
    return user


def get_profile_form_by_request_method(request, profile):
    """
        Get the appropriate ProfileModelForm based on the HTTP request method.

        Args:
            request (HttpRequest): The HTTP request object.
            profile (Profile): The profile instance to be used for the form.

        Returns:
            ProfileModelForm: An instance of ProfileModelForm populated with data
                              based on the request method.
    """
    if request.method == "POST":
        form = ProfileModelForm(request.POST, request.FILES, instance=profile)
    else:
        form = ProfileModelForm(instance=profile)
    return form


def get_profiles_by_users_list(users):
    """
        Retrieve a list of profiles associated with the given list of users.

        Args:
            users (list): A list of User objects.

        Returns:
            list: A list of Profile objects corresponding to the provided users.
    """
    result = [Profile.objects.get(user=user) for user in users]
    return result


def check_if_friends(profile, request_user):
    """
        Check if two users are friends.

        Args:
            profile (Profile): The profile to check for friendship.
            request_user (User): The user to be checked for friendship.

        Returns:
            bool: True if the request user is in the profile's friends and vice versa, False otherwise.
    """
    return request_user in profile.friends.all()


def get_friends_of_user(user):
    """
        Get the list of profiles representing the friends of the given user.

        Args:
            user (User): The user for whom to retrieve the friends' profiles.

        Returns:
            list: A list of Profile objects representing the user's friends.
    """
    request_user_profile = Profile.objects.get(user=user)
    friends_users = request_user_profile.friends.all()
    friends_profiles = get_profiles_by_users_list(friends_users)
    return friends_profiles


def get_profile_by_pk(request):
    """
        Get a profile by its primary key extracted from the request.

        Args:
            request (HttpRequest): The HTTP request object containing the "pk" parameter.

        Returns:
            Profile: The profile instance corresponding to the provided primary key.
    """
    pk = request.POST.get("pk")
    profile = Profile.objects.get(pk=pk)
    return profile


def get_received_invites(profile):
    """
        Get a list of profiles that have sent friendship invitations to the given profile.

        Args:
            profile (Profile): The profile for which to retrieve received invitations.

        Returns:
            list: A list of Profile objects representing users who sent invitations.
    """
    qs = Relationship.objects.invitations_received(profile)
    results = list(map(lambda x: x.sender, qs))
    return results


def get_sent_invites(profile):
    """
        Get a list of profiles to which the given profile has sent friendship invitations.

        Args:
            profile (Profile): The profile for which to retrieve sent invitations.

        Returns:
            list: A list of Profile objects representing users to whom invitations were sent.
    """
    qs = Relationship.objects.invitations_sent(profile)
    results = list(map(lambda x: x.receiver, qs))
    return results


def follow_unfollow(my_profile, profile):
    """
        Follow or unfollow a profile based on the existing relationship.

        Args:
            my_profile (Profile): The user's own profile.
            profile (Profile): The profile to follow or unfollow.
    """
    if profile.user in my_profile.following.all():
        my_profile.following.remove(profile.user)
        profile.followers.remove(my_profile.user)
    else:
        my_profile.following.add(profile.user)
        profile.followers.add(my_profile.user)


def redirect_back(request):
    """
        Redirect to the previous page (HTTP_REFERER) or a default location.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponseRedirect: A redirection response.
    """
    return redirect(request.META.get("HTTP_REFERER", "/"))


def get_relationship_users(profile):
    """
        Get the users related to the given profile based on relationship status.

        Args:
            profile (Profile): The profile for which to retrieve relationship users.

        Returns:
            tuple: A tuple containing two lists - invited_users and incoming_invite_users.
    """
    relship_sent = Relationship.objects.filter(sender=profile, status="sent")
    relship_received = Relationship.objects.filter(
        receiver=profile,
        status="sent",
    )

    invited_users = [i.receiver.user for i in relship_sent]
    incoming_invite_users = [i.sender.user for i in relship_received]

    return invited_users, incoming_invite_users


def get_received_messages(sender, receiver):
    """
        Get the content of messages sent from the sender to the receiver.

        Args:
            sender (User): The user sending the messages.
            receiver (User): The user receiving the messages.

        Returns:
            list: A list of message contents between the sender and receiver.
    """
    messages = Message.objects.filter(sender=sender, receiver=receiver)
    return messages.values_list("content", flat=True)
