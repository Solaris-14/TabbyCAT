# Contributing to TabbyPatrol 🐾

Thank you for your interest in contributing to **TabbyPatrol**! We welcome contributions ranging from new pixel-art mascot skins and hammer effects to enhanced Computer Vision models and platform ports.

---

## 🛠️ Development Setup

1. Fork & clone the repository:
   ```bash
   git clone https://github.com/your-username/tabbypatrol.git
   cd tabbypatrol
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run the automated tests to verify setup:
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```
4. Run the desktop application:
   ```bash
   python overlay/tabby_overlay.py
   ```

---

## 🎨 Adding New Pet Skins or Hammer Variants

All pixel-art sprites are generated in [overlay/cat_sprites.py](overlay/cat_sprites.py) and [overlay/pillow_sprites.py](overlay/pillow_sprites.py) using procedural Pillow drawings.
- If you're designing a new mascot (e.g. Shiba Inu, Duck, Capybara), create a new sprite generator function returning a PIL `RGBA` image.
- Match the standard bounding canvas (~42x42 base) so the alignment with the [X] close button remains pixel-perfect!

---

## 🧪 Submitting Pull Requests

- Keep PRs focused on a single feature or bug fix.
- Ensure all tests pass (`python -m unittest tests/test_tabby.py`).
- Add tests for any new features in `tests/test_tabby.py`.
