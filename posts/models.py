from django.core.validators import FileExtensionValidator
from django.db import models

from profiles.models import Profile
from profiles.views_utils import get_request_user_profile

from .models_utils import get_related_posts_queryset


class PostManager(models.Manager):
    """
        A custom manager for the Post model that provides methods for retrieving related posts.
    """
    def get_related_posts(self, user):
        """
            Retrieve a queryset of related posts based on the user's profile, friends, and following.

            Args:
                user (User): The user for whom related posts are to be fetched.

            Returns:
                QuerySet: A queryset containing related posts.
        """
        profile = get_request_user_profile(user)
        friends = profile.friends.all()
        following = profile.following.all()

        related_posts = get_related_posts_queryset(profile, friends, following)

        return related_posts


class Post(models.Model):
    """
    Represents a post made by a user.
    """

    content = models.TextField()
    image = models.ImageField(
        blank=True,
        upload_to="posts",
        validators=[FileExtensionValidator(["png", "jpg", "jpeg"])],
    )
    liked = models.ManyToManyField(Profile, blank=True, related_name="likes")
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = PostManager()

    def __str__(self):
        """
            Returns a string representation of the post, truncating content if it's too long.

            Returns:
                str: A concise string representation of the post.
        """
        if len(str(self.content)) > 50:
            return f"{self.author} - {str(self.content)[:50].strip()}.."
        return f"{self.author} - {str(self.content)}"

    def num_comments(self):
        """
            Calculate the number of comments on the post.

            Returns:
                int: The number of comments on the post.
        """
        return self.comment_set.all().count()

    class Meta:
        ordering = ("-created",)


class Comment(models.Model):
    """
    Represents a comment on a post.
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField(max_length=300)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
            Returns a string representation of the comment.

            Returns:
                str: A string representation of the comment.
        """
        return f"{self.profile} - {self.content}"


class Like(models.Model):
    """
    Represents a like left on a post.
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
           Returns a string representation of the like.

           Returns:
               str: A string representation of the like.
       """
        return f"{self.profile} liked {self.post}"
