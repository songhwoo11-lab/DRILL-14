SPRITE_SHEET_WIDTH = 918
SPRITE_SHEET_HEIGHT = 506

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


def frame_source_rect(frame_index):
    left, top, right, bottom = EAGLE_FRAME_BOUNDS[frame_index]
    return (
        left,
        SPRITE_SHEET_HEIGHT - bottom,
        right - left,
        bottom - top,
    )
