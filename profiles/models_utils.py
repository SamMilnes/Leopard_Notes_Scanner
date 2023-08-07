def get_list_of_profiles_by_user(users):
    """
        Get a list of profiles associated with the given list of users.

        Args:
            users (list): List of User instances for whom to retrieve profiles.

        Returns:
            list: A list of Profile instances corresponding to the provided users.
    """
    result = []

    for user in users:
        from .models import Profile

        result.append(Profile.objects.get(user=user))

    return result


def get_likes_received_count(posts):
    """
        Get the total count of likes received by posts.

        Args:
            posts (QuerySet): QuerySet containing the posts for which to count likes.

        Returns:
            int: Total count of likes received by the provided posts.
    """
    total_liked = 0
    for post in posts:
        total_liked += post.liked.all().count()

    return total_liked
