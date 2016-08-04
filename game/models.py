import json
import itertools
from django.db import models


class ScoreException(Exception):
    pass


class GameManager(models.Manager):
    """Custom manager for the Game model"""
    def new_game(self, name):
        """shortcut for creating a new game"""
        game = Game(name=name)
        game.save()
        return game


class Game(models.Model):
    """
    Django model for storing game data

    only stores a list of rolls and a  name. All other stuff is calculated
    based on that list because storing rolls on a Frame database model got
    needlessly complicated.
    """
    objects = GameManager()
    name = models.CharField(max_length=100)
    _rolls = models.TextField(default='[]')

    @property
    def rolls(self):
        """Load rolls text field int a usable list of integers"""
        rolls = json.loads(self._rolls)
        if rolls:
            return rolls
        return []

    @rolls.setter
    def rolls(self, rolls):
        """converts the given list of integers to the text _rolls attribute"""
        self._rolls = json.dumps(rolls)

    @property
    def score(self):
        """Calculate the game's score"""
        return sum([frame.score() for frame in self.frames])

    @property
    def frames(self):
        """
        Separate the rolls list into its correct frames

        Since there are different rules for Strikes, Spares, and the Final Frame
        of the game, we'll have to validate for those
        """
        rolls = self.rolls
        frames = [Frame([])]
        for (i, roll) in enumerate(rolls):
            if len(frames) == 10:
                frames[-1].type = Frame.FINAL_FRAME

            if frames[-1].can_add_roll():
                frames[-1] = Game._update_frame(frames[-1], rolls[i:])

            if frames[-1].type not in (
                    Frame.FINAL_FRAME, Frame.NEW,
                    Frame.HALF, Frame.INVALID
            ):
                frames.append(Frame([]))
        return frames

    def add_roll(self, roll):
        """Validate the given roll and push it onto the rolls list"""
        frames = self.frames
        rolls = self.rolls
        if len(frames) == 10 and not frames[-1].can_add_roll():
            raise ScoreException("Can't add roll")
        frames[-1].add_roll(roll)
        rolls.append(roll)
        self.rolls = rolls

    @staticmethod
    def _update_frame(frame, rolls):
        """
        Decipher what to do with the current frame based on slice
        of the rolls.
        """
        # make sure we don't get any index errors in the rest of
        # this function
        if rolls == []:
            return frame
        if frame.type == Frame.NEW:
            # the first roll makes the current frame a strike, add that
            # roll and the next two to the rolls list
            if rolls[0] == 10:
                frame.add_rolls(rolls[:3])
            # otherwise it makes it a half frame, thus we'll only add
            # the first roll
            else:
                frame.add_roll(rolls[0])
        elif frame.type == Frame.HALF:
            # if the first frame will make the half frame a spare,
            # add the next two rolls to it
            if frame.rolls[0] + rolls[0] == 10:
                frame.add_rolls(rolls[:2])
            # otherwise it just makes it an open frame
            else:
                frame.add_roll(rolls[0])
        elif frame.type == Frame.FINAL_FRAME:
            frame.add_rolls(rolls)

        return frame


class Frame(object):
    """An object which stores a frame's information"""
    NEW = "N"
    HALF = "H"
    OPEN_FRAME = "OF"
    SPARE = "SP"
    STRIKE = "ST"
    FINAL_FRAME = "FF"
    INVALID = "XX"

    def __init__(self, rolls=[], final=False):
        """Decide the type and rolls which the model will use in other methods"""
        if final:
            self.type = Frame.FINAL_FRAME
            self.rolls = rolls

        else:
            self.type = Frame.NEW
            self.rolls = []
            try:
                for roll in rolls:
                    if self.can_add_roll():
                        self.add_roll(roll)
                        continue
                    break
            except ScoreException as e:
                print(rolls)
                raise e

        if self.type in (Frame.STRIKE, Frame.SPARE):
            self.rolls = rolls[:3]
        elif self.type == Frame.OPEN_FRAME:
            self.rolls = rolls[:2]
        else:
            self.rolls = rolls


    def add_rolls(self, rolls):
        """Wrapper for adding multiple rolls to a frame"""
        for roll in rolls:
            self.add_roll(roll)

    def add_roll(self, roll):
        """Validate the given roll and add it to the rolls list"""
        if self.can_add_roll():
            if not self._is_roll_valid(roll):
                raise ScoreException(
                    "That's not a valid roll value: {} {}".format(
                        json.dumps(self.rolls), roll))
            rolls = self.rolls
            rolls.append(roll)
            self.rolls = rolls
            self._determine_type()
        else:
            raise ScoreException("Can't add roll to that frame")

    def _is_roll_valid(self, roll):
        """Check that an incoming roll can be added to this frame"""
        return not ((roll > 10 or roll < 0) or
                    (self.type == Frame.HALF and
                     roll > (10 - self.rolls[0])) or
                    (self.type == Frame.FINAL_FRAME and
                     self._ff_is_roll_invalid(roll)))

    def _ff_is_roll_invalid(self, roll):
        """Since final frames' logic is a bit complicated, break it out into
            its own function"""
        r = self.rolls
        # first roll strike
        if ((r == [10]) or
            # first two strikes
            (r == [10, 10]) or
            # first two rolls equal a spare
            (len(r) == 2 and sum(r) == 10)
        ):
            return roll < 0 or roll > 10
        # first roll non-strike
        elif len(r) == 1 and r[0] < 10:
            return 10 - r[0] < roll
        # first roll strike, second roll non-strike
        elif len(r) == 2 and r[0] == 10:
            return 10 - r[1] < roll
        return False

    def _determine_type(self):
        """Determine the type of a frame based on its rolls attribute"""
        if self.type == Frame.FINAL_FRAME:
            self.type = Frame.FINAL_FRAME
        elif self.rolls == []:
            self.type = Frame.NEW
        elif self.rolls[0] == 10:
            self.type = Frame.STRIKE
        elif len(self.rolls) == 1:
            self.type = Frame.HALF
        elif sum(self.rolls[:2]) == 10:
            self.type = Frame.SPARE
        else:
            self.type = Frame.OPEN_FRAME

    def can_add_roll(self):
        """Check whether a frame can add a roll"""
        if self.type == Frame.OPEN_FRAME:
            return False
        if self.type in (Frame.STRIKE, Frame.SPARE):
            return len(self.rolls) < 3
        elif self.type == Frame.FINAL_FRAME:
            return self._ff_can_add_roll()
        return True

    def _ff_can_add_roll(self):
        """ since the logic for last frames is a bit complicated,
        I'm breaking this out into its own method"""
        return ((len(self.rolls) < 2) or
                (len(self.rolls) == 2 and
                    (self.rolls[0] == 10 or
                        sum(self.rolls) == 10)))

    def score(self):
        """Calculate the frame's score"""
        if self.rolls == []:
            return 0
        return sum(self.rolls)
