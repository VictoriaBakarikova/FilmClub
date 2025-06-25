from django.contrib.auth.models import User
from django.db import models

from .mixins import CreatedAtMixin

class Comment(
    CreatedAtMixin,
    models.Model
):
    film = models.ForeignKey(
        "films.Film",
        on_delete=models.CASCADE,
        related_name="comments",
        null=False,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )

    content = models.TextField()
    tagged_user=models.ManyToManyField(
        User,
        related_name="tagged_in_comments",
        blank=True,
    )

    class Meta:
        db_table = "comments"

    @property
    def likes_count(self) -> int:
        return self.likes.count()

    def is_liked_by(self, user: User) -> bool:
        return self.likes.filter(user=user).exists()


class CommentLike(
    CreatedAtMixin,
    models.Model
):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )



    class Meta:
        db_table = "comments_likes"
        unique_together = ("comment", "user")