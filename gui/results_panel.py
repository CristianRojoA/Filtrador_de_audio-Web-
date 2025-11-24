"""
📊 PANEL DE RESULTADOS
=======================
Panel derecho con visualización de resultados
"""

import tkinter as tk
from tkinter import scrolledtext
from .styles import COLORS, FONTS

class ResultsPanel:
    """Panel para mostrar resultados del análisis"""
    
    def __init__(self, parent):
        self.parent = parent
        self._initialized = False
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets del panel"""
        if self._initialized:
            return
        
        inner = tk.Frame(self.parent, bg='white')
        inner.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(
            inner,
            text="📊 Resultados del Análisis",
            font=FONTS['heading'],
            bg='white',
            fg=COLORS['dark']
        ).pack(anchor='w', pady=(0, 15))
        
        # Área de texto con scroll
        self.results_text = scrolledtext.ScrolledText(
            inner,
            font=FONTS['console'],
            bg=COLORS['dark'],
            fg=COLORS['light'],
            relief='solid',
            bd=1,
            padx=15,
            pady=15,
            wrap='word'
        )
        self.results_text.pack(fill='both', expand=True)
        
        self._initialized = True
        
        # Mensaje de bienvenida (solo una vez)
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """Mostrar mensaje de bienvenida"""
        welcome = (
            "🎯 Bienvenido al Clasificador de Audio\n"
            "==================================================\n\n"
            "Pasos para usar:\n\n"
            "1️⃣ Selecciona un archivo de audio\n"
            "2️⃣ Elige el tipo de análisis:\n"
            "   • Predicción Simple: Identifica qué es el audio completo\n"
            "   • Análisis Temporal: Detecta cuándo ocurre cada evento\n\n"
            "3️⃣ Espera los resultados\n"
            "4️⃣ Opcionalmente exporta a JSON\n\n"
            "💡 El análisis temporal es más detallado pero tarda más.\n\n"
            "⏰ Análisis Temporal te muestra:\n"
            "   • En qué momento (MM:SS) empieza cada sonido\n"
            "   • Cuánto dura cada evento\n"
            "   • La confianza de cada detección\n"
        )
        try:
            self.results_text.delete('1.0', 'end')
            self.results_text.insert('1.0', welcome)
        except:
            pass
    
    def clear(self):
        """Limpiar el área de resultados"""
        self.results_text.delete('1.0', 'end')
    
    def append(self, text):
        """Agregar texto al área de resultados"""
        self.results_text.insert('end', text)
        self.results_text.see('end')
    
    def set_text(self, text):
        """Reemplazar todo el texto"""
        self.clear()
        self.append(text)
