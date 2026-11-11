import unittest
from unittest.mock import Mock, patch

import game_framework
from eagle import (
    ANIMATION_CYCLE_DISTANCE_M,
    ANIMATION_CYCLE_DISTANCE_PX,
    ANIMATION_CYCLE_SECONDS,
    EAGLE_FRAME_BOUNDS,
    EAGLE_FRAME_COUNT,
    Eagle,
    FLIGHT_SPEED_KMPH,
    FLIGHT_SPEED_MPS,
    FLIGHT_SPEED_PPS,
    FRAME_INTERVAL_SECONDS,
    METERS_PER_PIXEL,
    SPRITE_SHEET_HEIGHT,
    SPRITE_SHEET_WIDTH,
    frame_source_rect,
)


class EagleMotionTests(unittest.TestCase):
    def test_fixed_flight_speed_is_converted_to_pixels_per_second(self):
        self.assertEqual(FLIGHT_SPEED_KMPH, 60.0)
        self.assertAlmostEqual(FLIGHT_SPEED_MPS, 16.6666667, places=6)
        self.assertAlmostEqual(FLIGHT_SPEED_PPS, 555.5555556, places=6)

    def test_fixed_cycle_distance_and_frame_timing(self):
        self.assertEqual(METERS_PER_PIXEL, 0.03)
        self.assertEqual(ANIMATION_CYCLE_DISTANCE_M, 7.0)
        self.assertAlmostEqual(ANIMATION_CYCLE_DISTANCE_PX, 233.3333333, places=6)
        self.assertAlmostEqual(ANIMATION_CYCLE_SECONDS, 0.42, places=8)
        self.assertAlmostEqual(FRAME_INTERVAL_SECONDS, 0.03, places=8)

    def test_all_fourteen_frame_rectangles_fit_the_sprite_sheet(self):
        self.assertEqual(EAGLE_FRAME_COUNT, 14)

        for frame_index, (left, top, right, bottom) in enumerate(EAGLE_FRAME_BOUNDS):
            self.assertGreaterEqual(left, 0)
            self.assertGreaterEqual(top, 0)
            self.assertLess(right, SPRITE_SHEET_WIDTH + 1)
            self.assertLess(bottom, SPRITE_SHEET_HEIGHT + 1)
            self.assertGreater(right, left)
            self.assertGreater(bottom, top)

            source_x, source_y, width, height = frame_source_rect(frame_index)
            self.assertEqual(source_x, left)
            self.assertEqual(source_y, SPRITE_SHEET_HEIGHT - bottom)
            self.assertEqual(width, right - left)
            self.assertEqual(height, bottom - top)
            self.assertLessEqual(source_x + width, SPRITE_SHEET_WIDTH)
            self.assertLessEqual(source_y + height, SPRITE_SHEET_HEIGHT)


class EagleAnimationTests(unittest.TestCase):
    def setUp(self):
        self.image = Mock()
        Eagle._sprite_sheet = self.image
        self.eagle = Eagle(120, 240)

    def tearDown(self):
        Eagle._sprite_sheet = None

    def test_animation_advances_through_all_frames_and_loops(self):
        self.eagle.advance_animation(FRAME_INTERVAL_SECONDS * 13)
        self.assertEqual(self.eagle.frame_index, 13)

        self.eagle.advance_animation(FRAME_INTERVAL_SECONDS)
        self.assertEqual(self.eagle.frame_index, 0)

    def test_motion_uses_elapsed_seconds_and_facing_direction(self):
        self.eagle.advance(1.0)
        self.assertAlmostEqual(self.eagle.x, 120 + 555.5555556, places=6)

        self.eagle.direction = -1
        self.eagle.advance(0.5)
        self.assertAlmostEqual(self.eagle.x, 120 + 555.5555556 - 277.7777778, places=6)

    def test_zero_time_does_not_advance_and_negative_time_is_rejected(self):
        self.eagle.advance_animation(0)
        self.assertEqual(self.eagle.frame_index, 0)

        with self.assertRaises(ValueError):
            self.eagle.advance_animation(-0.01)

    def test_draw_uses_frame_rectangle_and_direction_flip(self):
        eagle = Eagle(120, 240, direction=-1)
        eagle.draw()

        args = self.image.clip_composite_draw.call_args.args
        self.assertEqual(args[:4], frame_source_rect(0))
        self.assertEqual(args[5], "h")
        self.assertEqual(args[6:8], (120, 240))


class FrameTimeTests(unittest.TestCase):
    def test_game_loop_sets_delta_time_before_updating_mode(self):
        observed_frame_times = []

        class Mode:
            event_count = 0

            def init(self):
                pass

            def handle_events(self):
                self.event_count += 1
                if self.event_count == 2:
                    game_framework.quit()

            def update(self):
                observed_frame_times.append(game_framework.frame_time)

            def render(self):
                pass

            def finish(self):
                pass

        mode = Mode()
        with patch(
            "game_framework.time.perf_counter",
            side_effect=(1.0, 1.02, 1.05),
        ):
            game_framework.run(mode)

        self.assertEqual(len(observed_frame_times), 2)
        self.assertAlmostEqual(observed_frame_times[0], 0.02)
        self.assertAlmostEqual(observed_frame_times[1], 0.03)


if __name__ == "__main__":
    unittest.main()
