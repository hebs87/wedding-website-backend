from rest_framework import serializers

from guests.models import Guest, Invitation


class GuestSerializer(serializers.ModelSerializer):
    """ A serializer for returning guest data """
    class Meta:
        model = Guest
        fields = ('guest_uuid', 'name', 'attending', 'song')


class InvitationSerializer(serializers.ModelSerializer):
    """ A serializer for returning invitation data, including guests """
    guests = serializers.SerializerMethodField()

    @staticmethod
    def get_guests(obj):
        """ Method to redefine the guests field """
        return GuestSerializer(obj.guests.all(), many=True).data

    class Meta:
        model = Invitation
        fields = ('invitation_uuid', 'name', 'responded', 'additional_info', 'guests')
