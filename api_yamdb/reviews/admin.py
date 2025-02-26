from django.contrib import admin
from django.template.defaultfilters import truncatechars
from .models import Title, Category, Comment, Genre, Review


class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'description')
    search_fields = ('name',)
    list_filter = ('year',)
    empty_value_display = '-пусто-'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')

class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'text',
        'author',
        'title',
        'score',
        'pub_date',
    )

class CommentAdmin(admin.ModelAdmin):

    list_display = (
        'text',
        'author',
        'title',
        'score',
        'pub_date',
    )

admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
