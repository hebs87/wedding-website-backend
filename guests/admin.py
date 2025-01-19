from django.contrib import admin
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Invitation, Guest


# Register your models here.
class GuestInline(admin.TabularInline):
    """ Inline list of guests associated with an invitation """
    model = Guest
    fields = ('name', 'meal', 'attending')
    readonly_fields = ('attending',)
    extra = 1


class InvitationAdmin(admin.ModelAdmin):
    """ Custom InvitationAdmin model to allow custom invitation create and update functionality """
    list_display = ('name', 'get_link', 'responded', 'additional_info', 'get_copy_link')
    list_filter = ('responded',)
    readonly_fields = ('get_link', 'get_copy_link', 'responded', 'additional_info')
    inlines = (GuestInline,)

    add_fieldsets = (
        (
            'Invitation Details', {
                'fields': ('name',),
            }
        ),
    )
    fieldsets = (
        (
            'Invitation Details',  {
                'fields': ('name', 'get_link', 'get_copy_link', 'responded'),
            }
        ),
        (
            'Additional',  {
                'fields': ('additional_info',),
            }
        ),
    )


    class Media:
        js = (
            'js/admin-copy-link.js',
        )


    def get_link(self, obj):
        """ Custom field to get the invitation's RSVP link in the FE site """
        if obj.code:
            return f'{settings.FRONTEND_DASHBOARD}rsvp?code={obj.code}'
        else:
            return 'No link'
    get_link.short_description = 'Invitation Link'
    get_link.allow_tags = True


    @mark_safe
    def get_copy_link(self, obj):
        """ Custom button to copy the invitation's RSVP link in the FE site to the user's clipboard """
        if obj.code:
            url = f'{settings.FRONTEND_DASHBOARD}rsvp?code={obj.code}'
            btn_id = 'copy-link'
            btn_styles = 'margin: 0; padding: 0; color: #81d4fa; cursor: pointer;'
            return f'<p id="{btn_id}" data-clipboard-text={url} style="{btn_styles}">Copy link</p>'
        else:
            return 'No link'
    get_copy_link.short_description = 'Copy Link'
    get_copy_link.allow_tags = True


class GuestAttendingStatusListFilter(admin.SimpleListFilter):
    """ Custom list filter to allow filtering guests by attending status """
    title = _('attending status')  # Will render as 'By attending status'
    parameter_name = 'attending_status'  # The url param that will be added when filtering

    def lookups(self, request, model_admin):
        """ Return filter list options """
        return [
            ('yes', _('Yes')),
            ('no', _('No')),
            ('pending', _('Pending')),
        ]

    def queryset(self, request, queryset):
        """ Return the queryset filtered by the filter value """
        if self.value() == "yes":
            return queryset.filter(attending=True)
        if self.value() == "no":
            return queryset.filter(attending=False, invitation__responded=True)
        if self.value() == "pending":
            return queryset.filter(attending=False, invitation__responded=False)


class GuestAdmin(admin.ModelAdmin):
    """ Custom GuestAdmin model to allow viewing guests (read only) """
    list_display = ('name', 'meal', 'get_attending_status')
    list_filter = ('meal', GuestAttendingStatusListFilter)
    raw_id_fields = ('invitation',)

    fieldsets = (
        (
            'Invitation Details',  {
                'fields': ('invitation',),
            }
        ),
        (
            'Guest Details',  {
                'fields': ('name', 'meal'),
            }
        ),
        (
            'RSVP Details',  {
                'fields': ('get_attending_status',),
            }
        ),
    )


    def get_attending_status(self, obj):
        """ Custom field to get the guest's attending status, based on the invitation's responded status' """
        if obj.attending:
            return 'Yes'
        else:
            if obj.invitation.responded:
                return 'No'
            else:
                return 'Pending'
    get_attending_status.short_description = 'Attending Status'
    get_attending_status.allow_tags = True

    def has_add_permission(self, request, obj=None):
        """ Override to disallow adding guests """
        return False

    def has_delete_permission(self, request, obj=None):
        """ Override to disallow deleting guests """
        return False

    def has_change_permission(self, request, obj=None):
        """ Override to disallow changing guests """
        return False


# Register models
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Guest, GuestAdmin)
