"""
💾 GESTOR DE CONFIGURACIÓN DE VENTANA
======================================
Guarda y carga el tamaño y posición de las ventanas
"""

import json
import os

class WindowConfig:
    """Gestor de configuración de ventanas"""
    
    CONFIG_FILE = "window_config.json"
    
    DEFAULT_CONFIG = {
        "start": {"width": 800, "height": 600, "maximized": False},
        "training": {"width": 1000, "height": 750, "maximized": False},
        "identify": {"width": 1100, "height": 750, "maximized": False}
    }
    
    @staticmethod
    def load_config():
        """Cargar configuración desde archivo"""
        if os.path.exists(WindowConfig.CONFIG_FILE):
            try:
                with open(WindowConfig.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return WindowConfig.DEFAULT_CONFIG.copy()
    
    @staticmethod
    def save_config(config):
        """Guardar configuración a archivo"""
        try:
            with open(WindowConfig.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass
    
    @staticmethod
    def get_window_config(window_type):
        """Obtener configuración de una ventana específica"""
        config = WindowConfig.load_config()
        return config.get(window_type, WindowConfig.DEFAULT_CONFIG[window_type])
    
    @staticmethod
    def save_window_config(window_type, width, height, maximized):
        """Guardar configuración de una ventana"""
        config = WindowConfig.load_config()
        config[window_type] = {
            "width": width,
            "height": height,
            "maximized": maximized
        }
        WindowConfig.save_config(config)
