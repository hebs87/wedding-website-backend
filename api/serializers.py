from rest_framework import serializers

from guests.models import Guest, Invitation
from memories.models import Picture


class GuestSerializer(serializers.ModelSerializer):
    """ A serializer for returning guest data """
    class Meta:
        model = Guest
        fields = ('guest_uuid', 'name', 'party_only', 'wedding', 'party')


class InvitationSerializer(serializers.ModelSerializer):
    """ A serializer for returning invitation data, including guests """
    guests = serializers.SerializerMethodField()
    invitation_type = serializers.SerializerMethodField()

    @staticmethod
    def get_invitation_type(obj):
        """ Method to redefine the invitation_type field """
        guests = obj.guests.all()
        return 'party_only' if all(guest.party_only for guest in guests) else 'wedding'

    @staticmethod
    def get_guests(obj):
        """ Method to redefine the guests field """
        return GuestSerializer(obj.guests.all(), many=True).data

    class Meta:
        model = Invitation
        fields = ('invitation_uuid', 'name', 'responded', 'additional_info', 'invitation_type', 'guests')


class PictureSerializer(serializers.ModelSerializer):
    """ A serializer for returning picture data """
    url = serializers.SerializerMethodField()

    @staticmethod
    def get_url(obj):
        """ Method to redefine the url field """
        return obj.file.url

    class Meta:
        model = Picture
        fields = ('picture_uuid', 'url')
