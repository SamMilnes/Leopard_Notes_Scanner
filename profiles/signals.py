from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Profile, Relationship


@receiver(post_save, sender=User)
def post_save_create_profile(sender, instance, created, **kwargs):
    """
        Create a user profile when a User instance is created.

        Args:
            sender (Model): The sender model class (User).
            instance (User): The User instance being saved.
            created (bool): Indicates whether the instance was newly created.
            **kwargs: Additional keyword arguments.

        Returns:
            None
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Relationship)
def post_save_add_to_friends(sender, instance, created, **kwargs):
    """
        Add profiles to each other's friend list when a Relationship instance with status "accepted" is created.

        Args:
            sender (Model): The sender model class (Relationship).
            instance (Relationship): The Relationship instance being saved.
            created (bool): Indicates whether the instance was newly created.
            **kwargs: Additional keyword arguments.

        Returns:
            None
    """

    relship_sender_profile = instance.sender
    relship_receiver_profile = instance.receiver
    if instance.status == "accepted":
        relship_sender_profile.friends.add(relship_receiver_profile.user)
        relship_receiver_profile.friends.add(relship_sender_profile.user)

        relship_sender_profile.save()
        relship_receiver_profile.save()


@receiver(pre_delete, sender=Relationship)
def pre_delete_remove_from_friends(sender, instance, **kwargs):
    """
        Delete profiles from each other's friend list when a Relationship instance is deleted.

        Args:
            sender (Model): The sender model class (Relationship).
            instance (Relationship): The Relationship instance being deleted.
            **kwargs: Additional keyword arguments.

        Returns:
            None
    """
    relship_sender_profile = instance.sender
    relship_receiver_profile = instance.receiver

    relship_sender_profile.friends.remove(relship_receiver_profile.user)
    relship_receiver_profile.friends.remove(relship_sender_profile.user)

    relship_sender_profile.save()
    relship_receiver_profile.save()
