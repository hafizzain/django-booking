from rest_framework import serializers


class CreatedAtFormat:
    created_at = serializers.DateTimeField(format="%d-%m-%Y")