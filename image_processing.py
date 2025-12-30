"""
Module de traitement d'images avec différents filtres
Auteur: Image Processing App
Date: 2025
"""

import numpy as np
from PIL import Image
import argparse
import os


class ImageProcessor:
    """Classe pour appliquer différents filtres sur les images"""
    
    def __init__(self, image_path):
        """Initialise le processeur avec une image
        
        Args:
            image_path: Chemin vers l'image à traiter
        """
        self.image = Image.open(image_path)
        self.pixels = np.array(self.image, dtype=np.float64)
        
    def negative(self):
        """Applique un filtre négatif à l'image"""
        result = 255 - self.pixels
        return Image.fromarray(result.astype(np.uint8))
    
    def black_and_white(self):
        """Convertit l'image en noir et blanc (niveaux de gris)"""
        if len(self.pixels.shape) == 3:
            # Formule standard de conversion RGB vers grayscale
            gray = 0.299 * self.pixels[:,:,0] + 0.587 * self.pixels[:,:,1] + 0.114 * self.pixels[:,:,2]
            result = np.stack([gray, gray, gray], axis=2)
        else:
            result = self.pixels
        return Image.fromarray(result.astype(np.uint8))
    
    def sepia(self):
        """Applique un filtre sépia à l'image"""
        if len(self.pixels.shape) == 2:
            pixels = np.stack([self.pixels, self.pixels, self.pixels], axis=2)
        else:
            pixels = self.pixels.copy()
            
        result = np.zeros_like(pixels)
        result[:,:,0] = 0.393 * pixels[:,:,0] + 0.769 * pixels[:,:,1] + 0.189 * pixels[:,:,2]  # Red
        result[:,:,1] = 0.349 * pixels[:,:,0] + 0.686 * pixels[:,:,1] + 0.168 * pixels[:,:,2]  # Green
        result[:,:,2] = 0.272 * pixels[:,:,0] + 0.534 * pixels[:,:,1] + 0.131 * pixels[:,:,2]  # Blue
        
        result = np.clip(result, 0, 255)
        return Image.fromarray(result.astype(np.uint8))
    
    def mirror_vertical(self):
        """Applique un miroir vertical (retournement haut/bas)"""
        result = np.flipud(self.pixels)
        return Image.fromarray(result.astype(np.uint8))
    
    def mirror_horizontal(self):
        """Applique un miroir horizontal (retournement gauche/droite)"""
        result = np.fliplr(self.pixels)
        return Image.fromarray(result.astype(np.uint8))
    
    def selective_clipping(self, min_val=50, max_val=200):
        """Applique un clipping sélectif des valeurs de pixels
        
        Args:
            min_val: Valeur minimale (par défaut 50)
            max_val: Valeur maximale (par défaut 200)
        """
        result = np.clip(self.pixels, min_val, max_val)
        return Image.fromarray(result.astype(np.uint8))
    
    def contrast(self, factor=1.5):
        """Ajuste le contraste de l'image
        
        Args:
            factor: Facteur de contraste (> 1 augmente, < 1 diminue)
        """
        mean = np.mean(self.pixels)
        result = mean + factor * (self.pixels - mean)
        result = np.clip(result, 0, 255)
        return Image.fromarray(result.astype(np.uint8))
    
    def threshold(self, threshold_value=128):
        """Applique un seuillage binaire à l'image
        
        Args:
            threshold_value: Valeur du seuil (par défaut 128)
        """
        if len(self.pixels.shape) == 3:
            gray = 0.299 * self.pixels[:,:,0] + 0.587 * self.pixels[:,:,1] + 0.114 * self.pixels[:,:,2]
        else:
            gray = self.pixels
            
        result = np.where(gray > threshold_value, 255, 0)
        if len(self.pixels.shape) == 3:
            result = np.stack([result, result, result], axis=2)
        return Image.fromarray(result.astype(np.uint8))
    
    def desaturation(self, factor=0.5):
        """Réduit la saturation de l'image
        
        Args:
            factor: Facteur de désaturation (0 = noir et blanc, 1 = couleurs originales)
        """
        if len(self.pixels.shape) == 3:
            gray = 0.299 * self.pixels[:,:,0] + 0.587 * self.pixels[:,:,1] + 0.114 * self.pixels[:,:,2]
            gray_stack = np.stack([gray, gray, gray], axis=2)
            result = factor * self.pixels + (1 - factor) * gray_stack
        else:
            result = self.pixels
        return Image.fromarray(result.astype(np.uint8))
    
    def posterization(self, levels=4):
        """Applique une postérisation à l'image (réduction du nombre de couleurs)
        
        Args:
            levels: Nombre de niveaux par canal de couleur (par défaut 4)
        """
        step = 256 // levels
        result = (self.pixels // step) * step
        return Image.fromarray(result.astype(np.uint8))


def main():
    parser = argparse.ArgumentParser(description='Application de traitement d\'images')
    parser.add_argument('input', help='Chemin de l\'image d\'entrée')
    parser.add_argument('output', help='Chemin de l\'image de sortie')
    parser.add_argument('--filter', required=True, 
                       choices=['negative', 'bw', 'sepia', 'mirror-v', 'mirror-h', 
                               'clipping', 'contrast', 'threshold', 'desaturation', 'posterization'],
                       help='Filtre à appliquer')
    parser.add_argument('--param', type=float, help='Paramètre du filtre (si applicable)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Erreur: Le fichier {args.input} n'existe pas")
        return
    
    processor = ImageProcessor(args.input)
    
    # Application du filtre sélectionné
    filter_map = {
        'negative': lambda: processor.negative(),
        'bw': lambda: processor.black_and_white(),
        'sepia': lambda: processor.sepia(),
        'mirror-v': lambda: processor.mirror_vertical(),
        'mirror-h': lambda: processor.mirror_horizontal(),
        'clipping': lambda: processor.selective_clipping(),
        'contrast': lambda: processor.contrast(args.param if args.param else 1.5),
        'threshold': lambda: processor.threshold(int(args.param) if args.param else 128),
        'desaturation': lambda: processor.desaturation(args.param if args.param else 0.5),
        'posterization': lambda: processor.posterization(int(args.param) if args.param else 4)
    }
    
    result_image = filter_map[args.filter]()
    result_image.save(args.output)
    print(f"Image traitée sauvegardée dans {args.output}")


if __name__ == '__main__':
    main()
