from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from .mixins import UpdatedAtMixin, CreatedAtMixin


class Film(
    CreatedAtMixin,
    UpdatedAtMixin,
    models.Model,
):
    title = models.CharField(max_length=255, db_index=True)
    director = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    genres = models.CharField(max_length=255, null=True, blank=True)
    rating = models.CharField(max_length=7, null=True, blank=True)
    release = models.IntegerField(null=True, blank=True)
    cover_url = models.URLField(null=True, blank=True)
    views = models.PositiveIntegerField(default=0)

    tags = models.ManyToManyField(
        "Tag",
        related_name="films",
        blank=True,
    )

    grade = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )

    review = models.TextField(null=True, blank=True)
    class Meta:
        db_table = "films"

    def __str__(self):
        return self.title




