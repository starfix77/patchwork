#!/usr/bin/env python3

'''
Génération pêle-mêle artistique du patchwork : les photos sont disposées sur un fond noir
avec des rotations aléatoires, des tailles variables (± 40 %) et se recouvrent partiellement,
comme un montage photographique ou un mur de photos.

Le script conserve :
- Une image finale de dimensions configurables (1920 × 1200 par défaut).
- Un fond noir.
- Jusqu'à --max_photo photos JPG.
- Un cadre blanc fin autour de chaque photo.
- Des angles de rotation différents (horizontal, incliné à gauche ou à droite).
- Une disposition répartie sur toute la surface, sans alignement strict en grille.
- Les proportions originales des photos.

Nouveau :
- Les photos se chevauchent partiellement (OVERLAP_BASE).
- La taille de chaque photo varie aléatoirement de ± 40 % (SIZE_VARIATION).
- Position légèrement décalée aléatoirement dans sa zone (JITTER).
- Ordre d'empilement aléatoire (certaines photos passent au-dessus des autres).

# Pré-requis:
pip install Pillow



# Usage: 

patchwork.py [-h] [--path PATH]
                    [--max_photo MAX_PHOTO]
                    [--width WIDTH]
                    [--height HEIGHT]
                    [--output OUTPUT]

Génération d'un patchwork photo

options:
  -h, --help
      show this help message and exit

  --path PATH
      Répertoire contenant les photos (default: .)

  --max_photo MAX_PHOTO
      Nombre maximum de photos (default: 15)

  --width WIDTH
      Largeur du canvas (default: 1920)

  --height HEIGHT
      Hauteur du canvas (default: 1200)

  --output OUTPUT
      Nom du fichier de sortie (default: patchwork.jpg)

'''

from PIL import Image, ImageOps
from pathlib import Path
import random
import argparse
import math

# ---------------- ARGUMENTS ----------------
parser = argparse.ArgumentParser(description="Génération d'un patchwork photo")
parser.add_argument("--path", default=".",
                    help="Répertoire contenant les photos (default: .)")
parser.add_argument("--max_photo", type=int, default=15,
                    help="Nombre maximum de photos (default: 15)")
parser.add_argument("--width", type=int, default=1920,
                    help="Largeur du canvas (default: 1920)")
parser.add_argument("--height", type=int, default=1200,
                    help="Hauteur du canvas (default: 1200)")
parser.add_argument("--output", default="patchwork.jpg",
                    help="Nom du fichier de sortie (default: patchwork.jpg)")
args = parser.parse_args()

if args.max_photo < 1:
    parser.error("--max_photo doit être supérieur ou égal à 1")
if args.width < 1 or args.height < 1:
    parser.error("--width et --height doivent être strictement positifs")

# ---------------- PARAMETRES ----------------
WIDTH, HEIGHT = args.width, args.height
MAX_PHOTOS = args.max_photo
OUTPUT = args.output

BACKGROUND = (0, 0, 0)
FRAME_COLOR = (255, 255, 255)
FRAME_WIDTH = 5                    # épaisseur du cadre blanc en pixels
ANGLE_MIN, ANGLE_MAX = -30, 30     # inclinaison minimale et maximale en degrés
MARGIN = 35

OVERLAP_BASE = 1.35                # >1 : les photos dépassent de leur zone => chevauchement
SIZE_VARIATION = 0.40              # variation de taille aléatoire : ± 40 %
JITTER = 0.30                      # décalage aléatoire du centre (fraction de la zone)

if WIDTH <= 2 * MARGIN or HEIGHT <= 2 * MARGIN:
    parser.error(f"Le canvas doit être plus grand que {2 * MARGIN} px dans chaque dimension")


# ---------------- RECHERCHE DES PHOTOS ----------------
directory = Path(args.path)

if not directory.is_dir():
    parser.error(f"Le répertoire n'existe pas : {directory}")

output_name = Path(OUTPUT).name.lower()

