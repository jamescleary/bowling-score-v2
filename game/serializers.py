"""
JSON Serializer
"""
from rest_framework import serializers
from game.models import (Frame, Game, ScoreException)


class GameSerializer(serializers.ModelSerializer):
    """
    Custom serializer for Game models
    """
    class Meta:
        model = Game
        fields = ('pk', 'name', 'rolls', 'score')

    rolls = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=10)
    )

    def validate_rolls(self, rolls):
        """Make sure incoming rolls arrays are good"""
        # create a game object which won't be saved to the database
        # so we can check that our rolls list is valid
        test_game = Game(name="test_game", _rolls='[]')
        try:
            for roll in rolls:
                test_game.add_roll(roll)
        except:
            raise serializers.ValidationError("Rolls list was invald")

        return rolls
