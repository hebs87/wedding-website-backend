from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import WeddingWebsiteBaseUser


# Register your models here.
class WeddingWebsiteBaseUserAdmin(UserAdmin):
    """ Custom WeddingWebsiteBaseUserAdmin model to allow custom user create and update functionality """
    model = WeddingWebsiteBaseUser

    search_fields = ('first_name', 'last_name', 'email', 'username')
    list_filter = ('is_active', 'role')
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')

    add_fieldsets = (
        (
            'User Details', {
                'fields': ('first_name', 'last_name', 'username', 'email', 'role', 'password1', 'password2'),
            }
        ),
    )
    fieldsets = (
        (
            'Personal info',  {
                'fields': ('first_name', 'last_name', 'username', 'email', 'role', 'password'),
            }
        ),
        (
            'Status',  {
                'fields': ('is_active',),
            }
        ),
        (
            'Important Dates', {
                'fields': ('last_login', 'date_joined')
            }
        )
    )
    readonly_fields = ('date_joined', 'last_login')


# Register models
admin.site.register(WeddingWebsiteBaseUser, WeddingWebsiteBaseUserAdmin)
