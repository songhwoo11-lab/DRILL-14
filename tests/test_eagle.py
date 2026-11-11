import unittest
from unittest.mock import Mock, patch

import game_framework
from eagle import (
    ANIMATION_CYCLE_DISTANCE_M,
    ANIMATION_CYCLE_DISTANCE_PX,
    ANIMATION_CYCLE_SECONDS,
    EAGLE_FRAME_BOUNDS,
    EAGLE_FRAME_COUNT,
    EAGLE_COUNT,
    EAGLE_MAX_HEIGHT,
    EAGLE_MAX_WIDTH,
    Eagle,
    FLIGHT_SPEED_KMPH,
    FLIGHT_SPEED_MPS,
    FLIGHT_SPEED_PPS,
    FRAME_INTERVAL_SECONDS,
    METERS_PER_PIXEL,
    SPRITE_SHEET_HEIGHT,
    SPRITE_SHEET_WIDTH,
    create_flock,
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
        with patch("eagle.get_canvas_width", return_value=1600), patch(
            "eagle.get_canvas_height", return_value=600
        ):
            self.eagle.advance(1.0)
        self.assertAlmostEqual(self.eagle.x, 120 + 555.5555556, places=6)

        self.eagle.direction = -1
        with patch("eagle.get_canvas_width", return_value=1600), patch(
            "eagle.get_canvas_height", return_value=600
        ):
            self.eagle.advance(0.5)
        self.assertAlmostEqual(self.eagle.x, 120 + 555.5555556 - 277.7777778, places=6)

    def test_horizontal_motion_reflects_at_edges_and_stays_visible(self):
        self.eagle.x = 100
        with patch("eagle.get_canvas_width", return_value=200), patch(
            "eagle.get_canvas_height", return_value=200
        ):
            self.eagle.advance(0.2)

        self.assertEqual(self.eagle.direction, -1)
        self.assertGreaterEqual(self.eagle.x, EAGLE_MAX_WIDTH / 2)
        self.assertLessEqual(self.eagle.x, 200 - EAGLE_MAX_WIDTH / 2)

    def test_large_delta_time_handles_multiple_edge_reflections(self):
        self.eagle.x = 100
        with patch("eagle.get_canvas_width", return_value=200), patch(
            "eagle.get_canvas_height", return_value=200
        ):
            self.eagle.advance(2.0)

        self.assertGreaterEqual(self.eagle.x, EAGLE_MAX_WIDTH / 2)
        self.assertLessEqual(self.eagle.x, 200 - EAGLE_MAX_WIDTH / 2)
        self.assertIn(self.eagle.direction, (-1, 1))

    def test_vertical_position_is_clamped_to_canvas(self):
        self.eagle.y = -10
        with patch("eagle.get_canvas_width", return_value=1600), patch(
            "eagle.get_canvas_height", return_value=100
        ):
            self.eagle.advance(0)

        self.assertEqual(self.eagle.y, EAGLE_MAX_HEIGHT / 2)

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


class EagleFlockTests(unittest.TestCase):
    def setUp(self):
        Eagle._sprite_sheet = Mock()

    def tearDown(self):
        Eagle._sprite_sheet = None

    def test_flock_has_ten_independent_non_overlapping_eagles(self):
        flock = create_flock(1600, 600)

        self.assertEqual(len(flock), EAGLE_COUNT)
        self.assertEqual(len({eagle.x for eagle in flock[:5]}), 5)
        self.assertEqual(len({eagle.y for eagle in flock}), 2)
        self.assertGreaterEqual(
            min(eagle.x for eagle in flock), EAGLE_MAX_WIDTH / 2
        )
        self.assertLessEqual(
            max(eagle.x for eagle in flock),
            1600 - EAGLE_MAX_WIDTH / 2,
        )
        self.assertGreaterEqual(
            min(eagle.y for eagle in flock), EAGLE_MAX_HEIGHT / 2
        )
        self.assertGreaterEqual(
            abs(flock[0].x - flock[1].x), EAGLE_MAX_WIDTH
        )
        self.assertGreaterEqual(
            abs(flock[0].y - flock[5].y), EAGLE_MAX_HEIGHT
        )

        flock[0].advance_animation(FRAME_INTERVAL_SECONDS)
        self.assertEqual(flock[0].frame_index, 1)
        self.assertTrue(all(eagle.frame_index == 0 for eagle in flock[1:]))

    def test_flock_rejects_canvas_too_small_for_non_overlapping_layout(self):
        with self.assertRaises(ValueError):
            create_flock(400, 600)
        with self.assertRaises(ValueError):
            create_flock(1600, 200)


if __name__ == "__main__":
    unittest.main()
