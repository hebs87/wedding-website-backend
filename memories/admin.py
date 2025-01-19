from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Picture


# Register your models here.
class PictureAdmin(admin.ModelAdmin):
    """ Custom PictureAdmin model to allow custom picture create and update functionality """
    model = Picture
    list_display = ('get_name', 'get_link', 'get_thumbnail')
    readonly_fields = ('get_link', 'get_thumbnail',)


    def get_name(self, obj):
        """ Custom field to get the picture's name """
        return obj.file.name.split('/')[-1]
    get_name.short_description = 'Name'
    get_name.allow_tags = True


    @mark_safe
    def get_link(self, obj):
        """ Custom field to get the picture's URL - allow clicking it to open it in a new tab """
        if obj.file:
            return f'<a href="{obj.file.url}" target="blank"/>{obj.file.name}</a>'
        else:
            return 'No link'
    get_link.short_description = 'Link'
    get_link.allow_tags = True


    @mark_safe
    def get_thumbnail(self, obj):
        """ Custom field to get the picture's thumbnail """
        if obj.file:
            return f'<img src="{obj.file.url}"  height="100px"/>'
        else:
            return 'No image'
    get_thumbnail.short_description = 'Thumbnail'
    get_thumbnail.allow_tags = True


# Register models
admin.site.register(Picture, PictureAdmin)
