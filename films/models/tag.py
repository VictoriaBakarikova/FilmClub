from django.db import models
from .mixins import CreatedAtMixin


class Tag(
    CreatedAtMixin,
    models.Model
):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        db_table = "tags"

    def __str__(self):
        return self.name
