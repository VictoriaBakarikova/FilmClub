from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Exists, OuterRef, QuerySet

from .mixins import UpdatedAtMixin, CreatedAtMixin

class FilmQuerySet(QuerySet):
    def with_movie_folders(self, user):
        from films.models import MovieFolder
        return self.annotate(
            in_my_folder=Exists(
                MovieFolder.objects.filter(user=user, film=OuterRef("pk"))
            )
        )

    def watching_movies(self, user):
        if not user.is_authenticated:
            return self
        return self.prefetch_related("folder").filter(folder__user=user)

class FilmManager(models.Manager):
    def get_queryset(self):
        return FilmQuerySet(self.model, using=self._db)

    def with_movie_folders(self, user):
        return self.get_queryset().with_movie_folders(user)

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
    objects = FilmManager()
    review = models.TextField(null=True, blank=True)
    class Meta:
        db_table = "films"

    def __str__(self):
        return self.title




