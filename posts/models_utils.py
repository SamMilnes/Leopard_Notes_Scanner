from profiles.models import Profile


def get_related_posts_queryset(profile, friends, following):
    """
        Generate a combined queryset of posts related to a given profile, their friends, and those they follow.

        This function retrieves posts authored by the given profile, their friends, and profiles they follow,
        creating a single queryset containing these posts sorted by their creation time.

        Args:
            profile (Profile): The main profile for which related posts are to be fetched.
            friends (QuerySet[User]): A queryset of User objects representing the main profile's friends.
            following (QuerySet[User]): A queryset of User objects representing users the main profile follows.

        Returns:
            QuerySet[Post]: A combined queryset containing posts from the main profile, their friends, and followed profiles,
                            ordered by creation time in descending order.
    """

    from .models import Post

    unique_profiles = set()
    querysets = []
    post_pks = []

    for user in friends:
        unique_profiles.add(Profile.objects.get(user=user))

    for user in following:
        unique_profiles.add(Profile.objects.get(user=user))

    querysets.append(profile.posts.all())

    for unique_profile in unique_profiles:
        querysets.append(unique_profile.posts.all())

    for queryset in querysets:
        for post in queryset:
            post_pks.append(post.pk)

    result = Post.objects.filter(pk__in=post_pks).order_by("-created")

    return result
