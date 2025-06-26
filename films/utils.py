import re


MENTION_PATTERN = re.compile(r"@(\w+)")

from .models import Film

def get_filtered_and_sorted_films(request):
    sort = request.GET.get("sort")
    tags_selected = request.GET.getlist("tags[]")

    films = Film.objects.all()

    if tags_selected:
        films = films.filter(tags__id__in=tags_selected).distinct()

    if sort == "title_asc":
        films = films.order_by("title")
    elif sort == "year_asc":
        films = films.order_by("release")
    elif sort == "year_desc":
        films = films.order_by("-release")

    return films, sort, list(map(int, tags_selected))
