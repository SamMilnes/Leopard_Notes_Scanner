from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from django.core.validators import FileExtensionValidator

from .models_utils import get_likes_received_count, get_list_of_profiles_by_user


class ProfileManager(models.Manager):
    """
        Custom manager for the Profile model, providing methods to retrieve friend profiles.
    """
    def get_my_friends_profiles(self, user):
        """
            Get profiles of friends associated with the given user.

            Args:
                user (User): The user for whom to retrieve friend profiles.

            Returns:
                QuerySet: QuerySet containing profiles of friends.
        """
        users = Profile.objects.get(user=user).friends.all()
        profiles = get_list_of_profiles_by_user(users)
        return profiles


class Profile(models.Model):
    """
        Model representing user profiles.
    """

    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="No Bio..", max_length=300, blank=True)
    email = models.EmailField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(
        default="avatar.png",
        upload_to="avatars/",
        validators=[FileExtensionValidator(["png", "jpg", "jpeg"])],
    )
    friends = models.ManyToManyField(User, blank=True, related_name="friends")
    following = models.ManyToManyField(
        User,
        blank=True,
        related_name="following",
    )
    followers = models.ManyToManyField(
        User,
        blank=True,
        related_name="followers",
    )
    slug = models.SlugField(unique=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ProfileManager()

    def __str__(self):
        """
            Return a string representation of the profile.
        """
        return f"{self.user.username}"

    def get_absolute_url(self):
        """
           Get the URL for the profile's detail view.

           Returns:
               str: The URL for the profile's detail view.
        """
        return reverse(
            "profiles:profile-detail-view",
            kwargs={"slug": self.slug},
        )

    def save(self, *args, **kwargs):
        """
            Override the save method to set the slug field and call the parent's save method.
        """
        self.slug = str(self.user)
        super().save(*args, **kwargs)

    def get_likes_given_count(self):
        """
            Get the count of likes given by the user.

            Returns:
                int: Count of likes given by the user.
        """
        likes = self.like_set.all()

        total_liked = likes.count()

        return total_liked

    def get_likes_received_count(self):
        """
            Get the count of likes received by the user.

            Returns:
                int: Count of likes received by the user.
        """
        posts = self.posts.all()

        total_liked = get_likes_received_count(posts)

        return total_liked


class RelationshipManager(models.Manager):
    """
        Custom manager for the Relationship model, providing methods to query friend requests.
    """
    def invitations_received(self, receiver):
        """
            Get friend requests received by the specified receiver.

            Args:
                receiver (Profile): The receiver profile for whom to retrieve friend requests.

            Returns:
                QuerySet: QuerySet containing friend requests received by the receiver.
        """
        qs = Relationship.objects.filter(receiver=receiver, status="sent")
        return qs

    def invitations_sent(self, sender):
        """
            Get friend requests sent by the specified sender.

            Args:
                sender (Profile): The sender profile for whom to retrieve sent friend requests.

            Returns:
                QuerySet: QuerySet containing friend requests sent by the sender.
        """
        qs = Relationship.objects.filter(sender=sender, status="sent")
        return qs


STATUS_CHOICES = (
    ("sent", "sent"),
    ("accepted", "accepted"),
)


class Relationship(models.Model):
    """
        Model representing friend relationships.
    """

    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="receiver",
    )
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = RelationshipManager()

    def __str__(self):
        """
            Return a string representation of the relationship.
        """
        return f"{self.sender} - {self.receiver} - {self.status}"


class Message(models.Model):
    """
        Model representing chat messages.
    """

    sender = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="message_sender",
    )
    receiver = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="message_receiver",
    )
    content = models.TextField(max_length=200)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
            Return a string representation of the message.
        """
        if len(str(self.content)) > 50:
            return f"{self.sender} - {str(self.content)[:50].strip()}.."
        return f"{self.sender} - {str(self.content)}"


class OCRImage(models.Model):
    """
        Model representing OCR images.
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='ocr_images')
    title = models.CharField(max_length=100, default="Untitled")
    ocr_text = models.TextField(max_length=200)
    uploaded_image = models.ImageField(upload_to='media/ocr_images/')
    fully_segmented_image = models.ImageField(upload_to='media/fully_segmented_images/', null=True, blank=True)
    isSnipped = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
            Return a string representation of the OCR image.
        """
        return self.title

