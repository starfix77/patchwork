# Génération Pêle-mêle photos
Vous pouvez créer un pêle-mêle photo façon patchwork en choisissant un dossier ayant plusieurs fichiers JPG/JPEG
Les photos seront disposées sur le fond noir avec des rotations différentes et aléatoires, comme un montage photographique ou un mur de photos.

## Fonctionnalités principales:
- Une image finale de width × height pixels.
- Un fond noir.
- Jusqu'à max_photo photos JPG.
- Un cadre blanc fin autour de chaque photo.
- Des angles de rotation différents (horizontal, incliné à gauche ou à droite).
- Des tailles de photos variables pour un rendu plus naturel.
- Une disposition répartie sur toute la surface, sans alignement strict en grille.
- Les proportions originales des photos.
- Taille ±40 % : chaque photo reçoit un facteur aléatoire entre 0,6 et 1,4 (SIZE_VARIATION = 0.40).
- Chevauchement : les photos sont agrandies de base (OVERLAP_BASE = 1.35) pour dépasser de leur zone et empiéter sur leurs voisines. Augmentez cette valeur pour plus de recouvrement, diminuez-la pour moins.
- Décalage aléatoire : le centre de chaque photo est déplacé au hasard (JITTER = 0.30), ce qui évite tout alignement.
- Ordre d’empilement aléatoire : certaines photos passent au-dessus des autres.


![Exemple de rendu](example_1.jpg) 
![Exemple de rendu](example_2.jpg) 



## Prérequis:

| Outil | Windows | Linux | macOS |
|---|---|---|---|
| **Python 3.10+** | https://www.python.org/downloads/ | Debian / Ubuntu / Mint<br> `sudo apt install python3 python3-pip python3-venv`<br><br>RedHat /  Fedora<br> `sudo dnf install python3 python3-pip python3-venv` | `brew install python`| `brew install python`  |
*Note pour MacOS: Homebrew doit être installé au préalable (https://brew.sh). Sur macOS, brew install python installe la dernière version stable de Python 3, et python3 / pip3 sont alors disponibles dans le PATH.*

```bash
pip install Pillow
```


## Usage:
patchwork.py [-h] [--path PATH]
                    [--max_photo MAX_PHOTO]
                    [--width WIDTH]
                    [--height HEIGHT]
                    [--output OUTPUT]

```bash
# Aide / Usage
python patchwork.py --help


# Génération d'un patchwork photo
python patchwork.py --path ./photos --max_photo 20 --width 3840 --height 1200 --output patchwork_holiday.jpg
```


options:
*  **-h, --help**
      show this help message and exit

*  **--path** PATH
      Répertoire contenant les photos (default: .)

*  **--max_photo** MAX_PHOTO
      Nombre maximum de photos (default: 15)

*  **--width** WIDTH
      Largeur du canvas (default: 1920)

*  **--height** HEIGHT
      Hauteur du canvas (default: 1200)

*  **--output** OUTPUT
      Nom du fichier de sortie (default: patchwork.jpg)
```
