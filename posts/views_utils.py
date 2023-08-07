from .forms import CommentCreateModelForm, PostCreateModelForm
from .models import Like, Post


def add_post_if_submitted(request, profile):
    """
        Add a new post if the post submission form is submitted.

        Args:
            request (HttpRequest): The HTTP request object containing form data.
            profile (Profile): The user profile associated with the post author.

        Returns:
            bool: True if the post was successfully created and saved, False otherwise.
    """
    if "submit_p_form" in request.POST:

        p_form = PostCreateModelForm(request.POST, request.FILES)

        if p_form.is_valid():
            instance = p_form.save(commit=False)
            instance.author = profile
            instance.save()

            p_form = PostCreateModelForm()

            return True


def add_comment_if_submitted(request, profile):
    """
        Add a new comment if the comment submission form is submitted.

        Args:
            request (HttpRequest): The HTTP request object containing form data.
            profile (Profile): The user profile associated with the comment author.

        Returns:
            bool: True if the comment was successfully created and saved, False otherwise.
    """
    if "submit_c_form" in request.POST:

        c_form = CommentCreateModelForm(request.POST)

        if c_form.is_valid():
            instance = c_form.save(commit=False)
            instance.profile = profile
            instance.post = Post.objects.get(id=request.POST.get("post_id"))
            instance.save()

            c_form = CommentCreateModelForm()

            return True


def get_post_id_and_post_obj(request):
    """
        Retrieve the post ID and corresponding Post object based on the request.

        Args:
            request (HttpRequest): The HTTP request object containing the post ID.

        Returns:
            tuple: A tuple containing the post ID (str) and Post object (Post).
    """
    post_id = request.POST.get("post_id")
    post_obj = Post.objects.get(id=post_id)
    return post_id, post_obj


def like_unlike_post(profile, post_id, post_obj):
    """
        Handle liking or unliking a post by a user.

        Args:
            profile (Profile): The user profile performing the like/unlike action.
            post_id (str): The ID of the post being liked/unliked.
            post_obj (Post): The Post object being liked/unliked.

        Returns:
            bool: True if the like was added, False if it was removed.
    """
    if profile in post_obj.liked.all():
        post_obj.liked.remove(profile)
        like_added = False
    else:
        post_obj.liked.add(profile)
        like_added = True

    like, created = Like.objects.get_or_create(profile=profile, post_id=post_id)

    if not created:
        like.delete()
    else:
        like.save()
        post_obj.save()

    return like_added
