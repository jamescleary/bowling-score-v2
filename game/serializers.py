"""
JSON Serializer
"""

from rest_framework import serializers
from game.models import (Frame, Game)


class GameSerializer(serializers.HyperlinkedModelSerializer):
    """
    Custom serializer for Game models
    """
    frames = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Frame.objects.all())
    class Meta:
        model = Game
        fields = ('id', 'name', 'frames')


class FrameSerializer(serializers.HyperlinkedModelSerializer):
    """Custom serializer for Frame models"""
    rolls = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=10)
    )

    class Meta:
        model = Frame
        fields = ('parent_game', 'frame_type', 'frame_number',
                  'rolls', 'complete')

