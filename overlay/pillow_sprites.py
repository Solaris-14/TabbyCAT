"""
Pillow Sprites & Tactical Sniper Cat Animations for TabbyPatrol
Features the Elite Sniper Kitten on its plush cushion:
- Snoozing loaf
- Perching behind a tactical .50 cal / railgun sniper rifle with scope & bipod
- Peering through high-magnification scope with laser aiming sight
- Rapid-fire muzzle flash & casing ejection
- Quick bolt-action cycling (chambering next round for multi-target quick succession)
- Smug post-shot pose blowing smoke from the barrel
"""

from PIL import Image, ImageDraw


def create_pillow_sprite(color_theme="pink", scale=1.35):
    """
    Renders plush cushion with puffy contours, center tuft button, and corner tassels.
    Returns a PIL RGBA Image scaled by `scale`.
    """
    w, h = 80, 44
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    themes = {
        "pink": {
            "main": (251, 207, 232, 255),
            "shade": (244, 114, 182, 255),
            "shadow": (219, 39, 119, 255),
            "highlight": (253, 242, 248, 255),
            "tassel": (251, 191, 36, 255),
            "tassel_dark": (217, 119, 6, 255)
        },
        "lavender": {
            "main": (233, 213, 255, 255),
            "shade": (192, 132, 252, 255),
            "shadow": (147, 51, 234, 255),
            "highlight": (250, 245, 255, 255),
            "tassel": (251, 191, 36, 255),
            "tassel_dark": (217, 119, 6, 255)
        },
        "mint": {
            "main": (204, 251, 241, 255),
            "shade": (94, 234, 212, 255),
            "shadow": (13, 148, 136, 255),
            "highlight": (240, 253, 250, 255),
            "tassel": (251, 191, 36, 255),
            "tassel_dark": (217, 119, 6, 255)
        }
    }

    t = themes.get(color_theme, themes["pink"])

    # Drop shadow below cushion
    d.ellipse([10, 26, 70, 42], fill=(40, 20, 30, 80))

    # Outer Cushion Body
    d.rounded_rectangle([6, 10, 74, 38], radius=16, fill=t["shade"], outline=t["shadow"], width=2)
    # Inner Soft Cushion Highlight
    d.rounded_rectangle([10, 12, 70, 34], radius=14, fill=t["main"])
    # Top Puff Highlight
    d.ellipse([14, 13, 66, 25], fill=t["highlight"])

    # Center Tuft Button & Creases
    cx, cy = 40, 24
    d.ellipse([cx - 3, cy - 2, cx + 3, cy + 2], fill=t["shadow"])
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 1], fill=t["tassel"])

    d.line([(cx - 2, cy), (cx - 18, cy - 5)], fill=t["shade"], width=2)
    d.line([(cx + 2, cy), (cx + 18, cy - 5)], fill=t["shade"], width=2)
    d.line([(cx - 2, cy + 1), (cx - 14, cy + 7)], fill=t["shade"], width=2)
    d.line([(cx + 2, cy + 1), (cx + 14, cy + 7)], fill=t["shade"], width=2)

    # Corner Tassels
    tassels = [(6, 12), (72, 12), (6, 36), (72, 36)]
    for tx, ty in tassels:
        d.ellipse([tx - 3, ty - 3, tx + 3, ty + 3], fill=t["tassel_dark"])
        d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=t["tassel"])
        d.polygon([(tx - 3, ty + 2), (tx + 3, ty + 2), (tx + 5, ty + 8), (tx - 5, ty + 8)], fill=t["tassel"])

    target_w = int(w * scale)
    target_h = int(h * scale)
    return img.resize((target_w, target_h), Image.Resampling.NEAREST)


