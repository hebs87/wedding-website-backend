from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Invitation, Guest


# Register your models here.
class GuestInline(admin.TabularInline):
    """ Inline list of guests associated with an invitation """
    model = Guest
    fields = ('name', 'party_only', 'wedding', 'party')
    readonly_fields = ('wedding', 'party')
    extra = 1


class InvitationAdmin(admin.ModelAdmin):
    """ Custom InvitationAdmin model to allow custom invitation create and update functionality """
    list_display = ('name', 'get_code', 'responded', 'additional_info', 'get_copy_code')
    list_filter = ('responded',)
    search_fields = ('name',)
    readonly_fields = ('get_code', 'get_copy_code', 'responded', 'additional_info')
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
                'fields': ('name', 'get_code', 'get_copy_code', 'responded'),
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

    def get_code(self, obj):
        """ Custom field to get the invitation's RSVP code """
        return obj.code if obj.code else 'No code'
    get_code.short_description = 'Invitation Code'
    get_code.allow_tags = True

    @mark_safe
    def get_copy_code(self, obj):
        """ Custom button to copy the invitation's RSVP code to the user's clipboard """
        if obj.code:
            btn_id = 'copy-code'
            btn_styles = 'margin: 0; padding: 0; color: #81d4fa; cursor: pointer;'
            return f'<p id="{btn_id}" data-clipboard-text={obj.code} style="{btn_styles}">Copy code</p>'
        else:
            return 'No code'
    get_copy_code.short_description = 'Copy Code'
    get_copy_code.allow_tags = True


class GuestAttendingStatusListFilter(admin.SimpleListFilter):
    """ Custom list filter to allow filtering guests by attending status """
    title = _('attending status')  # Will render as 'By attending status'
    parameter_name = 'attending_status'  # The url param that will be added when filtering

    def lookups(self, request, model_admin):
        """ Return filter list options """
        return [
            ('wedding', _('Wedding')),
            ('party', _('Party')),
            ('none', _('None')),
            ('pending', _('Pending')),
        ]

    def queryset(self, request, queryset):
        """ Return the queryset filtered by the filter value """
        if self.value() == 'wedding':
            return queryset.filter(wedding=True, invitation__responded=True)
        if self.value() == 'party':
            return queryset.filter(party=True, invitation__responded=True)
        if self.value() == 'none':
            return queryset.filter(wedding=False, party=False, invitation__responded=True)
        if self.value() == 'pending':
            return queryset.filter(invitation__responded=False)

        return queryset


class GuestAdmin(admin.ModelAdmin):
    """ Custom GuestAdmin model to allow viewing guests (read only) """
    list_display = ('name', 'get_party_name', 'party_only', 'wedding', 'party', 'get_attending_status')
    list_filter = ('party_only', GuestAttendingStatusListFilter)
    search_fields = ('name',)
    raw_id_fields = ('invitation',)

    fieldsets = (
        (
            'Invitation Details',  {
                'fields': ('invitation',),
            }
        ),
        (
            'Guest Details',  {
                'fields': ('name',),
            }
        ),
        (
            'RSVP Details',  {
                'fields': ('get_attending_status',),
            }
        ),
    )

    def get_party_name(self, obj):
        """ Custom field to get the invitation's name """
        return obj.invitation.name if obj.invitation.name else ''
    get_party_name.short_description = 'Party Name'
    get_party_name.allow_tags = True

    def get_attending_status(self, obj):
        """ Custom field to get the guest's attending status, based on the invitation's responded status' """
        return obj.attending_status
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
