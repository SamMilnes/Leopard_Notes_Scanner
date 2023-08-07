from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, UpdateView

from profiles.views_utils import get_request_user_profile, redirect_back

from .forms import CommentCreateModelForm, PostCreateModelForm, PostUpdateModelForm
from .models import Comment, Post
from .views_utils import (
    add_comment_if_submitted,
    add_post_if_submitted,
    get_post_id_and_post_obj,
    like_unlike_post,
)


@login_required
def post_comment_create_and_list_view(request):
    """
        Display the user's posts and allows creating comments.

        This view function displays the user's posts and provides forms to create comments on those posts.
        It also handles the submission of new posts and comments, redirecting back to the main page after submission.

        Args:
            request (HttpRequest): The incoming HTTP request object.

        Returns:
            HttpResponse: A rendered HTML response containing user's posts and comment forms.
    """
    qs = Post.objects.get_related_posts(user=request.user)
    profile = get_request_user_profile(request.user)

    p_form = PostCreateModelForm()
    c_form = CommentCreateModelForm()

    if add_post_if_submitted(request, profile):
        return redirect_back(request)

    if add_comment_if_submitted(request, profile):
        return redirect_back(request)

    context = {
        "qs": qs,
        "profile": profile,
        "p_form": p_form,
        "c_form": c_form,
    }

    return render(request, "posts/main.html", context)


@login_required
def switch_like(request):
    """
        Add or remove a like to/from a post

        This view function processes a POST request to add or remove a like from a post. It returns a JSON
        response indicating the total number of likes and whether a like was added or removed.

        Args:
            request (HttpRequest): The incoming HTTP request object.

        Returns:
            JsonResponse: JSON response containing total_likes and like_added status.
    """
    if request.method == "POST":
        post_id, post_obj = get_post_id_and_post_obj(request)
        profile = get_request_user_profile(request.user)

        like_added = like_unlike_post(profile, post_id, post_obj)

    # Return JSON response for AJAX script in like.js
    return JsonResponse(
        {"total_likes": post_obj.liked.count(), "like_added": like_added},
    )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """
        Delete a post by its primary key.

        This class-based view allows the deletion of a post by its primary key. It checks if the requesting user is the
        author of the post and handles error messages accordingly.

        Args:
            LoginRequiredMixin: A mixin to require login.
            DeleteView: A generic view for deleting an object.
    """

    model = Post
    template_name = "posts/confirm_delete.html"
    success_url = reverse_lazy("posts:main-post-view")

    def form_valid(self, *args, **kwargs):
        post = self.get_object()

        if post.author.user != self.request.user:
            messages.add_message(
                self.request,
                messages.ERROR,
                "You aren't allowed to delete this post",
            )
            return HttpResponseRedirect(self.success_url)

        self.object.delete()

        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Post deleted successfully!",
        )
        return HttpResponseRedirect(self.success_url)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """
        Delete a comment by its primary key.

        This class-based view allows the deletion of a comment by its primary key. It checks if the requesting user
        is the author of the comment and handles error messages accordingly. The view is identical to PostDeleteView.

        Args:
            LoginRequiredMixin: A mixin to require login.
            DeleteView: A generic view for deleting an object.
    """

    model = Comment

    def form_valid(self, *args, **kwargs):
        comment = self.get_object()

        if comment.profile.user != self.request.user:
            messages.add_message(
                self.request,
                messages.ERROR,
                "You aren't allowed to delete this comment",
            )
            return redirect_back(self.request)

        self.object.delete()

        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Comment deleted successfully!",
        )
        return redirect_back(self.request)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """
        Update a post by its primary key.

        This class-based view allows the updating of a post by its primary key. It checks if the requesting user is the
        author of the post and handles error messages accordingly. The view is identical to PostDeleteView.

        Args:
            LoginRequiredMixin: A mixin to require login.
            UpdateView: A generic view for updating an object.
    """

    model = Post
    form_class = PostUpdateModelForm
    template_name = "posts/update.html"
    success_url = reverse_lazy("posts:main-post-view")

    def form_valid(self, form):
        profile = get_request_user_profile(self.request.user)

        if form.instance.author != profile:
            messages.add_message(
                self.request,
                messages.ERROR,
                "You aren't allowed to update this post",
            )
            return HttpResponseRedirect(self.success_url)

        self.object = form.save()

        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Post updated successfully!",
        )
        return HttpResponseRedirect(self.success_url)

