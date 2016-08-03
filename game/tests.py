import random
import json
from django.test import TestCase
from rest_framework import serializers
from game.serializers import GameSerializer
from game.models import (
    Frame, Game, ScoreException
)

class SerializerTestCase(TestCase):
    def setUp(self):
        self.ser = GameSerializer()

    def test_validate_rolls(self):
        rolls = self.ser.validate_rolls([1, 2, 3, 4])
        self.assertEqual(rolls, [1, 2, 3, 4])
        with self.assertRaises(serializers.ValidationError):
            rolls2 = self.ser.validate_rolls([5,6])

class BaseGameTestCase(TestCase):
    def setUp(self):
        self.new = Game(name="newgame")
        self.new.save()

        self.perfect = Game(name="perfect")
        self.perfect._rolls = ("[10, 10, 10, 10, 10, 10,"
                               " 10, 10, 10, 10, 10, 10]")
        self.perfect.save()

        self.incomplete = Game(name="incomplete")
        self.incomplete._rolls = ("[10, 3, 4, 5, 5, 10, 2, 4, 0, 0]")
        self.incomplete.save()

        self.regular = Game(name="regular")
        self.regular._rolls = ("[5, 4, 6, 4, 10, 2, 3, 1, 4,"
                               " 4, 0, 7, 2, 8, 0, 10, 2, 3]")
        self.regular.save()


class GameTestCase(BaseGameTestCase):
    def test_frames(self):
        self.assertEqual(len(self.perfect.frames), 10)
        self.assertEqual(len(self.incomplete.frames), 7)
        self.assertEqual(len(self.regular.frames), 10)

    def test_score(self):
        self.assertEqual(self.perfect.score, 300)
        self.assertEqual(self.incomplete.score, 66)
        self.assertEqual(self.regular.score, 95)

class GameMutTestCase(BaseGameTestCase):
    def test_add_roll(self):
        self.incomplete.add_roll(6)
        self.assertEqual(self.incomplete.score, 72)
        with self.assertRaises(ScoreException):
            self.perfect.add_roll(5)
            self.complete.add_roll(5)
            self.incomplete.add_roll(7)




class BaseFrameTestCase(TestCase):
    def setUp(self):
        self.strike0 = Frame([10])
        self.strike1 = Frame([10, 10])
        self.strike2 = Frame([10, 10, 10])
        self.strike = Frame([10, 3, 4, 6])
        self.spare = Frame([7, 3, 4, 6])
        self.new = Frame([])
        self.half = Frame([7])
        self.open = Frame([2, 3, 4, 5])
        self.final = Frame([2, 3], final=True)
        self.finaln = Frame([2], final=True)
        self.finalsn = Frame([7, 3, 4], final=True)
        self.finalx = Frame([10], final=True)
        self.finalxn = Frame([10, 4], final=True)
        self.finalxxn = Frame([10, 10, 3], final=True)
        self.finalxnn = Frame([10, 4, 3], final=True)

    def tearDown(self):
        self.strike0 = Frame([10])
        self.strike1 = Frame([10, 10])
        self.strike2 = Frame([10, 10, 10])
        self.strike = Frame([10, 3, 4, 6])
        self.spare = Frame([7, 3, 4, 6])
        self.new = Frame([])
        self.half = Frame([7])
        self.open = Frame([2, 3, 4, 5])
        self.final = Frame([2, 3], final=True)


class FrameTestCase(BaseFrameTestCase):
    def test_frame_init(self):
        self.assertEqual(self.strike.type, Frame.STRIKE)
        self.assertEqual(self.strike.rolls, [10, 3, 4])
        self.assertEqual(self.spare.type, Frame.SPARE)
        self.assertEqual(self.spare.rolls, [7, 3, 4])
        self.assertEqual(self.new.type, Frame.NEW)
        self.assertEqual(self.new.rolls, [])
        self.assertEqual(self.half.type, Frame.HALF)
        self.assertEqual(self.half.rolls, [7])
        self.assertEqual(self.open.type, Frame.OPEN_FRAME)
        self.assertEqual(self.open.rolls, [2, 3])
        self.assertEqual(self.final.type, Frame.FINAL_FRAME)
        self.assertEqual(self.final.rolls, [2, 3])

    def test_frame_scoring(self):
        self.assertEqual(self.strike0.score(), 10)
        self.assertEqual(self.strike1.score(), 20)
        self.assertEqual(self.strike2.score(), 30)
        self.assertEqual(self.strike.score(), 17)
        self.assertEqual(self.spare.score(), 14)
        self.assertEqual(self.new.score(), 0)
        self.assertEqual(self.half.score(), 7)
        self.assertEqual(self.open.score(), 5)
        self.assertEqual(self.final.score(), 5)

    def test_frame_can_add_roll(self):
        self.assertTrue(self.strike0.can_add_roll())
        self.assertTrue(self.strike1.can_add_roll())
        self.assertTrue(self.new.can_add_roll())
        self.assertTrue(self.half.can_add_roll())
        self.assertFalse(self.strike.can_add_roll())
        self.assertFalse(self.strike2.can_add_roll())
        self.assertFalse(self.spare.can_add_roll())
        self.assertFalse(self.open.can_add_roll())
        self.assertFalse(self.final.can_add_roll())
        self.assertTrue(self.finaln.can_add_roll())
        self.assertFalse(self.finalsn.can_add_roll())
        self.assertTrue(self.finalx.can_add_roll())
        self.assertTrue(self.finalxn.can_add_roll())
        self.assertFalse(self.finalxxn.can_add_roll())
        self.assertFalse(self.finalxnn.can_add_roll())

    def test_frame_is_roll_valid(self):
        self.assertTrue(self.new._is_roll_valid(6))
        self.assertTrue(self.new._is_roll_valid(10))
        self.assertFalse(self.new._is_roll_valid(14))
        self.assertFalse(self.new._is_roll_valid(-14))
        self.assertTrue(self.half._is_roll_valid(2))
        self.assertTrue(self.half._is_roll_valid(3))
        self.assertFalse(self.half._is_roll_valid(5))
        self.assertFalse(self.half._is_roll_valid(-5))
        self.assertTrue(self.finaln._is_roll_valid(8))
        self.assertFalse(self.finaln._is_roll_valid(9))
        self.assertTrue(self.finalx._is_roll_valid(10))
        self.assertTrue(self.finalx._is_roll_valid(2))
        self.assertFalse(self.finalx._is_roll_valid(11))
        self.assertTrue(self.finalxn._is_roll_valid(6))
        self.assertFalse(self.finalxn._is_roll_valid(8))


class FrameMutTestCase(BaseFrameTestCase):
    """
    Test case for Frame methods that cause mutations
    """
    def test_frame_add_roll(self):
        self.strike0.add_roll(1)
        self.strike1.add_roll(1)
        self.new.add_roll(1)
        self.half.add_roll(1)

        with self.assertRaises(ScoreException):
            self.strike.add_roll(1)
            self.strike2.add_roll(1)
            self.spare.add_roll(1)
            self.open.add_roll(1)
            self.final.add_roll(1)

        self.assertEqual(self.new.type, Frame.HALF)
        self.assertEqual(self.new.rolls, [1])
        self.assertEqual(self.half.type, Frame.OPEN_FRAME)
        self.assertEqual(self.half.rolls, [7, 1])
        self.assertEqual(self.strike0.type, Frame.STRIKE)
        self.assertEqual(self.strike0.rolls, [10, 1])
        self.assertEqual(self.strike1.type, Frame.STRIKE)
        self.assertEqual(self.strike1.rolls, [10, 10, 1])
