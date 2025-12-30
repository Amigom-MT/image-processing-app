# Application de Traitement d'Images

Application Python pour appliquer divers filtres et transformations sur des images.

## Description

Cette application permet d'appliquer les filtres suivants sur des images :

- **Négatif** : Inverse les couleurs de l'image
- **Noir & Blanc** : Convertit l'image en niveaux de gris
- **Sépia** : Applique un filtre sépia vintage
- **Miroir Vertical** : Retourne l'image verticalement
- **Miroir Horizontal** : Retourne l'image horizontalement
- **Clipping Sélectif** : Limite les valeurs de pixels dans une plage définie
- **Contraste** : Ajuste le contraste de l'image
- **Seuillage** : Applique un seuillage binaire
- **Désaturation** : Réduit la saturation des couleurs
- **Postérisation** : Réduit le nombre de couleurs (effet poster)

## Installation

### Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## Utilisation

### Syntaxe générale

```bash
python image_processing.py <image_entree> <image_sortie> --filter <filtre> [--param <valeur>]
```

### Exemples d'utilisation

#### Appliquer un filtre négatif
```bash
python image_processing.py input.jpg output.jpg --filter negative
```

#### Convertir en noir et blanc
```bash
python image_processing.py input.jpg output.jpg --filter bw
```

#### Appliquer un filtre sépia
```bash
python image_processing.py input.jpg output.jpg --filter sepia
```

#### Miroir vertical
```bash
python image_processing.py input.jpg output.jpg --filter mirror-v
```

#### Miroir horizontal
```bash
python image_processing.py input.jpg output.jpg --filter mirror-h
```

#### Clipping sélectif (valeurs par défaut)
```bash
python image_processing.py input.jpg output.jpg --filter clipping
```

#### Ajuster le contraste (facteur 2.0)
```bash
python image_processing.py input.jpg output.jpg --filter contrast --param 2.0
```

#### Seuillage avec valeur personnalisée (150)
```bash
python image_processing.py input.jpg output.jpg --filter threshold --param 150
```

#### Désaturation partielle (50%)
```bash
python image_processing.py input.jpg output.jpg --filter desaturation --param 0.5
```

#### Postérisation avec 8 niveaux
```bash
python image_processing.py input.jpg output.jpg --filter posterization --param 8
```

## Filtres disponibles

| Filtre | Commande | Paramètre optionnel | Description |
|--------|----------|---------------------|-------------|
| Négatif | `negative` | Non | Inverse toutes les couleurs |
| Noir & Blanc | `bw` | Non | Conversion en niveaux de gris |
| Sépia | `sepia` | Non | Applique une teinte sépia |
| Miroir Vertical | `mirror-v` | Non | Retourne l'image de haut en bas |
| Miroir Horizontal | `mirror-h` | Non | Retourne l'image de gauche à droite |
| Clipping | `clipping` | Non | Limite les valeurs entre 50 et 200 |
| Contraste | `contrast` | Oui (défaut: 1.5) | Facteur de contraste (>1 augmente, <1 diminue) |
| Seuillage | `threshold` | Oui (défaut: 128) | Valeur de seuil (0-255) |
| Désaturation | `desaturation` | Oui (défaut: 0.5) | Facteur (0=N&B, 1=couleurs originales) |
| Postérisation | `posterization` | Oui (défaut: 4) | Nombre de niveaux par canal |

## Structure du projet

```
image-processing-app/
│
├── image_processing.py    # Module principal avec tous les filtres
├── requirements.txt        # Dépendances Python
├── README.md               # Ce fichier
└── LICENSE                 # Licence MIT
```

## Développement

### Architecture

L'application est organisée autour de la classe `ImageProcessor` qui encapsule toutes les opérations de traitement d'images. Chaque filtre est implémenté comme une méthode de cette classe.

### Ajouter un nouveau filtre

Pour ajouter un nouveau filtre :

1. Créez une nouvelle méthode dans la classe `ImageProcessor`
2. Ajoutez le filtre dans les choix de l'argument `--filter`
3. Ajoutez l'entrée correspondante dans le dictionnaire `filter_map`

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Contributeurs

Développé avec ❤️ pour le traitement d'images en Python.

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.
