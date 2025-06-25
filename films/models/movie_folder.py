from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User

from .mixins import UpdatedAtMixin, CreatedAtMixin

class MovieFolder(
    CreatedAtMixin,
    UpdatedAtMixin,
    models.Model
):
    WATCHED = "watch"
    WATCHING = "watching"
    WANT = "want"

    STATUS_CHOICES = [
        (WATCHED, "Watched"),
        (WATCHING, "Watching"),
        (WANT, "Want to watch"),
    ]

    user = models.ForeignKey(
        User,
        related_name="movie_folders",
        on_delete=models.CASCADE,
        null=True
    )
    film = models.ForeignKey(
        "Film",
        related_name="folder",
        on_delete=models.PROTECT,
        null=False,
    )
    added_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        null=False,
    )
    rating = models.PositiveSmallIntegerField(
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    review = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "film_folder"
        unique_together = ("user", "film")

        indexes = [
            models.Index(
                name="ix_films_user_id_status",
                fields=["user", "status"],
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.film.title} ({self.status})"

    @property
    def is_watching(self) -> bool:
        return self.status == self.WATCHING




