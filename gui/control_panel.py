"""
🎛️ PANEL DE CONTROLES
=======================
Panel izquierdo con controles de la aplicación
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from .styles import COLORS, FONTS

class ControlPanel:
    """Panel de controles para selección y configuración"""
    
    def __init__(self, parent, on_file_select, on_predict_simple, on_predict_temporal, on_export):
        self.parent = parent
        self.on_file_select = on_file_select
        self.on_predict_simple = on_predict_simple
        self.on_predict_temporal = on_predict_temporal
        self.on_export = on_export
        
        self.archivo_actual = None
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets del panel"""
        inner = tk.Frame(self.parent, bg='white')
        inner.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Sección: Seleccionar archivo
        self._create_file_section(inner)
        
        # Separador
        ttk.Separator(inner, orient='horizontal').pack(fill='x', pady=15)
        
        # Sección: Configuración
        self._create_config_section(inner)
        
        # Separador
        ttk.Separator(inner, orient='horizontal').pack(fill='x', pady=15)
        
        # Sección: Acciones
        self._create_actions_section(inner)
    
    def _create_file_section(self, parent):
        """Crear sección de selección de archivo"""
        tk.Label(
            parent,
            text="📂 Seleccionar Audio",
            font=FONTS['heading'],
            bg='white',
            fg=COLORS['dark']
        ).pack(anchor='w', pady=(0, 15))
        
        # Botón seleccionar
        self.btn_select = tk.Button(
            parent,
            text="📁 Seleccionar Archivo",
            font=FONTS['button'],
            bg=COLORS['primary'],
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.select_file
        )
        self.btn_select.pack(fill='x', pady=(0, 10))
        
        # Label del archivo
        self.lbl_file = tk.Label(
            parent,
            text="Ningún archivo seleccionado",
            font=FONTS['small'],
            bg='white',
            fg=COLORS['gray'],
            wraplength=280,
            justify='left'
        )
        self.lbl_file.pack(anchor='w', pady=(0, 20))
    
    def _create_config_section(self, parent):
        """Crear sección de configuración"""
        tk.Label(
            parent,
            text="⚙️ Configuración",
            font=FONTS['heading'],
            bg='white',
            fg=COLORS['dark']
        ).pack(anchor='w', pady=(0, 15))
        
        config_frame = tk.Frame(parent, bg='white')
        config_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            config_frame,
            text="Ventana de análisis (segundos):",
            font=FONTS['body'],
            bg='white',
            fg=COLORS['dark']
        ).pack(anchor='w')
        
        self.ventana_var = tk.StringVar(value="2.0")
        ventana_entry = tk.Entry(
            config_frame,
            textvariable=self.ventana_var,
            font=FONTS['body'],
            bg=COLORS['light'],
            relief='solid',
            bd=1,
            width=15
        )
        ventana_entry.pack(anchor='w', pady=(5, 0))
        
        tk.Label(
            config_frame,
            text="💡 Recomendado: 1.0 - 3.0",
            font=FONTS['small'],
            bg='white',
            fg=COLORS['gray']
        ).pack(anchor='w', pady=(3, 0))
    
    def _create_actions_section(self, parent):
        """Crear sección de acciones"""
        tk.Label(
            parent,
            text="🎯 Acciones",
            font=FONTS['heading'],
            bg='white',
            fg=COLORS['dark']
        ).pack(anchor='w', pady=(0, 15))
        
        # Predicción simple
        self.btn_simple = tk.Button(
            parent,
            text="🎵 Predicción Simple",
            font=FONTS['button'],
            bg=COLORS['gray'],
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.on_predict_simple
        )
        self.btn_simple.pack(fill='x', pady=(0, 10))
        
        # Análisis temporal
        self.btn_temporal = tk.Button(
            parent,
            text="⏰ Análisis Temporal",
            font=FONTS['button'],
            bg=COLORS['success'],
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.on_predict_temporal
        )
        self.btn_temporal.pack(fill='x', pady=(0, 10))
        
        # Exportar JSON
        self.btn_export = tk.Button(
            parent,
            text="💾 Exportar JSON",
            font=FONTS['button'],
            bg=COLORS['warning'],
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.on_export,
            state='disabled'
        )
        self.btn_export.pack(fill='x')
    
    def select_file(self):
        """Seleccionar archivo de audio"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de audio",
            filetypes=[
                ("Archivos de audio", "*.wav *.mp3 *.flac *.ogg"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if filename:
            self.archivo_actual = filename
            self.lbl_file.config(
                text=f"📁 {os.path.basename(filename)}",
                fg=COLORS['success']
            )
            self.on_file_select(filename)
    
    def get_ventana(self):
        """Obtener valor de ventana de análisis"""
        try:
            ventana = float(self.ventana_var.get())
            if ventana <= 0:
                return 2.0
            return ventana
        except ValueError:
            return 2.0
    
    def disable_buttons(self):
        """Deshabilitar todos los botones"""
        self.btn_select.config(state='disabled')
        self.btn_simple.config(state='disabled')
        self.btn_temporal.config(state='disabled')
    
    def enable_buttons(self):
        """Habilitar todos los botones"""
        self.btn_select.config(state='normal')
        self.btn_simple.config(state='normal')
        self.btn_temporal.config(state='normal')
    
    def enable_export(self):
        """Habilitar botón de exportar"""
        self.btn_export.config(state='normal')
