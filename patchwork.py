#!/usr/bin/env python3


'''
Génération pele-mlel  artistique du patchwork : les photos seront disposées sur le fond noir avec des rotations différentes et aléatoires, comme un montage photographique ou un mur de photos.

Le script conservera :
- Une image finale de 3840 × 1200 pixels.
- Un fond noir.
- Jusqu'à 20 photos JPG.
- Un cadre blanc fin autour de chaque photo.
- Des angles de rotation différents (horizontal, incliné à gauche ou à droite).
- Des tailles de photos variables pour un rendu plus naturel.
- Une disposition répartie sur toute la surface, sans alignement strict en grille.
- Les proportions originales des photos.

Usage:
pip install Pillow

python3 patchwork.py 


'''

from PIL import Image, ImageOps
from pathlib import Path
import random
import math

# ---------------- PARAMETRES ----------------
WIDTH, HEIGHT = 3840, 1200
MAX_PHOTOS = 100
OUTPUT = "patchwork.jpg"

BACKGROUND = (0, 0, 0)
FRAME_COLOR = (255, 255, 255)
FRAME_WIDTH = 5                  # épaisseur du cadre blanc en pixels
ANGLE_MIN, ANGLE_MAX = -30, 30     # inclinaison minimale et maximale en degrés
MARGIN = 35
GAP = 18

# Composition reproductible. Utiliser random.seed() pour varier à chaque lancement.
random.seed(42)

# ---------------- RECHERCHE DES PHOTOS ----------------
files = sorted(
    [p for p in Path(".").iterdir()
     if p.is_file()
     and p.suffix.lower() in (".jpg", ".jpeg")
     and p.name.lower() != OUTPUT.lower()],
    key=lambda p: p.name.lower()
)[:MAX_PHOTOS]

if not files:
    raise SystemExit("Aucun fichier JPG/JPEG trouvé dans le dossier courant.")

print(f"{len(files)} photo(s) trouvée(s).")

# ---------------- PREPARATION DU CANVAS ----------------
canvas = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)

# Les cases répartissent les photos sur toute la surface.
# Les photos sont ensuite tournées et de tailles variées : pas de grille horizontale rigide.
cols, rows = 20, 5
cell_w = (WIDTH - 2 * MARGIN - (cols - 1) * GAP) / cols
cell_h = (HEIGHT - 2 * MARGIN - (rows - 1) * GAP) / rows

slots = [(c, r) for r in range(rows) for c in range(cols)]
random.shuffle(slots)

# Angles distincts autant que possible, alternant inclinaisons gauche/droite.
angles = []
for i in range(len(files)):
    magnitude = random.uniform(ANGLE_MIN, ANGLE_MAX)
    sign = -1 if i % 2 else 1
    angles.append(sign * magnitude)
random.shuffle(angles)

# ---------------- ASSEMBLAGE ----------------
for i, path in enumerate(files):
    try:
        with Image.open(path) as im:
            photo = ImageOps.exif_transpose(im).convert("RGB")

        col, row = slots[i]
        center_x = MARGIN + col * (cell_w + GAP) + cell_w / 2
        center_y = MARGIN + row * (cell_h + GAP) + cell_h / 2

        angle = angles[i]
        theta = math.radians(abs(angle))
        cos_a, sin_a = math.cos(theta), math.sin(theta)

        # Dimensionner la photo pour que son cadre tourné reste dans sa case.
        # On tient compte de l'encombrement réel après rotation.
        available_w = cell_w * 0.88
        available_h = cell_h * 0.88
        source_w, source_h = photo.size

        # Dimensions maximales avant rotation, en tenant compte du cadre.
        framed_w = source_w + 2 * FRAME_WIDTH
        framed_h = source_h + 2 * FRAME_WIDTH

        scale_fit = min(
            available_w / (framed_w * cos_a + framed_h * sin_a),
            available_h / (framed_w * sin_a + framed_h * cos_a)
        )
        # Variation de taille pour un rendu moins uniforme.
        scale = scale_fit * random.uniform(0.78, 1.0)

        new_w = max(1, int(source_w * scale))
        new_h = max(1, int(source_h * scale))
        photo = photo.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Carte blanche avec la photo à l'intérieur.
        card = Image.new(
            "RGB",
            (photo.width + 2 * FRAME_WIDTH, photo.height + 2 * FRAME_WIDTH),
            FRAME_COLOR
        )
        card.paste(photo, (FRAME_WIDTH, FRAME_WIDTH))

        # Rotation avec coins transparents.
        rotated = card.convert("RGBA").rotate(
            angle,
            resample=Image.Resampling.BICUBIC,
            expand=True,
            fillcolor=(0, 0, 0, 0)
        )

        x = int(center_x - rotated.width / 2)
        y = int(center_y - rotated.height / 2)

        # Collage de la photo tournée sur le fond noir.
        canvas_rgba = canvas.convert("RGBA")
        canvas_rgba.alpha_composite(rotated, (x, y))
        canvas = canvas_rgba.convert("RGB")

        print(f"[{i + 1:02d}/{len(files):02d}] {path.name} — rotation {angle:+.1f}°")

    except Exception as exc:
        print(f"ERREUR avec {path.name} : {exc}")

# ---------------- ENREGISTREMENT ----------------
canvas.save(OUTPUT, "JPEG", quality=95, subsampling=0)

print("----------------------------------------")
print(f"Patchwork créé : {OUTPUT}")
print(f"Dimensions : {WIDTH} x {HEIGHT}")
