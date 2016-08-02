import json
import itertools
from django.db import models


class ScoreException(Exception):
    pass


class GameManager(models.Manager):
    def new_game(self, name):
        game = Game(name=name)
        game.save()

        for i in range(0, 10):
            frame = Frame(
                parent_game=game,
                frame_type=Frame.NEW,
                frame_number=i,
                rolls_json='[]'
            )
            if i == 9:
                frame.frame_type=Frame.FINAL_FRAME
            frame.save()
        return game


class Game(models.Model):
    name = models.CharField(max_length=100, unique=True)
    objects = GameManager()

    def score(self):
        frames = self.frames.all()
        scores = []
        for frame in frames:
            score = frame.score(*frames.filter(
                frame_number__in=(
                    frame.frame_number + 1, frame.frame_number + 2
                )
            ))
            scores.append(score)
        return sum(scores)


class FrameManager(models.Manager):
    def create(self, *args, **kwargs):
        kwargs['rolls_json'] = json.dumps(kwargs.get('rolls', '[]'))
        return super(FrameManager, self).create(*args, **kwargs)


class Frame(models.Model):
    NEW = "N"
    HALF = "H"
    OPEN_FRAME = "OF"
    SPARE = "SP"
    STRIKE = "ST"
    FINAL_FRAME = "FF"
    FRAME_CHOICES = (
        (NEW, 'New'),
        (HALF, 'Half'),
        (OPEN_FRAME, 'Open Frame'),
        (SPARE, 'Spare'),
        (STRIKE, 'Strike'),
        (FINAL_FRAME, 'Final Frame'),
    )

    parent_game = models.ForeignKey('Game', related_name='frames')
    frame_type = models.CharField(choices=FRAME_CHOICES, max_length=2,
                                  default=NEW)
    frame_number = models.IntegerField(default=0)
    rolls_json = models.TextField(default='[]')
    complete = models.BooleanField(default=False)

    def is_final_frame(self):
        return self.frame_number == 9

    def add_roll(self, roll):
        """
        Add a roll to the list of rolls already on

        Raises a ScoreExcpetion when adding a roll to the frame is not allowed
        """
        rolls = self.get_rolls()
        if self.frame_type in (Frame.STRIKE, Frame.SPARE, Frame.OPEN_FRAME) or self.complete:
            raise ScoreException("Can't add more rolls to that frame")

        elif rolls == []:
            if roll == 10:
                self.frame_type = Frame.STRIKE
                self.set_rolls([10])
                self.complete = True
            else:
                self.frame_type = Frame.HALF
                self.set_rolls([roll])
                self.complete = False

        elif len(rolls) == 1 and not self.frame_type == Frame.FINAL_FRAME:
            sanity = roll + sum(rolls)
            if sanity > 10 or sanity < 0:
                raise ScoreException("new roll is an invalid value")

            if sanity == 10:
                self.frame_type = Frame.SPARE
            else:
                self.frame_type = Frame.OPEN_FRAME
            rolls.append(roll)
            self.set_rolls(rolls)
            self.complete = True

        elif self.frame_type == Frame.FINAL_FRAME:
            # if there are two rolls in the frame, and they don't consist
            # of a first roll strike, or a spare, raise an exception.
            # also if there are already three rolls raise an exception.
            if ((len(rolls) == 2 and
                 not ((sum(rolls[:2]) == 10) or
                  (rolls[0] == 10))) or
                len(rolls) >=3
            ):
                raise ScoreException("Can't add more rolls to that frame")
            else:
                rolls.append(roll)
                self.set_rolls(rolls)

        else:
            raise ScoreException("Can't add more rolls to that frame")

    def set_rolls(self, rolls):
        self.rolls_json = json.dumps(rolls)

    def get_rolls(self):
        return json.loads(self.rolls_json)

    def score(self, *nxt):
        """
        Calculate the total score of the frame

        gets passed the next two frames so that strikes and spares can
        calculate their score based on the rolls in those frames
        """
        rolls = self.get_rolls() + [
            roll for f in nxt for roll in f.get_rolls()
        ]
        if self.frame_type in (Frame.STRIKE, Frame.SPARE):
            # since we're including the self.rolls, both spares and strikes
            # will take the first three rolls (strikes go [10, x, y] and spares go
            # [6, 4, x])
            return sum(rolls[:3])
        else:
            return sum(self.get_rolls())
