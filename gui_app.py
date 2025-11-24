"""
🎨 PUNTO DE ENTRADA PRINCIPAL DE LA GUI
========================================
Inicializa y ejecuta la interfaz gráfica modular
"""

import tkinter as tk
from gui.start_window import StartWindow
from gui.main_window import AudioClassifierGUI
from gui.training_window import TrainingWindow
from gui.separator_window import SeparatorWindow
from entrenador_personalizado import EntrenadorPersonalizado

def main():
    """Iniciar la aplicación GUI"""
    from gui.window_config import WindowConfig
    from gui.fft_window import FFTVisualizationWindow
    from gui.import_window import ImportWindow
    
    root = tk.Tk()
    root.title("🎵 Clasificador de Audio")
    
    # Configurar icono de la aplicación
    try:
        root.iconbitmap('app_icon.ico')
    except:
        pass  # Si no encuentra el icono, continuar sin él
    
    # Cargar configuración guardada
    config = WindowConfig.get_window_config("start")
    root.geometry(f"{config['width']}x{config['height']}")
    if config.get('maximized', False):
        root.state('zoomed')
    
    root.configure(bg='#f0f0f0')
    
    def open_training():
        """Abrir ventana de entrenamiento"""
        root.destroy()
        train_root = tk.Tk()
        try:
            train_root.iconbitmap('app_icon.ico')
        except:
            pass
        TrainingWindow(train_root, EntrenadorPersonalizado)
        train_root.mainloop()
    
    def open_identify():
        """Abrir ventana de identificación"""
        root.destroy()
        identify_root = tk.Tk()
        try:
            identify_root.iconbitmap('app_icon.ico')
        except:
            pass
        AudioClassifierGUI(identify_root, EntrenadorPersonalizado)
        identify_root.mainloop()
    
    def open_fft():
        """Abrir ventana de análisis FFT"""
        root.destroy()
        fft_root = tk.Tk()
        try:
            fft_root.iconbitmap('app_icon.ico')
        except:
            pass
        FFTVisualizationWindow(fft_root)
        fft_root.mainloop()
    
    def open_separator():
        """Abrir ventana de separación de audio"""
        root.destroy()
        separator_root = tk.Tk()
        try:
            separator_root.iconbitmap('app_icon.ico')
        except:
            pass
        SeparatorWindow(separator_root, EntrenadorPersonalizado)
        separator_root.mainloop()
    
    def open_import():
        """Abrir ventana de importación"""
        root.destroy()
        import_root = tk.Tk()
        try:
            import_root.iconbitmap('app_icon.ico')
        except:
            pass
        ImportWindow(import_root)
        import_root.mainloop()
    
    # Mostrar ventana de inicio
    StartWindow(root, on_train=open_training, on_identify=open_identify, 
                on_fft=open_fft, on_separator=open_separator, on_import=open_import)
    root.mainloop()

if __name__ == "__main__":
    main()
