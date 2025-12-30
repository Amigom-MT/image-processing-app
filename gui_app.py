#!/usr/bin/env python3
"""
Interface graphique moderne pour le traitement d'images
Aperçu dynamique en temps réel avec sliders ajustables
"""

import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import numpy as np
from image_processing import ImageProcessor
import os


class ModernImageProcessingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing Studio")
        self.root.geometry("1400x800")
        self.root.configure(bg='#1e1e1e')
        
        # Style moderne
        self.setup_modern_style()
        
        self.original_image = None
        self.processed_image = None
        self.current_image_path = None
        self.processor = None
        
        # Variables pour les filtres
        self.filter_vars = {}
        self.param_vars = {}
        
        # Timer pour l'aperçu dynamique
        self.update_timer = None
        
        self.create_widgets()
        
    def setup_modern_style(self):
        """Configure un style moderne pour l'interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Couleurs modernes
        bg_dark = '#1e1e1e'
        bg_medium = '#2d2d2d'
        bg_light = '#3d3d3d'
        accent = '#007acc'
        text_color = '#ffffff'
        
        style.configure('Modern.TFrame', background=bg_dark)
        style.configure('Modern.TLabel', background=bg_dark, foreground=text_color, font=('Segoe UI', 10))
        style.configure('Modern.TLabelframe', background=bg_dark, foreground=text_color)
        style.configure('Modern.TLabelframe.Label', background=bg_dark, foreground=text_color, font=('Segoe UI', 11, 'bold'))
        style.configure('Modern.TCheckbutton', background=bg_dark, foreground=text_color)
        style.configure('Modern.TButton', background=accent, foreground=text_color, borderwidth=0, font=('Segoe UI', 10))
        style.map('Modern.TButton', background=[('active', '#005a9e')])
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="15", style='Modern.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # === BARRE DE TITRE ET BOUTONS ===
        header_frame = tk.Frame(main_frame, bg='#007acc', height=60)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.grid_propagate(False)
        
        title_label = tk.Label(header_frame, text="🎨 Image Processing Studio", 
                               bg='#007acc', fg='white', font=('Segoe UI', 16, 'bold'))
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Boutons modernes
        btn_container = tk.Frame(header_frame, bg='#007acc')
        btn_container.pack(side=tk.RIGHT, padx=20)
        
        buttons_config = [
            ("📁 Charger", self.load_image, '#4CAF50'),
            ("💾 Sauvegarder", self.save_image, '#2196F3'),
            ("🔄 Réinitialiser", self.reset_image, '#FF9800')
        ]
        
        for text, command, color in buttons_config:
            btn = tk.Button(btn_container, text=text, command=command,
                           bg=color, fg='white', font=('Segoe UI', 10, 'bold'),
                           relief=tk.FLAT, padx=15, pady=8, cursor='hand2')
            btn.pack(side=tk.LEFT, padx=5)
            # Effet hover
            btn.bind('<Enter>', lambda e, b=btn, c=color: b.config(bg=self.darken_color(c)))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.config(bg=c))
        
        # === PANEL DE FILTRES (Gauche) ===
        filters_frame = ttk.LabelFrame(main_frame, text=" 🎛️ Filtres & Réglages ", 
                                      padding="15", style='Modern.TLabelframe')
        filters_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.W), padx=(0, 15))
        
        # Canvas avec scrollbar
        canvas = tk.Canvas(filters_frame, width=280, bg='#2d2d2d', highlightthickness=0)
        scrollbar = ttk.Scrollbar(filters_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2d2d2d')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Filtres simples
        simple_filters = [
            ("🔄 Négatif", "negative"),
            ("⚫ Noir & Blanc", "bw"),
            ("🟤 Sépia", "sepia"),
            ("⬆️ Miroir Vertical", "mirror_v"),
            ("↔️ Miroir Horizontal", "mirror_h"),
            ("✂️ Clipping Sélectif", "clipping")
        ]
        
        title_simple = tk.Label(scrollable_frame, text="Filtres Simples", 
                               font=('Segoe UI', 11, 'bold'), bg='#2d2d2d', fg='#007acc')
        title_simple.pack(anchor=tk.W, pady=(5, 10))
        
        for label, filter_name in simple_filters:
            var = tk.BooleanVar()
            self.filter_vars[filter_name] = var
            chk = tk.Checkbutton(scrollable_frame, text=label, variable=var,
                                bg='#2d2d2d', fg='white', selectcolor='#1e1e1e',
                                activebackground='#3d3d3d', activeforeground='white',
                                command=self.schedule_update, font=('Segoe UI', 10))
            chk.pack(anchor=tk.W, pady=3, padx=5)
        
        ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Filtres avec sliders
        title_adjustable = tk.Label(scrollable_frame, text="Filtres Ajustables", 
                                    font=('Segoe UI', 11, 'bold'), bg='#2d2d2d', fg='#007acc')
        title_adjustable.pack(anchor=tk.W, pady=(0, 10))
        
        self.create_filter_with_slider(scrollable_frame, "🔆 Contraste", "contrast", 0.1, 3.0, 1.5, "x")
        self.create_filter_with_slider(scrollable_frame, "🎯 Seuillage", "threshold", 0, 255, 128, "")
        self.create_filter_with_slider(scrollable_frame, "🎨 Désaturation", "desaturation", 0.0, 1.0, 0.5, "")
        self.create_filter_with_slider(scrollable_frame, "🖼️ Postérisation", "posterization", 2, 16, 4, " niveaux")
        
        # === IMAGE ORIGINALE (Centre) ===
        original_frame = self.create_image_panel(main_frame, "📷 Image Originale", 1, 1)
        self.original_label = tk.Label(original_frame, text="Chargez une image pour commencer",
                                      bg='#2d2d2d', fg='#888888', font=('Segoe UI', 12))
        self.original_label.pack(expand=True, fill=tk.BOTH)
        
        # === IMAGE TRAITÉE (Droite) ===
        processed_frame = self.create_image_panel(main_frame, "✨ Aperçu avec Filtres", 1, 2)
        self.processed_label = tk.Label(processed_frame, text="L'aperçu apparaîtra ici",
                                       bg='#2d2d2d', fg='#888888', font=('Segoe UI', 12))
        self.processed_label.pack(expand=True, fill=tk.BOTH)
        
        # === BARRE DE STATUT ===
        self.status_bar = tk.Label(main_frame, text="Prêt  ✓", bg='#007acc', fg='white',
                                  font=('Segoe UI', 9), anchor=tk.W, padx=15, height=2)
        self.status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 0))
        
    def create_image_panel(self, parent, title, row, col):
        """Crée un panneau d'image stylisé"""
        frame = ttk.LabelFrame(parent, text=f" {title} ", padding="15", style='Modern.TLabelframe')
        frame.grid(row=row, column=col, sticky=(tk.N, tk.S, tk.E, tk.W), padx=7)
        
        inner_frame = tk.Frame(frame, bg='#2d2d2d', relief=tk.SUNKEN, bd=2)
        inner_frame.pack(expand=True, fill=tk.BOTH)
        
        return inner_frame
    
    def create_filter_with_slider(self, parent, label_text, filter_name, from_, to, default, unit):
        """Crée un filtre avec checkbox et slider ajustable"""
        container = tk.Frame(parent, bg='#2d2d2d')
        container.pack(fill=tk.X, pady=8, padx=5)
        
        # Checkbox
        var = tk.BooleanVar()
        self.filter_vars[filter_name] = var
        chk = tk.Checkbutton(container, text=label_text, variable=var,
                            bg='#2d2d2d', fg='white', selectcolor='#1e1e1e',
                            activebackground='#3d3d3d', activeforeground='white',
                            command=lambda: self.toggle_slider(filter_name), font=('Segoe UI', 10))
        chk.pack(anchor=tk.W)
        
        # Slider frame
        slider_frame = tk.Frame(container, bg='#2d2d2d')
        slider_frame.pack(fill=tk.X, padx=(25, 0), pady=(5, 0))
        
        param_var = tk.DoubleVar(value=default)
        self.param_vars[filter_name] = param_var
        
        slider = tk.Scale(slider_frame, from_=from_, to=to, variable=param_var,
                         orient=tk.HORIZONTAL, bg='#3d3d3d', fg='white',
                         highlightthickness=0, troughcolor='#1e1e1e',
                         activebackground='#007acc', state=tk.DISABLED,
                         command=lambda val: self.on_slider_change(filter_name, val, unit, value_label))
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Label de valeur
        value_label = tk.Label(slider_frame, text=f"{default}{unit}",
                              bg='#2d2d2d', fg='#007acc', font=('Segoe UI', 9, 'bold'), width=12)
        value_label.pack(side=tk.RIGHT, padx=(8, 0))
        
        if not hasattr(self, 'sliders'):
            self.sliders = {}
        self.sliders[filter_name] = slider
        
    def on_slider_change(self, filter_name, val, unit, label):
        """Met à jour la valeur affichée et déclenche l'aperçu"""
        val_num = float(val)
        if filter_name in ["threshold", "posterization"]:
            val_num = int(val_num)
        label.config(text=f"{val_num}{unit}")
        self.schedule_update()
    
    def toggle_slider(self, filter_name):
        """Active/désactive le slider"""
        if filter_name in self.sliders:
            state = tk.NORMAL if self.filter_vars[filter_name].get() else tk.DISABLED
            self.sliders[filter_name].config(state=state)
        self.schedule_update()
    
    def schedule_update(self):
        """Programme une mise à jour de l'aperçu (évite les calculs trop fréquents)"""
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
        self.update_timer = self.root.after(300, self.apply_filters_preview)
    
    def load_image(self):
        """Charge une image"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner une image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.gif"), ("Tous", "*.*")]
        )
        
        if file_path:
            try:
                self.current_image_path = file_path
                self.original_image = Image.open(file_path)
                self.processor = ImageProcessor(file_path)
                self.display_image(self.original_image, self.original_label)
                self.processed_label.config(text="Appliquez des filtres", image='')
                self.update_status(f"Image  chargée : {os.path.basename(file_path)}", "success")
            except Exception as e:
                self.update_status(f"❌ Erreur : {str(e)}", "error")
    
    def apply_filters_preview(self):
        """Applique les filtres sélectionnés en temps réel (preview dynamique)"""
        if not self.processor or not self.original_image:
            return
        
        # Réinitialiser avec l'image originale
        self.processor = ImageProcessor(self.current_image_path)
        result = self.original_image.copy()
        
        applied_count = 0
        
        try:
            # Appliquer les filtres dans l'ordre
            for filter_name, var in self.filter_vars.items():
                if var.get():
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
                    
                    # Mettre à jour le processeur
                    self.processor.pixels = np.array(result, dtype=np.float64)
                    applied_count += 1
            
            if applied_count > 0:
                self.processed_image = result
                self.display_image(result, self.processed_label)
                self.update_status(f"✓ {applied_count} filtre(s) appliqué(s)", "success")
            else:
                self.processed_label.config(text="Sélectionnez des filtres", image='')
                self.update_status("Aucun filtre actif", "info")
                
        except Exception as e:
            self.update_status(f"❌ Erreur : {str(e)}", "error")
    
    def save_image(self):
        """Sauvegarde l'image traitée"""
        if not self.processed_image:
            self.update_status("⚠ Aucune image à sauvegarder", "warning")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Tous", "*.*")]
        )
        
        if file_path:
            try:
                self.processed_image.save(file_path)
                self.update_status(f"✓ Sauvegardé : {os.path.basename(file_path)}", "success")
            except Exception as e:
                self.update_status(f"❌ Erreur : {str(e)}", "error")
    
    def reset_image(self):
        """Réinitialise tous les filtres"""
        if self.original_image:
            self.processed_label.config(text="Appliquez des filtres", image='')
            self.processed_image = None
            
            # Décocher tous les filtres
            for var in self.filter_vars.values():
                var.set(False)
            
            # Réinitialiser les valeurs par défaut
            defaults = {
                'contrast': 1.5,
                'threshold': 128,
                'desaturation': 0.5,
                'posterization': 4
            }
            for name, val in defaults.items():
                if name in self.param_vars:
                    self.param_vars[name].set(val)
            
            # Désactiver tous les sliders
            if hasattr(self, 'sliders'):
                for slider in self.sliders.values():
                    slider.config(state=tk.DISABLED)
            
            self.update_status("🔄 Filtres réinitialisés", "info")
    
    def display_image(self, image, label):
        """Affiche une image avec redimensionnement intelligent"""
        display_size = (450, 450)
        img_copy = image.copy()
        img_copy.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(img_copy)
        label.config(image=photo, text='', bg='#2d2d2d')
        label.image = photo
    
    def update_status(self, message, status_type="info"):
        """Met à jour la barre de statut avec des couleurs selon le type"""
        colors = {
            "success": "#4CAF50",
            "error": "#F44336",
            "warning": "#FF9800",
            "info": "#007acc"
        }
        self.status_bar.config(text=f"  {message}", bg=colors.get(status_type, "#007acc"))
    
    def darken_color(self, hex_color):
        """Assombrit une couleur hexadécimale pour l'effet hover"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = int(r * 0.8), int(g * 0.8), int(b * 0.8)
        return f'#{r:02x}{g:02x}{b:02x}'


def main():
    root = tk.Tk()
    app = ModernImageProcessingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

