"""
🏠 VENTANA DE INICIO
====================
Permite elegir entre entrenar o identificar
"""

import tkinter as tk
from .styles import COLORS, FONTS
from .window_config import WindowConfig

class StartWindow:
    """Ventana inicial para elegir modo"""
    
    def __init__(self, root, on_train, on_identify, on_fft=None, on_separator=None, on_import=None):
        self.root = root
        self.on_train = on_train
        self.on_identify = on_identify
        self.on_fft = on_fft
        self.on_separator = on_separator
        self.on_import = on_import
        self.window_type = "start"
        
        self.setup_window()
        self.create_widgets()
        
        # Configurar eventos
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind('<Configure>', self.on_configure)
    
    def setup_window(self):
        """Configurar ventana"""
        self.root.minsize(700, 500)
        
        # Aplicar tamaño guardado
        config = WindowConfig.get_window_config(self.window_type)
        width = max(config['width'], 700)
        height = max(config['height'], 500)
        self.root.geometry(f"{width}x{height}")
        
        if config.get('maximized', False):
            self.root.state('zoomed')
    
    def create_widgets(self):
        """Crear interfaz de selección"""
        # Frame principal
        main = tk.Frame(self.root, bg=COLORS['bg'])
        main.pack(fill='both', expand=True)
        
        # Header
        header = tk.Frame(main, bg=COLORS['primary'], height=100)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🎵 Clasificador de Audio",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['primary'],
            fg='white'
        ).pack(pady=(20, 5))
        
        tk.Label(
            header,
            text="Sistema de Machine Learning para Audio",
            font=FONTS['body'],
            bg=COLORS['primary'],
            fg='#e0e7ff'
        ).pack()
        
        # Contenedor de opciones
        options_frame = tk.Frame(main, bg=COLORS['bg'])
        options_frame.pack(expand=True, pady=50)
        
        # Título
        tk.Label(
            options_frame,
            text="¿Qué deseas hacer?",
            font=('Segoe UI', 18, 'bold'),
            bg=COLORS['bg'],
            fg=COLORS['dark']
        ).pack(pady=(0, 40))
        
        # Contenedor de botones
        buttons_container = tk.Frame(options_frame, bg=COLORS['bg'])
        buttons_container.pack()
        
        # Opción 1: Entrenar
        train_frame = tk.Frame(buttons_container, bg='white', relief='solid', bd=2, cursor='hand2')
        train_frame.pack(side='left', padx=20)
        train_frame.bind('<Button-1>', lambda e: self.on_train())
        
        train_inner = tk.Frame(train_frame, bg='white')
        train_inner.pack(padx=40, pady=40)
        
        tk.Label(
            train_inner,
            text="🧠",
            font=('Segoe UI', 48),
            bg='white'
        ).pack()
        
        tk.Label(
            train_inner,
            text="Entrenar Modelo",
            font=('Segoe UI', 16, 'bold'),
            bg='white',
            fg=COLORS['primary']
        ).pack(pady=(10, 5))
        
        tk.Label(
            train_inner,
            text="Entrena la IA antes de comenzar a identificar audios",
            font=FONTS['body'],
            bg='white',
            fg=COLORS['gray'],
            justify='center'
        ).pack()
        
        # Hacer clickeable todo el frame
        for widget in train_inner.winfo_children():
            widget.bind('<Button-1>', lambda e: self.on_train())
        
        # Opción 2: Identificar
        identify_frame = tk.Frame(buttons_container, bg='white', relief='solid', bd=2, cursor='hand2')
        identify_frame.pack(side='left', padx=20)
        identify_frame.bind('<Button-1>', lambda e: self.on_identify())
        
        identify_inner = tk.Frame(identify_frame, bg='white')
        identify_inner.pack(padx=40, pady=40)
        
        tk.Label(
            identify_inner,
            text="🎯",
            font=('Segoe UI', 48),
            bg='white'
        ).pack()
        
        tk.Label(
            identify_inner,
            text="Identificar Audio",
            font=('Segoe UI', 16, 'bold'),
            bg='white',
            fg=COLORS['success']
        ).pack(pady=(10, 5))
        
        tk.Label(
            identify_inner,
            text="Analiza audios con\nun modelo entrenado",
            font=FONTS['body'],
            bg='white',
            fg=COLORS['gray'],
            justify='center'
        ).pack()
        
        # Hacer clickeable todo el frame
        for widget in identify_inner.winfo_children():
            widget.bind('<Button-1>', lambda e: self.on_identify())
        
        # Opción 3: Análisis FFT
        if self.on_fft:
            fft_frame = tk.Frame(buttons_container, bg='white', relief='solid', bd=2, cursor='hand2')
            fft_frame.pack(side='left', padx=20)
            fft_frame.bind('<Button-1>', lambda e: self.on_fft())
            
            fft_inner = tk.Frame(fft_frame, bg='white')
            fft_inner.pack(padx=40, pady=40)
            
            tk.Label(
                fft_inner,
                text="📊",
                font=('Segoe UI', 48),
                bg='white'
            ).pack()
            
            tk.Label(
                fft_inner,
                text="Análisis FFT",
                font=('Segoe UI', 16, 'bold'),
                bg='white',
                fg='#9c27b0'
            ).pack(pady=(10, 5))
            
            tk.Label(
                fft_inner,
                text="Visualiza espectro\ny frecuencias",
                font=FONTS['body'],
                bg='white',
                fg=COLORS['gray'],
                justify='center'
            ).pack()
            
            # Hacer clickeable todo el frame
            for widget in fft_inner.winfo_children():
                widget.bind('<Button-1>', lambda e: self.on_fft())
        
        # Nueva fila de opciones
        buttons_container2 = tk.Frame(options_frame, bg=COLORS['bg'])
        buttons_container2.pack(pady=20)
        
        # Opción 4: Separador de Audio
        if self.on_separator:
            separator_frame = tk.Frame(buttons_container2, bg='white', relief='solid', bd=2, cursor='hand2')
            separator_frame.pack(side='left', padx=20)
            separator_frame.bind('<Button-1>', lambda e: self.on_separator())
            
            separator_inner = tk.Frame(separator_frame, bg='white')
            separator_inner.pack(padx=40, pady=40)
            
            tk.Label(
                separator_inner,
                text="🎵",
                font=('Segoe UI', 48),
                bg='white'
            ).pack()
            
            tk.Label(
                separator_inner,
                text="Separar Audio",
                font=('Segoe UI', 16, 'bold'),
                bg='white',
                fg='#16a085'
            ).pack(pady=(10, 5))
            
            tk.Label(
                separator_inner,
                text="Filtra y exporta\ncomponentes",
                font=FONTS['body'],
                bg='white',
                fg=COLORS['gray'],
                justify='center'
            ).pack()
            
            # Hacer clickeable todo el frame
            for widget in separator_inner.winfo_children():
                widget.bind('<Button-1>', lambda e: self.on_separator())
        
        # Opción 5: Importar Análisis
        if self.on_import:
            import_frame = tk.Frame(buttons_container2, bg='white', relief='solid', bd=2, cursor='hand2')
            import_frame.pack(side='left', padx=20)
            import_frame.bind('<Button-1>', lambda e: self.on_import())
            
            import_inner = tk.Frame(import_frame, bg='white')
            import_inner.pack(padx=40, pady=40)
            
            tk.Label(
                import_inner,
                text="📥",
                font=('Segoe UI', 48),
                bg='white'
            ).pack()
            
            tk.Label(
                import_inner,
                text="Importar Datos",
                font=('Segoe UI', 16, 'bold'),
                bg='white',
                fg='#e67e22'
            ).pack(pady=(10, 5))
            
            tk.Label(
                import_inner,
                text="Visualiza análisis\nexportados",
                font=FONTS['body'],
                bg='white',
                fg=COLORS['gray'],
                justify='center'
            ).pack()
            
            # Hacer clickeable todo el frame
            for widget in import_inner.winfo_children():
                widget.bind('<Button-1>', lambda e: self.on_import())
        
        # Footer
        footer = tk.Label(
            main,
            text="💡 Tip: Primero entrena un modelo, luego úsalo para identificar audios",
            font=FONTS['small'],
            bg=COLORS['bg'],
            fg='black'
        )
        footer.pack(side='bottom', pady=20)
    
    def on_configure(self, event):
        """Guardar configuración cuando cambia el tamaño"""
        if event.widget == self.root:
            self.save_window_state()
    
    def save_window_state(self):
        """Guardar estado actual de la ventana"""
        try:
            is_maximized = (self.root.state() == 'zoomed')
            
            if not is_maximized:
                width = self.root.winfo_width()
                height = self.root.winfo_height()
            else:
                config = WindowConfig.get_window_config(self.window_type)
                width = config['width']
                height = config['height']
            
            WindowConfig.save_window_config(self.window_type, width, height, is_maximized)
        except:
            pass
    
    def on_closing(self):
        """Guardar estado antes de cerrar"""
        self.save_window_state()
        self.root.destroy()
