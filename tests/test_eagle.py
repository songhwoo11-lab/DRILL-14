import unittest

from eagle import (
    ANIMATION_CYCLE_DISTANCE_M,
    ANIMATION_CYCLE_DISTANCE_PX,
    ANIMATION_CYCLE_SECONDS,
    EAGLE_FRAME_BOUNDS,
    EAGLE_FRAME_COUNT,
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


if __name__ == "__main__":
    unittest.main()
