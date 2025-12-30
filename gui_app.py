#!/usr/bin/env python3
"""
Interface graphique pour l'application de traitement d'images
Permet d'appliquer plusieurs filtres avec des jauges ajustables
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from image_processing import ImageProcessor
import os


class ImageProcessingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Traitement d'Images - Interface Graphique")
        self.root.geometry("1200x700")
        
        self.original_image = None
        self.processed_image = None
        self.current_image_path = None
        self.processor = None
        
        # Variables pour les filtres
        self.filter_vars = {}
        self.param_vars = {}
        
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # === BARRE DE BOUTONS ===
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        ttk.Button(btn_frame, text="📁 Charger Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✨ Appliquer Filtres", command=self.apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Sauvegarder", command=self.save_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Réinitialiser", command=self.reset_image).pack(side=tk.LEFT, padx=5)
        
        # === PANEL DE FILTRES (Gauche) ===
        filters_frame = ttk.LabelFrame(main_frame, text="Filtres Disponibles", padding="10")
        filters_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.W), padx=(0, 10))
        
        # Canvas avec scrollbar pour les filtres
        canvas = tk.Canvas(filters_frame, width=250)
        scrollbar = ttk.Scrollbar(filters_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Filtres simples (sans paramètre)
        simple_filters = [
            ("Négatif", "negative"),
            ("Noir & Blanc", "bw"),
            ("Sépia", "sepia"),
            ("Miroir Vertical", "mirror_v"),
            ("Miroir Horizontal", "mirror_h"),
            ("Clipping Sélectif", "clipping")
        ]
        
        ttk.Label(scrollable_frame, text="Filtres Simples:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        for label, filter_name in simple_filters:
            var = tk.BooleanVar()
            self.filter_vars[filter_name] = var
            ttk.Checkbutton(scrollable_frame, text=label, variable=var).pack(anchor=tk.W, pady=2)
        
        ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Filtres avec paramètres ajustables
        ttk.Label(scrollable_frame, text="Filtres Ajustables:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # CONTRASTE
        self.create_filter_with_slider(scrollable_frame, "Contraste", "contrast", 0.1, 3.0, 1.5, "x")
        
        # SEUILLAGE
        self.create_filter_with_slider(scrollable_frame, "Seuillage", "threshold", 0, 255, 128, "")
        
        # DÉSATURATION
        self.create_filter_with_slider(scrollable_frame, "Désaturation", "desaturation", 0.0, 1.0, 0.5, "")
        
        # POSTÉRISATION
        self.create_filter_with_slider(scrollable_frame, "Postérisation", "posterization", 2, 16, 4, " niveaux")
        
        # === IMAGE ORIGINALE (Centre) ===
        original_frame = ttk.LabelFrame(main_frame, text="Image Originale", padding="10")
        original_frame.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5)
        
        self.original_label = ttk.Label(original_frame, text="Aucune image chargée", anchor=tk.CENTER)
        self.original_label.pack(expand=True, fill=tk.BOTH)
        
        # === IMAGE TRAITÉE (Droite) ===
        processed_frame = ttk.LabelFrame(main_frame, text="Aperçu avec Filtres", padding="10")
        processed_frame.grid(row=1, column=2, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(5, 0))
        
        self.processed_label = ttk.Label(processed_frame, text="Appliquez des filtres", anchor=tk.CENTER)
        self.processed_label.pack(expand=True, fill=tk.BOTH)
        
    def create_filter_with_slider(self, parent, label_text, filter_name, from_, to, default, unit):
        """Crée un filtre avec checkbox et slider ajustable"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        # Checkbox
        var = tk.BooleanVar()
        self.filter_vars[filter_name] = var
        chk = ttk.Checkbutton(frame, text=label_text, variable=var, 
                              command=lambda: self.toggle_slider(filter_name))
        chk.pack(anchor=tk.W)
        
        # Slider
        slider_frame = ttk.Frame(frame)
        slider_frame.pack(fill=tk.X, padx=(20, 0))
        
        param_var = tk.DoubleVar(value=default)
        self.param_vars[filter_name] = param_var
        
        slider = ttk.Scale(slider_frame, from_=from_, to=to, variable=param_var, 
                          orient=tk.HORIZONTAL, state=tk.DISABLED)
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Label de valeur
        value_label = ttk.Label(slider_frame, text=f"{default}{unit}", width=10)
        value_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Mise à jour de la valeur affichée
        def update_label(*args):
            val = param_var.get()
            if filter_name in ["threshold", "posterization"]:
                val = int(val)
            value_label.config(text=f"{val}{unit}")
        
        param_var.trace_add("write", update_label)
        
        # Stocker le slider pour l'activer/désactiver
        slider.filter_name = filter_name
        if not hasattr(self, 'sliders'):
            self.sliders = {}
        self.sliders[filter_name] = slider
        
    def toggle_slider(self, filter_name):
        """Active/désactive le slider selon le checkbox"""
        if filter_name in self.sliders:
            state = tk.NORMAL if self.filter_vars[filter_name].get() else tk.DISABLED
            self.sliders[filter_name].config(state=state)
    
    def load_image(self):
        """Charge une image depuis le disque"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner une image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.gif"), ("Tous les fichiers", "*.*")]
        )
        
        if file_path:
            try:
                self.current_image_path = file_path
                self.original_image = Image.open(file_path)
                self.processor = ImageProcessor(file_path)
                self.display_image(self.original_image, self.original_label)
                self.processed_label.config(text="Appliquez des filtres", image='')
                messagebox.showinfo("Succès", "Image chargée avec succès!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger l'image:\n{e}")
    
    def apply_filters(self):
        """Applique tous les filtres sélectionnés en séquence"""
        if not self.processor or not self.original_image:
            messagebox.showwarning("Attention", "Veuillez d'abord charger une image.")
            return
        
        # Réinitialiser avec l'image originale
        self.processor = ImageProcessor(self.current_image_path)
        result = self.original_image.copy()
        
        applied_filters = []
        
        try:
            # Appliquer les filtres dans l'ordre
            for filter_name, var in self.filter_vars.items():
                if var.get():  # Si le filtre est coché
                    if filter_name == "negative":
                        result = self.processor.negative()
                    elif filter_name == "bw":
                        result = self.processor.black_and_white()
                    elif filter_name == "sepia":
                        result = self.processor.sepia()
                    elif filter_name == "mirror_v":
                        result = self.processor.mirror_vertical()
                    elif filter_name == "mirror_h":
                        result = self.processor.mirror_horizontal()
                    elif filter_name == "clipping":
                        result = self.processor.selective_clipping()
                    elif filter_name == "contrast":
                        param = self.param_vars[filter_name].get()
                        result = self.processor.contrast(param)
                    elif filter_name == "threshold":
                        param = int(self.param_vars[filter_name].get())
                        result = self.processor.threshold(param)
                    elif filter_name == "desaturation":
                        param = self.param_vars[filter_name].get()
                        result = self.processor.desaturation(param)
                    elif filter_name == "posterization":
                        param = int(self.param_vars[filter_name].get())
                        result = self.processor.posterization(param)
                    
                    # Mettre à jour le processeur avec le résultat
                    self.processor.pixels = np.array(result, dtype=np.float64)
                    applied_filters.append(filter_name)
            
            if applied_filters:
                self.processed_image = result
                self.display_image(result, self.processed_label)
                messagebox.showinfo("Succès", f"{len(applied_filters)} filtre(s) appliqué(s)!")
            else:
                messagebox.showinfo("Information", "Aucun filtre sélectionné.")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'application des filtres:\n{e}")
    
    def save_image(self):
        """Sauvegarde l'image traitée"""
        if not self.processed_image:
            messagebox.showwarning("Attention", "Aucune image traitée à sauvegarder.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Tous les fichiers", "*.*")]
        )
        
        if file_path:
            try:
                self.processed_image.save(file_path)
                messagebox.showinfo("Succès", f"Image sauvegardée dans:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de sauvegarder:\n{e}")
    
    def reset_image(self):
        """Réinitialise l'image traitée"""
        if self.original_image:
            self.processed_label.config(text="Appliquez des filtres", image='')
            self.processed_image = None
            # Décocher tous les filtres
            for var in self.filter_vars.values():
                var.set(False)
            # Désactiver tous les sliders
            if hasattr(self, 'sliders'):
                for slider in self.sliders.values():
                    slider.config(state=tk.DISABLED)
            messagebox.showinfo("Réinitialisé", "Image réinitialisée.")
    
    def display_image(self, image, label):
        """Affiche une image dans un label avec redimensionnement"""
        # Redimensionner pour l'affichage
        display_size = (400, 400)
        image.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo, text='')
        label.image = photo  # Garder une référence


def main():
    root = tk.Tk()
    app = ImageProcessingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
