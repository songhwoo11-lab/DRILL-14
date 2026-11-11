import unittest
from unittest.mock import Mock, call, patch

import game_world
import play_mode


class PlayModeFlockTests(unittest.TestCase):
    def tearDown(self):
        play_mode.boy = None
        play_mode.eagles = []

    def test_init_creates_and_registers_ten_eagles(self):
        boy = Mock()
        grass = Mock()
        flock = [Mock() for _ in range(10)]

        with patch("play_mode.get_canvas_width", return_value=1600), patch(
            "play_mode.get_canvas_height", return_value=600
        ), patch("play_mode.create_flock", return_value=flock) as create_flock, patch(
            "play_mode.Boy", return_value=boy
        ), patch("play_mode.Grass", return_value=grass), patch(
            "play_mode.game_world.add_oject"
        ) as add_object:
            play_mode.init()

        create_flock.assert_called_once_with(1600, 600)
        self.assertIs(play_mode.boy, boy)
        self.assertIs(play_mode.eagles, flock)
        self.assertEqual(
            add_object.call_args_list,
            [call(boy), call(grass, 0)] + [call(eagle) for eagle in flock],
        )

    def test_finish_clears_world_and_drops_flock_references(self):
        play_mode.boy = Mock()
        play_mode.eagles = [Mock() for _ in range(10)]

        with patch.object(game_world, "clear") as clear_world:
            play_mode.finish()

        clear_world.assert_called_once_with()
        self.assertIsNone(play_mode.boy)
        self.assertEqual(play_mode.eagles, [])


if __name__ == "__main__":
    unittest.main()
