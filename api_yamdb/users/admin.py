from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

UserAdmin.fieldsets += (
    (
        'Extra Fields',
        {
            'fields':
            ('bio', 'role',)
        }
    ),
)

admin.site.register(User, UserAdmin)
