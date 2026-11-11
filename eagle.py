import game_framework
from pico2d import get_canvas_height, get_canvas_width, load_image


SPRITE_SHEET_WIDTH = 918
SPRITE_SHEET_HEIGHT = 506
SPRITE_SHEET_PATH = "bird_animation.png"
METERS_PER_PIXEL = 0.03
PIXELS_PER_METER = 1.0 / METERS_PER_PIXEL
FLIGHT_SPEED_KMPH = 60.0
FLIGHT_SPEED_MPS = FLIGHT_SPEED_KMPH * (1000.0 / 3600.0)
FLIGHT_SPEED_PPS = FLIGHT_SPEED_MPS * PIXELS_PER_METER
ANIMATION_CYCLE_DISTANCE_M = 7.0
ANIMATION_CYCLE_DISTANCE_PX = ANIMATION_CYCLE_DISTANCE_M * PIXELS_PER_METER
EAGLE_SCALE = 0.55

# Frame bounds use top-left origin and an exclusive right/bottom edge.
EAGLE_FRAME_BOUNDS = (
    (34, 1, 180, 144),
    (216, 2, 362, 143),
    (398, 12, 544, 142),
    (555, 17, 726, 139),
    (728, 48, 910, 136),
    (34, 217, 180, 335),
    (216, 216, 362, 340),
    (398, 216, 544, 336),
    (580, 217, 726, 326),
    (762, 219, 908, 329),
    (34, 392, 180, 500),
    (216, 394, 362, 500),
    (376, 395, 544, 483),
    (546, 370, 726, 484),
)
EAGLE_FRAME_COUNT = len(EAGLE_FRAME_BOUNDS)
ANIMATION_CYCLE_SECONDS = ANIMATION_CYCLE_DISTANCE_M / FLIGHT_SPEED_MPS
FRAME_INTERVAL_SECONDS = ANIMATION_CYCLE_SECONDS / EAGLE_FRAME_COUNT
EAGLE_MAX_WIDTH = (
    max(right - left for left, _, right, _ in EAGLE_FRAME_BOUNDS) * EAGLE_SCALE
)
EAGLE_MAX_HEIGHT = (
    max(bottom - top for _, top, _, bottom in EAGLE_FRAME_BOUNDS) * EAGLE_SCALE
)
EAGLE_COUNT = 10
FLOCK_COLUMNS = 5
FLOCK_ROWS = (EAGLE_COUNT + FLOCK_COLUMNS - 1) // FLOCK_COLUMNS


def frame_source_rect(frame_index):
    left, top, right, bottom = EAGLE_FRAME_BOUNDS[frame_index]
    return (
        left,
        SPRITE_SHEET_HEIGHT - bottom,
        right - left,
        bottom - top,
    )


class Eagle:
    _sprite_sheet = None

    def __init__(self, x, y, direction=1):
        if direction not in (-1, 1):
            raise ValueError("direction must be -1 or 1")
        if Eagle._sprite_sheet is None:
            Eagle._sprite_sheet = load_image(SPRITE_SHEET_PATH)

        self.x = x
        self.y = y
        self.direction = direction
        self.frame_index = 0
        self.animation_elapsed = 0.0

    def advance_animation(self, delta_time):
        if delta_time < 0:
            raise ValueError("delta_time cannot be negative")

        self.animation_elapsed += delta_time
        frames_advanced = int(
            (self.animation_elapsed + 1e-12) / FRAME_INTERVAL_SECONDS
        )
        if frames_advanced:
            self.frame_index = (
                self.frame_index + frames_advanced
            ) % EAGLE_FRAME_COUNT
            self.animation_elapsed -= frames_advanced * FRAME_INTERVAL_SECONDS
            self.animation_elapsed = max(0.0, self.animation_elapsed)

    def advance(self, delta_time):
        self.advance_animation(delta_time)
        self._advance_horizontal(FLIGHT_SPEED_PPS * delta_time, get_canvas_width())
        canvas_height = get_canvas_height()
        half_height = EAGLE_MAX_HEIGHT / 2
        if canvas_height <= EAGLE_MAX_HEIGHT:
            self.y = canvas_height / 2
        else:
            self.y = min(max(self.y, half_height), canvas_height - half_height)

    def _advance_horizontal(self, distance, canvas_width):
        half_width = EAGLE_MAX_WIDTH / 2
        if canvas_width <= EAGLE_MAX_WIDTH:
            self.x = canvas_width / 2
            return

        left_edge = half_width
        right_edge = canvas_width - half_width
        span = right_edge - left_edge
        offset = min(max(self.x - left_edge, 0.0), span)
        phase = offset if self.direction == 1 else 2 * span - offset
        phase = (phase + distance) % (2 * span)

        if phase < span:
            self.x = left_edge + phase
            self.direction = 1
        else:
            self.x = right_edge - (phase - span)
            self.direction = -1

    def update(self):
        self.advance(game_framework.frame_time)

    def draw(self):
        source_rect = frame_source_rect(self.frame_index)
        source_width, source_height = source_rect[2:]
        flip = "h" if self.direction == -1 else ""
        Eagle._sprite_sheet.clip_composite_draw(
            *source_rect,
            0,
            flip,
            self.x,
            self.y,
            source_width * EAGLE_SCALE,
            source_height * EAGLE_SCALE,
        )


def create_flock(canvas_width, canvas_height):
    if canvas_width <= 0 or canvas_height <= 0:
        raise ValueError("canvas dimensions must be positive")

    if canvas_width < EAGLE_MAX_WIDTH * (FLOCK_COLUMNS + 1):
        raise ValueError("canvas is too narrow for a non-overlapping flock")
    if canvas_height < EAGLE_MAX_HEIGHT * (FLOCK_ROWS + 1):
        raise ValueError("canvas is too short for a non-overlapping flock")

    half_width = EAGLE_MAX_WIDTH / 2
    available_width = canvas_width - EAGLE_MAX_WIDTH

    flock = []
    for index in range(EAGLE_COUNT):
        row, column = divmod(index, FLOCK_COLUMNS)
        x = half_width + available_width * (column + 0.5) / FLOCK_COLUMNS
        y = canvas_height * (row + 1) / (FLOCK_ROWS + 1)
        flock.append(Eagle(x, y))
    return flock
