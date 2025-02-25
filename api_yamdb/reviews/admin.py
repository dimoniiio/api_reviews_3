from django.contrib import admin
from django.template.defaultfilters import truncatechars

from .models import Review


class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'text',
        'author',
        'title',
        'score',
        'pub_date',
    )


admin.site.register(Review, ReviewAdmin)
