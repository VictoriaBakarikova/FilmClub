from django.contrib import admin
from django.utils.html import format_html
from .models import Film, Tag, UserProfile, MovieFolder


# Register your models here.
@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("title", "director", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("title",)
    ordering = ("title",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "director",
                    "tags",
                    "description",
                    "cover_url",
                    "genres",
                    "rating",
                    "release",
                    "views",
                )
            }

        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",)
            }
        )
    )

    @admin.display(empty_value="-")
    def cover(self, film):
        if not film.cover_url:
            return None
        return format_html(
            f"<img src='{film.cover_url}' alt='cover' width='100px' height='100px'/>",
        )

@admin.register(MovieFolder)
class MovieFolderAdmin(admin.ModelAdmin):
    list_display = ("film_title", "created_at", "updated_at")
    ordering = ("film__title",)

    @admin.display(description="Film title")
    def film_title(self, obj):
        return obj.film.title

    @admin.display(empty_value="-")
    def cover(self, folder):
        if not folder.cover_url:
            return None
        return format_html(
            f"<img src='{folder.cover_url}' alt='cover' width='100px' height='100px'/>",
        )

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
    )
    list_filter = ("name",)
    ordering = ("name",)
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("name",)}),
        (
            "Metadata",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            }
        )
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("avatar", "user_username")
    @admin.display(description="Username")
    def user_username(self, obj):
        return obj.user.username

    @admin.display(empty_value="-")
    def avatar(self, user_profile):
        if not user_profile.avatar:
            return None
        return format_html(
            f"<img src='{user_profile.avatar}' alt='cover' width='100px' height='100px'/>",
        )