files = [
    p for p in directory.iterdir()
    if p.is_file()
    and p.suffix.lower() in (".jpg", ".jpeg")
    and p.name.lower() != output_name
]

if not files:
    raise SystemExit(f"Aucun fichier JPG/JPEG trouvé dans : {directory}")

# Mélanger aléatoirement les fichiers
random.shuffle(files)

# Conserver au maximum MAX_PHOTOS fichiers
files = files[:MAX_PHOTOS]

n = len(files)
print(f"{n} photo(s) trouvée(s).")

# Composition reproductible. Commenter la ligne pour varier à chaque lancement.
random.seed(42)


# ---------------- PREPARATION DU CANVAS ----------------
canvas = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)

# Grille adaptée au nombre de photos (zones de répartition, pas de placement rigide).
usable_w = WIDTH - 2 * MARGIN
usable_h = HEIGHT - 2 * MARGIN
rows = max(1, round(math.sqrt(n * usable_h / usable_w)))
cols = math.ceil(n / rows)
cell_w = usable_w / cols
cell_h = usable_h / rows

slots = [(c, r) for r in range(rows) for c in range(cols)]
random.shuffle(slots)
slots = slots[:n]

# Angles alternant inclinaisons gauche/droite.
angles = []
for i in range(n):
    magnitude = random.uniform(ANGLE_MIN, ANGLE_MAX)
    sign = -1 if i % 2 else 1
    angles.append(sign * magnitude)
random.shuffle(angles)

# Ordre d'empilement aléatoire (la dernière photo dessinée est au-dessus).
order = list(range(n))
random.shuffle(order)

# ---------------- ASSEMBLAGE ----------------
for rank, i in enumerate(order):
    path = files[i]
    try:
        with Image.open(path) as im:
            photo = ImageOps.exif_transpose(im).convert("RGB")

        col, row = slots[i]
        center_x = MARGIN + col * cell_w + cell_w / 2
        center_y = MARGIN + row * cell_h + cell_h / 2

        # Décalage aléatoire du centre pour casser l'alignement.
        center_x += random.uniform(-JITTER, JITTER) * cell_w
        center_y += random.uniform(-JITTER, JITTER) * cell_h

        angle = angles[i]
        theta = math.radians(abs(angle))
        cos_a, sin_a = math.cos(theta), math.sin(theta)

        source_w, source_h = photo.size
        framed_w = source_w + 2 * FRAME_WIDTH
        framed_h = source_h + 2 * FRAME_WIDTH

        # Échelle pour que la photo tournée remplisse exactement sa zone.
        scale_fit = min(
            cell_w / (framed_w * cos_a + framed_h * sin_a),
            cell_h / (framed_w * sin_a + framed_h * cos_a)
        )

        # Agrandissement de base (chevauchement) × variation aléatoire de ± 40 %.
        size_factor = random.uniform(1 - SIZE_VARIATION, 1 + SIZE_VARIATION)
        scale = scale_fit * OVERLAP_BASE * size_factor

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

        # Garder la photo entièrement dans l'image finale.
        x = int(center_x - rotated.width / 2)
        y = int(center_y - rotated.height / 2)
        x = max(0, min(x, WIDTH - rotated.width))
        y = max(0, min(y, HEIGHT - rotated.height))

        # Collage avec le canal alpha comme masque (les coins transparents restent transparents).
        canvas.paste(rotated, (x, y), rotated)

        print(f"[{rank + 1:02d}/{n:02d}] {path.name} — rotation {angle:+.1f}° — taille {size_factor * 100:.0f} %")

    except Exception as exc:
        print(f"ERREUR avec {path.name} : {exc}")

# ---------------- ENREGISTREMENT ----------------
canvas.save(OUTPUT, "JPEG", quality=95, subsampling=0)

print("----------------------------------------")
print(f"Patchwork créé : {OUTPUT}")
print(f"Dimensions : {WIDTH} x {HEIGHT}")
