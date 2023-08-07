from django import forms

from .models import Message, Profile, OCRImage


class ProfileModelForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "bio", "avatar")


class MessageModelForm(forms.ModelForm):
    content = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Send a message.."}),
    )
    ocr_image_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Message
        fields = ["content", "ocr_image_id"]