def create_pillow_with_cat(action="sleep", sub_frame=0, color_theme="pink", facing_left=True, scale=1.35):
    """
    Renders composite of the plush pillow and the tactical sniper kitten.
    Actions:
    - 'sleep': Cozy sleeping loaf
    - 'sit': Sitting upright
    - 'knead': Kneading paws on cushion
    - 'sniper_aim': Looking through high-tech scope, bipod planted, barrel raised
    - 'sniper_fire': Muzzle flash, brass casing ejection, recoil
    - 'sniper_chamber': Working the bolt-action (CH-CHK!), casing flying
    - 'sniper_smug': Lowered sniper rifle, blowing smoke from barrel, victory wink
    """
    base_w, base_h = 80, 56
    composite = Image.new("RGBA", (base_w, base_h), (0, 0, 0, 0))

    # Cushion
    pillow_img = create_pillow_sprite(color_theme=color_theme, scale=1.0)
    composite.paste(pillow_img, (0, 12), pillow_img)

    d = ImageDraw.Draw(composite)

    ORANGE = (249, 115, 22, 255)
    DARK_ORANGE = (194, 65, 12, 255)
    STRIPE = (154, 52, 18, 255)
    CREAM = (255, 237, 213, 255)
    WHITE = (255, 255, 255, 255)
    PINK = (244, 114, 182, 255)
    BLACK = (28, 25, 23, 255)
    GUN_STEEL = (45, 52, 62, 255)
    GUN_DARK = (20, 24, 30, 255)
    GUN_METAL = (100, 110, 125, 255)
    SCOPE_CYAN = (56, 189, 248, 255)
    GOLD_CASING = (245, 158, 11, 255)
    MUZZLE_FLASH = (254, 240, 138, 255)
    RED = (239, 68, 68, 255)

    def p(x, y, color):
        if 0 <= x < base_w and 0 <= y < base_h:
            d.point((x, y), fill=color)

    def rect(x1, y1, x2, y2, color):
        d.rectangle([x1, y1, x2, y2], fill=color)

    if action == "sleep":
        bob = 1 if sub_frame % 2 == 1 else 0
        cat_x, cat_y = 26, 12 - bob

        rect(cat_x + 2, cat_y + 4, cat_x + 22, cat_y + 14, ORANGE)
        rect(cat_x + 4, cat_y + 2, cat_x + 20, cat_y + 4, ORANGE)
        rect(cat_x + 8, cat_y + 3, cat_x + 9, cat_y + 8, STRIPE)
        rect(cat_x + 14, cat_y + 3, cat_x + 15, cat_y + 8, STRIPE)

        rect(cat_x - 2, cat_y + 9, cat_x + 2, cat_y + 13, DARK_ORANGE)
        rect(cat_x, cat_y + 12, cat_x + 6, cat_y + 14, DARK_ORANGE)

        rect(cat_x + 18, cat_y + 3, cat_x + 26, cat_y + 12, ORANGE)
        rect(cat_x + 20, cat_y + 7, cat_x + 25, cat_y + 12, CREAM)

        rect(cat_x + 19, cat_y + 1, cat_x + 21, cat_y + 3, ORANGE)
        p(cat_x + 20, cat_y + 2, PINK)
        rect(cat_x + 24, cat_y + 1, cat_x + 26, cat_y + 3, ORANGE)
        p(cat_x + 25, cat_y + 2, PINK)

        p(cat_x + 22, cat_y + 7, BLACK)
        p(cat_x + 23, cat_y + 6, BLACK)
        p(cat_x + 25, cat_y + 7, BLACK)
        p(cat_x + 24, cat_y + 9, PINK)

    elif action == "sniper_aim":
        # Cat perched behind tactical sniper rifle, peering through scope
        cat_x, cat_y = 34, 8

        # 1. Cat Body (Crouched low behind rifle)
        rect(cat_x + 2, cat_y + 8, cat_x + 18, cat_y + 19, ORANGE)
        rect(cat_x + 6, cat_y + 10, cat_x + 14, cat_y + 18, CREAM)
        # Head tilted against the eyepiece
        rect(cat_x - 2, cat_y, cat_x + 12, cat_y + 9, ORANGE)
        rect(cat_x + 2, cat_y + 4, cat_x + 10, cat_y + 9, CREAM)
        # Ears pinned back
        rect(cat_x + 1, cat_y - 4, cat_x + 4, cat_y, ORANGE)
        p(cat_x + 2, cat_y - 2, PINK)
        rect(cat_x + 8, cat_y - 4, cat_x + 11, cat_y, ORANGE)
        p(cat_x + 9, cat_y - 2, PINK)

        # Eye against the scope (left eye closed in squint, right eye locked into scope)
        p(cat_x + 6, cat_y + 4, BLACK)
        rect(cat_x + 1, cat_y + 3, cat_x + 4, cat_y + 5, BLACK)
        p(cat_x + 2, cat_y + 3, SCOPE_CYAN) # eye glint
        p(cat_x + 4, cat_y + 6, PINK)

        # 2. Tactical Sniper Rifle (.50 cal / Railgun)
        # Bipod legs on cushion
        d.line([(22, 24), (18, 33)], fill=GUN_METAL, width=2)
        d.line([(24, 24), (28, 33)], fill=GUN_METAL, width=2)
        # Long heavy barrel pointing up-left towards tabs
        d.line([(6, 15), (32, 23)], fill=GUN_STEEL, width=4)
        # Muzzle brake at tip
        rect(4, 13, 8, 17, GUN_DARK)
        # Receiver & Stock
        rect(24, 20, 36, 26, GUN_DARK)
        # Scope on top
        rect(16, 13, 29, 18, GUN_STEEL)
        d.line([(16, 14), (16, 17)], fill=SCOPE_CYAN, width=1) # front objective lens
        d.line([(29, 14), (29, 17)], fill=SCOPE_CYAN, width=1) # eyepiece
        # Cat's paws gripping stock & trigger
        rect(22, 22, 25, 25, WHITE)
        rect(28, 22, 31, 25, WHITE)

    elif action == "sniper_fire":
        # MUZZLE FLASH! High recoil, brass casing ejecting
        cat_x, cat_y = 36, 8 # pushed back 2px by recoil

        rect(cat_x + 2, cat_y + 8, cat_x + 18, cat_y + 19, ORANGE)
        rect(cat_x + 6, cat_y + 10, cat_x + 14, cat_y + 18, CREAM)
        rect(cat_x - 2, cat_y, cat_x + 12, cat_y + 9, ORANGE)
        rect(cat_x + 2, cat_y + 4, cat_x + 10, cat_y + 9, CREAM)

        # Fierce eye
        rect(cat_x + 1, cat_y + 3, cat_x + 4, cat_y + 5, BLACK)
        p(cat_x + 2, cat_y + 3, WHITE)

        # Rifle recoiling
        d.line([(8, 16), (34, 24)], fill=GUN_STEEL, width=4)
        rect(6, 14, 10, 18, GUN_DARK)
        rect(26, 21, 38, 27, GUN_DARK)
        rect(18, 14, 31, 19, GUN_STEEL)

        # Giant Muzzle Flash Star at the barrel tip!
        d.polygon([(4, 15), (0, 10), (2, 15), (-2, 16), (2, 17), (0, 22), (4, 17), (7, 21), (6, 16)], fill=MUZZLE_FLASH)
        p(3, 16, RED)
        p(5, 15, WHITE)

        # Brass Shell Casing flying out top!
        rect(30, 9, 33, 12, GOLD_CASING)
        p(31, 8, WHITE) # shine

    elif action == "sniper_chamber":
        # Working the tactical bolt (CH-CHK!), casing tumbling, aiming at next target
        cat_x, cat_y = 34, 8

        rect(cat_x + 2, cat_y + 8, cat_x + 18, cat_y + 19, ORANGE)
        rect(cat_x + 6, cat_y + 10, cat_x + 14, cat_y + 18, CREAM)
        rect(cat_x - 2, cat_y, cat_x + 12, cat_y + 9, ORANGE)
        rect(cat_x + 2, cat_y + 4, cat_x + 10, cat_y + 9, CREAM)

        # Looking through scope
        rect(cat_x + 1, cat_y + 3, cat_x + 4, cat_y + 5, BLACK)
        p(cat_x + 2, cat_y + 3, SCOPE_CYAN)

        # Rifle
        d.line([(6, 15), (32, 23)], fill=GUN_STEEL, width=4)
        rect(4, 13, 8, 17, GUN_DARK)
        rect(24, 20, 36, 26, GUN_DARK)
        rect(16, 13, 29, 18, GUN_STEEL)

        # Paw pulling bolt back (action open)
        rect(28, 17, 31, 20, WHITE) # paw on bolt
        p(27, 20, GUN_METAL) # bolt handle

        # Casing spinning in air
        rect(28, 4, 31, 7, GOLD_CASING)

    elif action == "sniper_smug":
        # Smug Victory Pose: Rifle rested on bipod, blowing smoke, wink!
        cat_x, cat_y = 28, 6

        rect(cat_x + 4, cat_y + 8, cat_x + 18, cat_y + 20, ORANGE)
        rect(cat_x + 8, cat_y + 10, cat_x + 14, cat_y + 19, CREAM)
        rect(cat_x + 3, cat_y, cat_x + 19, cat_y + 9, ORANGE)
        rect(cat_x + 7, cat_y + 5, cat_x + 15, cat_y + 9, CREAM)

        # Smug winking eye (^ ~)
        p(cat_x + 6, cat_y + 3, BLACK)
        p(cat_x + 7, cat_y + 2, BLACK)
        p(cat_x + 8, cat_y + 3, BLACK)
        rect(cat_x + 12, cat_y + 3, cat_x + 15, cat_y + 3, BLACK)
        p(cat_x + 10, cat_y + 6, PINK)
        # Blush
        rect(cat_x + 5, cat_y + 5, cat_x + 7, cat_y + 6, PINK)
        rect(cat_x + 13, cat_y + 5, cat_x + 15, cat_y + 6, PINK)

        # Sniper rifle rested next to cat
        d.line([(10, 24), (26, 28)], fill=GUN_STEEL, width=3)
        rect(8, 22, 11, 25, GUN_DARK)
        # Tiny puff of smoke off the barrel
        p(7, 20, WHITE)
        p(5, 18, WHITE)
        p(6, 16, WHITE)

    elif action == "approved":
        # Proud scholar kitten: Sitting tall, golden reading glasses, happy anime eyes (^ . ^), blushing cheeks, open book!
        cat_x, cat_y = 28, 5
        nod = 1 if sub_frame % 2 == 1 else 0

        rect(cat_x + 4, cat_y + 8 + nod, cat_x + 18, cat_y + 20 + nod, ORANGE)
        rect(cat_x + 8, cat_y + 10 + nod, cat_x + 14, cat_y + 19 + nod, CREAM)
        rect(cat_x + 5, cat_y + 9 + nod, cat_x + 6, cat_y + 13 + nod, STRIPE)
        rect(cat_x + 16, cat_y + 9 + nod, cat_x + 17, cat_y + 13 + nod, STRIPE)

        rect(cat_x + 3, cat_y + nod, cat_x + 19, cat_y + 9 + nod, ORANGE)
        rect(cat_x + 7, cat_y + 5 + nod, cat_x + 15, cat_y + 9 + nod, CREAM)
        rect(cat_x + 4, cat_y - 4 + nod, cat_x + 7, cat_y + nod, ORANGE)
        rect(cat_x + 15, cat_y - 4 + nod, cat_x + 18, cat_y + nod, ORANGE)

        # Happy curved closed anime eyes (^ . ^)
        p(cat_x + 7, cat_y + 4 + nod, BLACK)
        p(cat_x + 8, cat_y + 3 + nod, BLACK)
        p(cat_x + 9, cat_y + 4 + nod, BLACK)

        p(cat_x + 13, cat_y + 4 + nod, BLACK)
        p(cat_x + 14, cat_y + 3 + nod, BLACK)
        p(cat_x + 15, cat_y + 4 + nod, BLACK)

        # Golden circular scholar reading glasses
        d.rectangle([cat_x + 6, cat_y + 2 + nod, cat_x + 10, cat_y + 5 + nod], outline=GOLD_CASING, width=1)
        d.rectangle([cat_x + 12, cat_y + 2 + nod, cat_x + 16, cat_y + 5 + nod], outline=GOLD_CASING, width=1)
        d.line([(cat_x + 10, cat_y + 3 + nod), (cat_x + 12, cat_y + 3 + nod)], fill=GOLD_CASING, width=1)

        # Nose & Blushing Cheeks
        p(cat_x + 11, cat_y + 6 + nod, PINK)
        rect(cat_x + 4, cat_y + 6 + nod, cat_x + 6, cat_y + 7 + nod, PINK)
        rect(cat_x + 16, cat_y + 6 + nod, cat_x + 18, cat_y + 7 + nod, PINK)

        # Paws resting on cushion
        rect(cat_x + 7, cat_y + 18 + nod, cat_x + 10, cat_y + 21 + nod, WHITE)
        rect(cat_x + 12, cat_y + 18 + nod, cat_x + 15, cat_y + 21 + nod, WHITE)

        # Tiny open book with emerald cover in front of cat
        rect(cat_x + 5, cat_y + 20 + nod, cat_x + 17, cat_y + 24 + nod, (16, 185, 129, 255))
        rect(cat_x + 7, cat_y + 20 + nod, cat_x + 15, cat_y + 23 + nod, WHITE)
        d.line([(cat_x + 11, cat_y + 20 + nod), (cat_x + 11, cat_y + 24 + nod)], fill=(5, 150, 105, 255), width=1)

    elif action == "knead":
        paw_step = sub_frame % 2
        cat_x, cat_y = 26, 8

        rect(cat_x + 4, cat_y + 6, cat_x + 22, cat_y + 18, ORANGE)
        rect(cat_x + 10, cat_y + 8, cat_x + 16, cat_y + 17, CREAM)
        rect(cat_x + 12, cat_y, cat_x + 24, cat_y + 8, ORANGE)
        rect(cat_x + 14, cat_y + 4, cat_x + 22, cat_y + 8, CREAM)
        rect(cat_x + 13, cat_y - 3, cat_x + 15, cat_y, ORANGE)
        rect(cat_x + 21, cat_y - 3, cat_x + 23, cat_y, ORANGE)

        p(cat_x + 15, cat_y + 3, BLACK)
        p(cat_x + 16, cat_y + 2, BLACK)
        p(cat_x + 20, cat_y + 2, BLACK)
        p(cat_x + 21, cat_y + 3, BLACK)
        p(cat_x + 18, cat_y + 5, PINK)

        if paw_step == 0:
            rect(cat_x + 13, cat_y + 18, cat_x + 16, cat_y + 22, WHITE)
            rect(cat_x + 19, cat_y + 16, cat_x + 22, cat_y + 19, WHITE)
        else:
            rect(cat_x + 13, cat_y + 16, cat_x + 16, cat_y + 19, WHITE)
            rect(cat_x + 19, cat_y + 18, cat_x + 22, cat_y + 22, WHITE)

        rect(cat_x - 1, cat_y + 10, cat_x + 4, cat_y + 13, DARK_ORANGE)

    else:
        # 'sit'
        blink = (sub_frame % 6 == 5)
        cat_x, cat_y = 28, 5

        rect(cat_x + 4, cat_y + 8, cat_x + 18, cat_y + 20, ORANGE)
        rect(cat_x + 8, cat_y + 10, cat_x + 14, cat_y + 19, CREAM)
        rect(cat_x + 5, cat_y + 9, cat_x + 6, cat_y + 13, STRIPE)
        rect(cat_x + 16, cat_y + 9, cat_x + 17, cat_y + 13, STRIPE)
        rect(cat_x + 3, cat_y, cat_x + 19, cat_y + 9, ORANGE)
        rect(cat_x + 7, cat_y + 5, cat_x + 15, cat_y + 9, CREAM)
        rect(cat_x + 4, cat_y - 4, cat_x + 7, cat_y, ORANGE)
        rect(cat_x + 15, cat_y - 4, cat_x + 18, cat_y, ORANGE)

        if blink:
            rect(cat_x + 7, cat_y + 4, cat_x + 10, cat_y + 4, BLACK)
            rect(cat_x + 12, cat_y + 4, cat_x + 15, cat_y + 4, BLACK)
        else:
            rect(cat_x + 7, cat_y + 2, cat_x + 10, cat_y + 5, BLACK)
            p(cat_x + 7, cat_y + 2, WHITE)
            rect(cat_x + 12, cat_y + 2, cat_x + 15, cat_y + 5, BLACK)
            p(cat_x + 12, cat_y + 2, WHITE)

        p(cat_x + 11, cat_y + 6, PINK)
        rect(cat_x + 6, cat_y + 19, cat_x + 9, cat_y + 22, WHITE)
        rect(cat_x + 13, cat_y + 19, cat_x + 16, cat_y + 22, WHITE)

    target_w = int(base_w * scale)
    target_h = int(base_h * scale)
    scaled = composite.resize((target_w, target_h), Image.Resampling.NEAREST)

    if not facing_left:
        scaled = scaled.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    return scaled


if __name__ == "__main__":
    for act in ["sleep", "sit", "knead", "approved", "sniper_aim", "sniper_fire", "sniper_chamber", "sniper_smug"]:
        im = create_pillow_with_cat(act, 0, scale=1.35)
        print(f"Sniper sprite '{act}': {im.size}")
