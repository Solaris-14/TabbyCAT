"""
Cat Sprites & Animation Frames Generator for TabbyPatrol
Generates refined, compact pixel art kitten sprites (~54x54px)
with the giant sledgehammer strike aligned directly to smash the tab's [X] button.
"""

from PIL import Image, ImageDraw


def create_cat_frame(state="idle", sub_frame=0, facing_right=True, scale=1.35):
    """
    Renders pixel art kitten.
    Base size is 42x42 (compact and cute), scaled cleanly to ~56x56 px.
    Returns PIL Image (RGBA).
    """
    w, h = 42, 42
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Palette
    ORANGE = (249, 115, 22, 255)
    DARK_ORANGE = (194, 65, 12, 255)
    STRIPE = (154, 52, 18, 255)
    CREAM = (255, 237, 213, 255)
    WHITE = (255, 255, 255, 255)
    PINK = (244, 114, 182, 255)
    BLACK = (28, 25, 23, 255)
    RED = (239, 68, 68, 255)
    YELLOW = (250, 204, 21, 255)

    # Hammer Palette
    HAMMER_STEEL = (71, 85, 105, 255)
    HAMMER_DARK = (30, 41, 59, 255)
    HAMMER_LIGHT = (203, 213, 225, 255)
    HAMMER_WOOD = (146, 64, 14, 255)
    GOLD = (245, 158, 11, 255)

    def p(x, y, color):
        if 0 <= x < w and 0 <= y < h:
            d.point((x, y), fill=color)

    def rect(x1, y1, x2, y2, color):
        d.rectangle([x1, y1, x2, y2], fill=color)

    if state == "hammer_windup":
        # Cat leaping high, holding the massive hammer backwards over its head
        bob = sub_frame % 2

        # 1. Giant Mallet Head (Held high overhead)
        d.line([(14, 12), (24, 26)], fill=HAMMER_WOOD, width=3)
        rect(5, 2 - bob, 20, 14 - bob, HAMMER_STEEL)
        d.rectangle([5, 2 - bob, 20, 14 - bob], outline=HAMMER_DARK, width=1)
        rect(10, 2 - bob, 15, 14 - bob, HAMMER_LIGHT) # steel band
        p(7, 4 - bob, GOLD)
        p(7, 12 - bob, GOLD)
        p(18, 4 - bob, GOLD)
        p(18, 12 - bob, GOLD)
        # Power sparks
        p(3, 2 - bob, YELLOW)
        p(22, 3 - bob, YELLOW)

        # 2. Cat Body in mid-air
        rect(20, 22, 31, 31, ORANGE)
        rect(23, 24, 28, 30, CREAM)
        rect(18, 30, 21, 33, WHITE) # feet curled
        rect(28, 30, 31, 33, WHITE)
        # Tail whipping
        rect(31, 25, 37, 28, DARK_ORANGE)
        rect(35, 21, 38, 25, DARK_ORANGE)

        # 3. Head fierce & focused
        rect(22, 15, 33, 23, ORANGE)
        rect(24, 19, 31, 23, CREAM)
        # Ears pinned back
        rect(23, 11, 26, 15, ORANGE)
        p(24, 13, PINK)
        rect(29, 11, 32, 15, ORANGE)
        p(30, 13, PINK)
        # Determined eyes (> <)
        p(25, 17, BLACK)
        p(26, 18, BLACK)
        p(30, 17, BLACK)
        p(29, 18, BLACK)
        p(28, 20, PINK) # nose
        # Paws gripping handle
        rect(21, 24, 25, 27, WHITE)
        rect(24, 22, 27, 25, WHITE)

    elif state == "hammer_slam":
        # THE IMPACT! Mallet head smashed down directly on target
        # 1. Smashed Mallet Head flat on bottom edge (X ~ 4..24, Y ~ 28..38)
        rect(4, 28, 24, 38, HAMMER_STEEL)
        d.rectangle([4, 28, 24, 38], outline=HAMMER_DARK, width=1)
        rect(12, 28, 16, 38, HAMMER_LIGHT)
        p(7, 30, GOLD)
        p(7, 36, GOLD)
        p(21, 30, GOLD)
        p(21, 36, GOLD)

        # Handle angled up into cat's paws
        d.line([(14, 28), (25, 19)], fill=HAMMER_WOOD, width=3)

        # 2. Cat slamming full body weight down
        rect(20, 20, 34, 31, ORANGE)
        rect(23, 22, 30, 30, CREAM)
        rect(22, 31, 25, 36, WHITE) # feet braced
        rect(30, 31, 33, 36, WHITE)
        # Tail puffed up
        rect(34, 22, 39, 26, DARK_ORANGE)
        rect(37, 18, 40, 22, DARK_ORANGE)

        # Head lowered forward
        rect(19, 15, 29, 23, ORANGE)
        rect(21, 19, 27, 23, CREAM)
        rect(19, 12, 22, 15, ORANGE)
        rect(26, 12, 29, 15, ORANGE)
        # Gritted triumph eyes
        p(22, 18, BLACK)
        p(26, 18, BLACK)
        p(24, 20, PINK)
        # Paws on handle
        rect(22, 18, 26, 21, WHITE)

        # 3. Comic sparks around hammer head
        p(1, 30, YELLOW)
        p(0, 31, RED)
        p(2, 35, YELLOW)
        p(26, 30, YELLOW)
        p(27, 31, RED)
        p(25, 35, YELLOW)
        p(10, 25, YELLOW)
        p(18, 24, YELLOW)

    elif state == "hammer_rest":
        # Proud Victory Pose: Giant Hammer rested over shoulder
        bob = sub_frame % 2

        # 1. Hammer over shoulder
        d.line([(18, 26 - bob), (32, 10 - bob)], fill=HAMMER_WOOD, width=3)
        rect(26, 2 - bob, 38, 14 - bob, HAMMER_STEEL)
        d.rectangle([26, 2 - bob, 38, 14 - bob], outline=HAMMER_DARK, width=1)
        rect(30, 2 - bob, 34, 14 - bob, HAMMER_LIGHT)
        p(28, 4 - bob, GOLD)
        p(36, 4 - bob, GOLD)
        # Smoke puff
        p(38, 1 - bob, WHITE)

        # 2. Cat Body upright
        rect(13, 19 - bob, 24, 31 - bob, ORANGE)
        rect(15, 21 - bob, 21, 30 - bob, CREAM)
        rect(14, 31 - bob, 17, 35 - bob, WHITE)
        rect(20, 31 - bob, 23, 35 - bob, WHITE)
        # Tail swishing
        rect(8, 23 - bob, 13, 27 - bob, DARK_ORANGE)
        rect(6, 20 - bob, 9, 23 - bob, DARK_ORANGE)

        # 3. Smug head
        rect(12, 10 - bob, 23, 19 - bob, ORANGE)
        rect(14, 15 - bob, 21, 19 - bob, CREAM)
        rect(13, 7 - bob, 16, 10 - bob, ORANGE)
        p(14, 8 - bob, PINK)
        rect(19, 7 - bob, 22, 10 - bob, ORANGE)
        p(20, 8 - bob, PINK)
        # Winking eye (^ ~)
        p(14, 13 - bob, BLACK)
        p(15, 12 - bob, BLACK)
        p(16, 13 - bob, BLACK)
        rect(18, 13 - bob, 21, 13 - bob, BLACK)
        p(17, 16 - bob, PINK)
        # Pink blush
        rect(13, 15 - bob, 14, 16 - bob, PINK)
        rect(20, 15 - bob, 21, 16 - bob, PINK)
        rect(17, 22 - bob, 20, 25 - bob, WHITE) # paw holding handle

    elif state == "walk":
        # Fast running sprint (4 frames)
        frame = sub_frame % 4
        bob = 1 if frame in (1, 3) else 0

        rect(10, 18 - bob, 25, 29 - bob, ORANGE)
        rect(13, 20 - bob, 22, 27 - bob, CREAM)
        rect(16, 18 - bob, 18, 22 - bob, STRIPE)

        # Head leaning forward
        rect(22, 11 - bob, 32, 21 - bob, ORANGE)
        rect(25, 16 - bob, 31, 21 - bob, CREAM)
        rect(23, 8 - bob, 26, 11 - bob, ORANGE)
        p(24, 9 - bob, PINK)
        rect(28, 8 - bob, 31, 11 - bob, ORANGE)
        p(29, 9 - bob, PINK)
        # Running eyes
        rect(26, 14 - bob, 28, 16 - bob, BLACK)
        p(26, 14 - bob, WHITE)
        rect(29, 14 - bob, 31, 16 - bob, BLACK)
        p(29, 14 - bob, WHITE)
        p(29, 18 - bob, PINK)

        # Legs
        if frame == 0:
            rect(11, 29 - bob, 14, 34, WHITE)
            rect(22, 29 - bob, 25, 34, WHITE)
            rect(6, 20 - bob, 10, 24 - bob, DARK_ORANGE)
        elif frame == 1:
            rect(13, 28, 16, 32, WHITE)
            rect(20, 28, 23, 32, WHITE)
            rect(5, 19, 9, 23, DARK_ORANGE)
        elif frame == 2:
            rect(15, 29 - bob, 18, 34, WHITE)
            rect(18, 29 - bob, 21, 34, WHITE)
            rect(6, 20 - bob, 10, 24 - bob, DARK_ORANGE)
        else:
            rect(13, 28, 16, 32, WHITE)
            rect(20, 28, 23, 32, WHITE)
            rect(5, 19, 9, 23, DARK_ORANGE)

    elif state == "alert":
        # Alert posture
        rect(13, 17, 26, 29, ORANGE)
        rect(16, 20, 23, 28, CREAM)
        rect(15, 29, 18, 33, WHITE)
        rect(21, 29, 24, 33, WHITE)
        # Head
        rect(13, 8, 26, 18, ORANGE)
        rect(15, 14, 24, 18, CREAM)
        rect(13, 4, 17, 8, ORANGE)
        p(15, 6, PINK)
        rect(22, 4, 26, 8, ORANGE)
        p(24, 6, PINK)
        # Alert eyes
        rect(15, 10, 18, 13, BLACK)
        p(15, 10, WHITE)
        rect(21, 10, 24, 13, BLACK)
        p(21, 10, WHITE)
        p(19, 14, PINK)
        rect(24, 19, 29, 22, DARK_ORANGE)
        rect(27, 14, 30, 19, DARK_ORANGE)
        # Exclamation Mark
        rect(18, 0, 20, 2, RED)
        rect(18, 4, 20, 4, RED)

    else:
        # Default: IDLE
        blink = (sub_frame % 6 == 5)
        tail_wag = (sub_frame % 4)

        rect(12, 18, 26, 29, ORANGE)
        rect(15, 20, 23, 28, CREAM)
        rect(12, 9, 26, 18, ORANGE)
        rect(15, 14, 23, 18, CREAM)
        rect(13, 5, 16, 9, ORANGE)
        p(14, 7, PINK)
        rect(22, 5, 25, 9, ORANGE)
        p(23, 7, PINK)

        if blink:
            rect(15, 12, 18, 12, BLACK)
            rect(20, 12, 23, 12, BLACK)
        else:
            rect(15, 10, 18, 13, BLACK)
            p(15, 10, WHITE)
            rect(20, 10, 23, 13, BLACK)
            p(20, 10, WHITE)
        p(19, 15, PINK)
        rect(14, 29, 17, 32, WHITE)
        rect(21, 29, 24, 32, WHITE)

        if tail_wag == 0:
            rect(7, 23, 12, 26, DARK_ORANGE)
            rect(5, 20, 8, 23, DARK_ORANGE)
        else:
            rect(7, 22, 12, 25, DARK_ORANGE)
            rect(6, 18, 9, 22, DARK_ORANGE)

    # Resize cleanly
    target_w = int(w * scale)
    target_h = int(h * scale)
    scaled = img.resize((target_w, target_h), Image.Resampling.NEAREST)
    if not facing_right:
        scaled = scaled.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    return scaled


if __name__ == "__main__":
    for st in ["hammer_windup", "hammer_slam", "hammer_rest", "walk", "alert", "idle"]:
        im = create_cat_frame(st, 0, facing_right=True, scale=1.35)
        print(f"Cat sprite '{st}': {im.size}")
