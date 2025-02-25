from django.contrib import admin

from .models import Title, Review, Comment, Category, Genre


class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'description')
    search_fields = ('name',)
    list_filter = ('year',)
    empty_value_display = '-пусто-'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')


admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment)
admin.site.register(Review)
admin.site.register(Genre)
