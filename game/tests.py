import random
import json
from django.test import TestCase
from game.models import (
    Frame, Game, ScoreException
)

# Create your tests here.
class GameTestCase(TestCase):
    def setUp(self):
        self.perfect_game = Game.objects.new_game("perfect")
        for frame in self.perfect_game.frames.all():
            if frame.is_final_frame():
                frame.frame_type = Frame.FINAL_FRAME
                frame.rolls_json = '[10, 10, 10]'
            else:
                frame.frame_type = Frame.STRIKE
                frame.rolls_json = '[10]'
            frame.complete = True
            frame.save()

        self.incomplete_game = Game.objects.new_game(name="incomplete")
        (first, second, third,
         fourth, fifth) = self.incomplete_game.frames.filter(
            frame_number__lt=5)
        first.frame_type = Frame.OPEN_FRAME
        first.rolls_json = '[6, 3]'
        first.complete = True
        first.save()

        second.frame_type = Frame.SPARE
        second.rolls_json = '[6, 4]'
        second.complete = True
        second.save()

        third.frame_type = Frame.STRIKE
        third.rolls_json = '[10]'
        third.complete = True
        third.save()

        fourth.frame_type = Frame.OPEN_FRAME
        fourth.rolls_json = '[0, 3]'
        fourth.complete = True
        fourth.save()
        fifth.frame_type = Frame.HALF
        fifth.rolls_json = '[6]'
        fifth.complete = False
        fifth.save()

    def test_score(self):
        self.assertEqual(self.perfect_game.score(), 300)
        self.assertEqual(self.incomplete_game.score(), 51)


class FrameTestCase(TestCase):
    def setUp(self):
        self.game = Game(name="test_game2")
        self.game.save()

        self.strike = Frame(
            parent_game=self.game,
            frame_type=Frame.STRIKE,
            frame_number=0,
            rolls_json='[10]'
        )
        self.strike.save()

        self.spare = Frame(
            parent_game=self.game,
            frame_type=Frame.SPARE,
            frame_number=0,
            rolls_json='[6,4]'
        )
        self.spare.save()

        self.final_frame1 = Frame(
            parent_game=self.game,
            frame_type=Frame.FINAL_FRAME,
            frame_number=9,
            rolls_json='[6,4]'
        )
        self.final_frame1.save()

        self.final_frame2 = Frame(
            parent_game=self.game,
            frame_type=Frame.FINAL_FRAME,
            frame_number=9,
            rolls_json='[4,3]'
        )
        self.final_frame2.save()

        self.final_frame3 = Frame(
            parent_game=self.game,
            frame_type=Frame.FINAL_FRAME,
            frame_number=9,
            rolls_json='[10, 3, 7]'
        )
        self.final_frame3.save()

        self.final_frame4 = Frame(
            parent_game=self.game,
            frame_type=Frame.FINAL_FRAME,
            frame_number=9,
            rolls_json='[10]'
        )
        self.final_frame4.save()

        self.new = Frame(
            parent_game=self.game,
            frame_type=Frame.NEW,
            frame_number=0,
            rolls_json='[]'
        )
        self.new.save()

        self.half = Frame(
            parent_game=self.game,
            frame_type=Frame.HALF,
            frame_number=0,
            rolls_json='[6]'
        )
        self.new.save()

    def test_strike_scoring(self):
        self.assertEqual(self.strike.score(), 10)
        self.assertEqual(
            self.strike.score(
                Frame(parent_game=self.game, frame_type=Frame.OPEN_FRAME,
                      frame_number=1, rolls_json='[3,4]')
            ), 17)
        self.assertEqual(
            self.strike.score(
                Frame(parent_game=self.game, frame_type=Frame.STRIKE,
                      frame_number=1, rolls_json='[10]'),
                Frame(parent_game=self.game, frame_type=Frame.STRIKE,
                      frame_number=2, rolls_json='[10]')
            ), 30)

        self.assertEqual(
            self.strike.score(Frame(parent_game=self.game,
                                    frame_type=Frame.FINAL_FRAME,
                                    frame_number=1, rolls_json='[10,2,3]'
            )), 22)

        self.assertEqual(
            self.strike.score(
                Frame(parent_game=self.game, frame_type=Frame.STRIKE,
                      frame_number=1, rolls_json='[10]'),
                Frame(parent_game=self.game,
                      frame_type=Frame.FINAL_FRAME,
                      frame_number=1, rolls_json='[10,2,3]')
            ), 30)

    def test_spare_scoring(self):
        self.assertEqual(self.spare.score(), 10)
        self.assertEqual(
            self.spare.score(
                Frame(parent_game=self.game, frame_type=Frame.OPEN_FRAME,
                      frame_number=1, rolls_json='[3,4]')
            ), 13)
        self.assertEqual(
            self.spare.score(
                Frame(parent_game=self.game, frame_type=Frame.STRIKE,
                      frame_number=1, rolls_json='[10]'),
                Frame(parent_game=self.game, frame_type=Frame.STRIKE,
                      frame_number=2, rolls_json='[10]')
            ), 20)

        self.assertEqual(
            self.spare.score(Frame(parent_game=self.game,
                                    frame_type=Frame.FINAL_FRAME,
                                    frame_number=1, rolls_json='[10,2,3]'
            )), 20)

        self.assertEqual(
            self.spare.score(
                Frame(parent_game=self.game,
                      frame_type=Frame.FINAL_FRAME,
                      frame_number=1, rolls_json='[2,8,10]')
            ), 12)

    def test_final_frame_scoring(self):
        self.assertEqual(self.final_frame1.score(), 10)
        self.assertEqual(self.final_frame2.score(), 7)
        self.assertEqual(self.final_frame3.score(), 20)

    def test_strike_add_roll(self):
        with self.assertRaises(ScoreException):
            self.strike.add_roll(3)

    def test_spare_add_roll(self):
        with self.assertRaises(ScoreException):
            self.spare.add_roll(3)

    def test_new_add_roll(self):
        self.new.add_roll(3)
        self.assertEqual([3], self.new.get_rolls())
        self.assertEqual(Frame.HALF, self.new.frame_type)
        self.assertFalse(self.new.complete)

    def test_half_add_roll(self):
        self.half.add_roll(3)
        self.assertEqual([6, 3], self.half.get_rolls())

    def test_open_frame_add_roll(self):
        with self.assertRaises(ScoreException):
            self.spare.add_roll(3)

    def test_final_frame_add_roll(self):
        self.final_frame1.add_roll(3)
        self.assertEqual([6,4,3], self.final_frame1.get_rolls())

        with self.assertRaises(ScoreException):
            self.final_frame2.add_roll(3)
            self.final_frame3.add_roll(3)

        self.final_frame4.add_roll(3)
        self.assertEqual([10,3], self.final_frame4.get_rolls())
        self.final_frame4.add_roll(7)
        self.assertEqual([10,3,7], self.final_frame4.get_rolls())

        with self.assertRaises(ScoreException):
            self.final_frame4.add_roll(3)
