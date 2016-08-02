from rest_framework import (
    mixins,
    generics,
    permissions
)

from game.models import (Game, Frame)
from game.serializers import (GameSerializer, FrameSerializer)


# Create your views here.
class GameList(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               generics.GenericAPIView):
    """
    List all games or create a new one
    """
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class GameFrames(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 generics.GenericAPIView):
    serializer_class = FrameSerializer

    def get_queryset(self, *args, **kwargs):
        return Game.objects.get(name=self.game_name).frames.all()

    def get(self, request, *args, **kwargs):
        self.game_name = kwargs['name']
        return self.list(request, *args, **kwargs)
