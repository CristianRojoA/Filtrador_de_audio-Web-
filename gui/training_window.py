"""
🧠 VENTANA DE ENTRENAMIENTO
============================
Interfaz para entrenar nuevos modelos
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
from io import StringIO
from .styles import COLORS, FONTS
from .window_config import WindowConfig

class TrainingWindow:
    """Ventana para entrenar modelos"""
    
    def __init__(self, root, entrenador_class):
        self.root = root
        self.entrenador_class = entrenador_class
        self.entrenador = None
        self.window_type = "training"
        
        self.setup_window()
        self.create_widgets()
        
        # Configurar eventos de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind('<Configure>', self.on_configure)
        
        # Inicializar entrenador
        self.root.after(100, self.init_entrenador)
    
    def setup_window(self):
        """Configurar ventana"""
        self.root.title("🧠 Entrenar Modelo - Clasificador de Audio")
        
        # Cargar configuración guardada
        config = WindowConfig.get_window_config(self.window_type)
        
        # Establecer tamaño mínimo
        self.root.minsize(800, 600)
        
        # Aplicar tamaño guardado
        width = max(config['width'], 800)
        height = max(config['height'], 600)
        self.root.geometry(f"{width}x{height}")
        
        # Aplicar estado maximizado si corresponde
        if config.get('maximized', False):
            self.root.state('zoomed')
        
        self.root.configure(bg=COLORS['bg'])
        
        # Hacer ventana responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def create_widgets(self):
        """Crear interfaz"""
        # Header
        header = tk.Frame(self.root, bg=COLORS['primary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🧠 Entrenamiento de Modelo",
            font=FONTS['title'],
            bg=COLORS['primary'],
            fg='white'
        ).pack(pady=25)
        
        # Contenedor principal
        main = tk.Frame(self.root, bg=COLORS['bg'])
        main.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Panel de acciones
        actions_panel = tk.Frame(main, bg='white', relief='solid', bd=1)
        actions_panel.pack(fill='x', pady=(0, 10))
        
        self.create_actions_panel(actions_panel)
        
        # Panel de log
        log_panel = tk.Frame(main, bg='white', relief='solid', bd=1)
        log_panel.pack(fill='both', expand=True)
        
        self.create_log_panel(log_panel)
        
        # Botón volver
        btn_back = tk.Button(
            main,
            text="⬅️ Volver al Menú",
            font=FONTS['button'],
            bg=COLORS['gray'],
            fg='white',
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.go_back
        )
        btn_back.pack(pady=(10, 0))
        
        # Barra de estado
        self.status_bar = tk.Label(
            self.root,
            text="⚪ Esperando...",
            bg='#e5e7eb',
            fg=COLORS['dark'],
            font=FONTS['status'],
            anchor='w',
            padx=10
        )
        self.status_bar.pack(side='bottom', fill='x')
    
    def create_actions_panel(self, parent):
        """Crear panel de acciones"""
        inner = tk.Frame(parent, bg='white')
        inner.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            inner,
            text="🎯 Acciones de Entrenamiento",
            font=FONTS['heading'],
            bg='white',
            fg=COLORS['dark']
        ).pack(anchor='w', pady=(0, 15))
        
        # Grid de botones
        btn_frame = tk.Frame(inner, bg='white')
        btn_frame.pack(fill='x')
        
        # Fila 1
        row1 = tk.Frame(btn_frame, bg='white')
        row1.pack(fill='x', pady=(0, 10))
        
        self.btn_add_data = tk.Button(
            row1,
            text="📁 Agregar Datos",
            font=FONTS['button'],
            bg=COLORS['primary'],
            fg='white',
            relief='flat',
            padx=15,
            pady=10,
            cursor='hand2',
            command=self.add_data
        )
        self.btn_add_data.pack(side='left', padx=(0, 10))
        
        self.btn_verify = tk.Button(
            row1,
            text="🔍 Verificar Datos",
            font=FONTS['button'],
            bg=COLORS['gray'],
            fg='white',
            relief='flat',
            padx=15,
            pady=10,
            cursor='hand2',
            command=self.verify_data
        )
        self.btn_verify.pack(side='left', padx=(0, 10))
        
        # Fila 2
        row2 = tk.Frame(btn_frame, bg='white')
        row2.pack(fill='x')
        
        self.btn_train = tk.Button(
            row2,
            text="🚀 Entrenar Modelo",
            font=FONTS['button'],
            bg=COLORS['success'],
            fg='white',
            relief='flat',
            padx=15,
            pady=10,
            cursor='hand2',
            command=self.train_model
        )
        self.btn_train.pack(side='left', padx=(0, 10))
        
        self.btn_models = tk.Button(
            row2,
            text="📊 Ver Modelos",
            font=FONTS['button'],
            bg=COLORS['warning'],
            fg='white',
            relief='flat',
            padx=15,
            pady=10,
            cursor='hand2',
            command=self.show_models
        )
        self.btn_models.pack(side='left')
        
        # Barra de progreso
        self.progress = ttk.Progressbar(inner, mode='indeterminate')
    
    def create_log_panel(self, parent):
        """Crear panel de log"""
        inner = tk.Frame(parent, bg='white')
        inner.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(
            inner,
            text="📋 Log de Entrenamiento",
            font=FONTS['heading'],
            bg='white',
            fg=COLORS['dark']
        ).pack(anchor='w', pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(
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
        self.log_text.pack(fill='both', expand=True)
        
        self.log("Sistema de entrenamiento iniciado.\n\n")
        self.log("📋 Pasos para entrenar:\n")
        self.log("="*50 + "\n")
        self.log("1. Click en 'Agregar Datos' para abrir la carpeta\n")
        self.log("2. Arrastra tus archivos de audio en cada categoría\n")
        self.log("3. Verifica que tienes suficientes datos (mínimo 10 por categoría)\n")
        self.log("4. Click en 'Entrenar Modelo'\n")
        self.log("="*50 + "\n\n")
    
    def init_entrenador(self):
        """Inicializar entrenador"""
        self.log("Inicializando sistema...\n")
        
        def init():
            try:
                self.entrenador = self.entrenador_class()
                self.root.after(0, lambda: self.log("✅ Sistema listo\n\n"))
                self.root.after(0, lambda: self.update_status("✅ Listo", COLORS['success']))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"❌ Error: {str(e)}\n"))
                self.root.after(0, lambda: self.update_status("❌ Error", COLORS['danger']))
        
        thread = threading.Thread(target=init, daemon=True)
        thread.start()
    
    def add_data(self):
        """Abrir carpeta de datos y crear estructura si no existe"""
        import os
        import subprocess
        
        if not self.entrenador:
            messagebox.showwarning("Advertencia", "Sistema no iniciado")
            return
        
        try:
            data_dir = os.path.abspath(self.entrenador.data_dir)
            
            # Crear estructura si no existe
            if not os.path.exists(data_dir) or not os.listdir(data_dir):
                self.log("📁 Creando estructura de carpetas...\n")
                categorias = self.entrenador.crear_estructura_datos()
                self.log(f"✅ Estructura creada: {len(categorias)} categorías\n")
                for cat in categorias:
                    self.log(f"   📁 {cat}\n")
                self.log("\n")
            
            # Abrir carpeta en el explorador de Windows
            self.log(f"📂 Abriendo carpeta: {data_dir}\n\n")
            self.log("💡 Instrucciones:\n")
            self.log("   1. Verás las carpetas por categoría\n")
            self.log("   2. Arrastra tus archivos de audio a cada carpeta\n")
            self.log("   3. Usa mínimo 10 archivos por categoría\n")
            self.log("   4. Formatos soportados: WAV, MP3, FLAC, OGG\n\n")
            
            # Abrir explorador de Windows
            subprocess.Popen(f'explorer "{data_dir}"')
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}\n")
            messagebox.showerror("Error", str(e))
    
    def verify_data(self):
        """Verificar datos disponibles"""
        if not self.entrenador:
            messagebox.showwarning("Advertencia", "Sistema no iniciado")
            return
        
        try:
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            self.entrenador.verificar_datos()
            
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            self.log(output + "\n")
        except Exception as e:
            self.log(f"❌ Error: {str(e)}\n")
    
    def train_model(self):
        """Entrenar modelo"""
        if not self.entrenador:
            messagebox.showwarning("Advertencia", "Sistema no iniciado")
            return
        
        self.disable_buttons()
        self.update_status("🚀 Entrenando modelo...", COLORS['warning'])
        self.progress.pack(fill='x', pady=(10, 0))
        self.progress.start(10)
        
        self.log("\n" + "="*50 + "\n")
        self.log("🚀 INICIANDO ENTRENAMIENTO\n")
        self.log("="*50 + "\n\n")
        
        def train():
            try:
                old_stdout = sys.stdout
                sys.stdout = StringIO()
                
                success = self.entrenador.entrenar_modelo()
                
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                self.root.after(0, lambda: self.log(output + "\n"))
                
                if success:
                    self.root.after(0, lambda: self.log("\n✅ ¡ENTRENAMIENTO COMPLETADO!\n\n"))
                    self.root.after(0, lambda: self.update_status("✅ Modelo entrenado", COLORS['success']))
                    self.root.after(0, lambda: messagebox.showinfo("Éxito", "Modelo entrenado exitosamente"))
                else:
                    self.root.after(0, lambda: self.log("\n❌ Entrenamiento fallido\n\n"))
                    self.root.after(0, lambda: self.update_status("❌ Falló", COLORS['danger']))
                
                self.root.after(0, self.training_finished)
                
            except Exception as e:
                self.root.after(0, lambda: self.log(f"\n❌ Error: {str(e)}\n\n"))
                self.root.after(0, lambda: self.update_status("❌ Error", COLORS['danger']))
                self.root.after(0, self.training_finished)
        
        thread = threading.Thread(target=train, daemon=True)
        thread.start()
    
    def show_models(self):
        """Mostrar modelos guardados"""
        import os
        from datetime import datetime
        
        modelo_dir = "modelo_personalizado"
        if os.path.exists(modelo_dir):
            modelos = sorted([f for f in os.listdir(modelo_dir) if f.startswith('clasificador_')])
            
            if modelos:
                self.log(f"\n📊 Modelos guardados ({len(modelos)}):\n")
                for i, modelo in enumerate(modelos, 1):
                    timestamp = modelo.replace('clasificador_', '').replace('.pkl', '')
                    try:
                        fecha = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                        self.log(f"   [{i}] {modelo}\n")
                        self.log(f"       Creado: {fecha.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    except:
                        self.log(f"   [{i}] {modelo}\n")
                self.log("\n")
            else:
                self.log("\n📭 No hay modelos guardados\n\n")
        else:
            self.log("\n📭 Directorio de modelos no existe\n\n")
    
    def training_finished(self):
        """Callback cuando termina el entrenamiento"""
        self.progress.stop()
        self.progress.pack_forget()
        self.enable_buttons()
    
    def disable_buttons(self):
        """Deshabilitar botones"""
        self.btn_add_data.config(state='disabled')
        self.btn_verify.config(state='disabled')
        self.btn_train.config(state='disabled')
        self.btn_models.config(state='disabled')
    
    def enable_buttons(self):
        """Habilitar botones"""
        self.btn_add_data.config(state='normal')
        self.btn_verify.config(state='normal')
        self.btn_train.config(state='normal')
        self.btn_models.config(state='normal')
    
    def log(self, message):
        """Agregar al log"""
        self.log_text.insert('end', message)
        self.log_text.see('end')
    
    def update_status(self, message, color):
        """Actualizar barra de estado"""
        self.status_bar.config(text=message, fg=color)
    
    def on_configure(self, event):
        """Guardar configuración cuando cambia el tamaño"""
        # Solo guardar si es el evento de la ventana principal
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
                # Si está maximizada, guardar el tamaño antes de maximizar
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
    
    def go_back(self):
        """Volver al menú principal"""
        if messagebox.askyesno("Confirmar", "¿Volver al menú principal?"):
            self.save_window_state()
            self.root.destroy()
            import tkinter as tk
            from .start_window import StartWindow
            from entrenador_personalizado import EntrenadorPersonalizado
            
            root = tk.Tk()
            root.title("🎵 Clasificador de Audio")
            
            # Aplicar config guardada
            config = WindowConfig.get_window_config("start")
            root.geometry(f"{config['width']}x{config['height']}")
            if config.get('maximized', False):
                root.state('zoomed')
            
            root.configure(bg='#f0f0f0')
            
            def open_training():
                root.destroy()
                train_root = tk.Tk()
                TrainingWindow(train_root, EntrenadorPersonalizado)
                train_root.mainloop()
            
            def open_identify():
                root.destroy()
                identify_root = tk.Tk()
                from .main_window import AudioClassifierGUI
                AudioClassifierGUI(identify_root, self.entrenador_class)
                identify_root.mainloop()
            
            def open_fft():
                root.destroy()
                from .fft_window import FFTVisualizationWindow
                fft_root = tk.Tk()
                FFTVisualizationWindow(fft_root)
                fft_root.mainloop()
            
            def open_separator():
                root.destroy()
                from .separator_window import SeparatorWindow
                sep_root = tk.Tk()
                SeparatorWindow(sep_root, self.entrenador_class)
                sep_root.mainloop()
            
            def open_import():
                root.destroy()
                from .import_window import ImportWindow
                import_root = tk.Tk()
                ImportWindow(import_root)
                import_root.mainloop()
            
            StartWindow(root, on_train=open_training, on_identify=open_identify, on_fft=open_fft, on_separator=open_separator, on_import=open_import)
            root.mainloop()
