"""
📊 VENTANA DE VISUALIZACIÓN FFT
================================
Interfaz para análisis espectral de audio
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from .styles import COLORS, FONTS
from .window_config import WindowConfig
from fft_analyzer import FFTAnalyzer
import os

class FFTVisualizationWindow:
    """Ventana para visualización de análisis FFT"""
    
    def __init__(self, root):
        self.root = root
        self.window_type = "fft"
        self.analyzer = FFTAnalyzer()
        self.current_audio_path = None
        self.current_audio = None
        self.current_canvas = None
        
        self.setup_window()
        self.create_widgets()
        
        # Configurar eventos
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind('<Configure>', self.on_configure)
    
    def setup_window(self):
        """Configurar ventana"""
        self.root.title("📊 Análisis FFT - Espectro de Frecuencias")
        
        # Cargar o usar configuración por defecto
        try:
            config = WindowConfig.get_window_config(self.window_type)
        except:
            config = {"width": 1200, "height": 800, "maximized": False}
        
        self.root.minsize(1000, 700)
        
        width = max(config['width'], 1000)
        height = max(config['height'], 700)
        self.root.geometry(f"{width}x{height}")
        
        if config.get('maximized', False):
            self.root.state('zoomed')
        
        self.root.configure(bg=COLORS['bg'])
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def create_widgets(self):
        """Crear interfaz"""
        # Panel superior con controles
        self.create_control_panel()
        
        # Panel central con visualizaciones
        self.create_visualization_panel()
        
        # Panel inferior con información
        self.create_info_panel()
    
    def create_control_panel(self):
        """Crear panel de controles"""
        control_frame = tk.Frame(self.root, bg=COLORS['bg'], pady=10)
        control_frame.grid(row=0, column=0, sticky='ew', padx=10)
        
        # Botón volver
        btn_back = tk.Button(
            control_frame,
            text="⬅️ Volver",
            font=FONTS['button'],
            bg=COLORS['gray'],
            fg='white',
            cursor='hand2',
            command=self.go_back,
            padx=15,
            pady=8,
            relief='flat',
            bd=0
        )
        btn_back.pack(side='left', padx=5)
        
        # Botón seleccionar archivo
        btn_select = tk.Button(
            control_frame,
            text="📁 Seleccionar Audio",
            font=FONTS['button'],
            bg=COLORS['primary'],
            fg='white',
            cursor='hand2',
            command=self.select_audio,
            padx=15,
            pady=8,
            relief='flat',
            bd=0
        )
        btn_select.pack(side='left', padx=5)
        
        # Label del archivo actual (inicializar antes de usar)
        self.label_file = tk.Label(
            control_frame,
            text="No hay archivo seleccionado",
            font=FONTS['body'],
            bg=COLORS['bg'],
            fg=COLORS['dark']
        )
        self.label_file.pack(side='left', padx=15)
        
        # Botones de visualización
        viz_frame = tk.Frame(control_frame, bg=COLORS['bg'])
        viz_frame.pack(side='right', padx=5)
        
        self.btn_spectrogram = tk.Button(
            viz_frame,
            text="🎨 Espectrograma",
            font=FONTS['button'],
            bg=COLORS['success'],
            fg='white',
            cursor='hand2',
            command=self.show_spectrogram,
            padx=12,
            pady=8,
            state='disabled',
            relief='flat',
            bd=0
        )
        self.btn_spectrogram.pack(side='left', padx=3)
        
        self.btn_bands = tk.Button(
            viz_frame,
            text="📊 Bandas",
            font=FONTS['button'],
            bg=COLORS['success'],
            fg='white',
            cursor='hand2',
            command=self.show_bands,
            padx=12,
            pady=8,
            state='disabled',
            relief='flat',
            bd=0
        )
        self.btn_bands.pack(side='left', padx=3)
    
    def create_visualization_panel(self):
        """Crear panel de visualización"""
        viz_container = tk.Frame(self.root, bg='white', relief='sunken', bd=2)
        viz_container.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        viz_container.grid_rowconfigure(0, weight=1)
        viz_container.grid_columnconfigure(0, weight=1)
        
        # Frame para el canvas de matplotlib
        self.canvas_frame = tk.Frame(viz_container, bg='white')
        self.canvas_frame.grid(row=0, column=0, sticky='nsew')
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Mensaje inicial
        welcome = tk.Label(
            self.canvas_frame,
            text="📊 Analizador FFT\n\n" +
                 "Selecciona un archivo de audio para comenzar el análisis\n\n" +
                 "🔹 Espectrograma: Frecuencias en el tiempo\n" +
                 "🔹 Bandas: Distribución de energía",
            font=FONTS['body'],
            bg='white',
            fg=COLORS['gray'],
            justify='center'
        )
        welcome.place(relx=0.5, rely=0.5, anchor='center')
        self.welcome_label = welcome
    
    def create_info_panel(self):
        """Crear panel de información"""
        info_frame = tk.Frame(self.root, bg=COLORS['bg'], pady=5)
        info_frame.grid(row=2, column=0, sticky='ew', padx=10)
        
        # Frame para estadísticas
        stats_frame = tk.LabelFrame(
            info_frame,
            text="📋 Información del Análisis",
            font=FONTS['body'],
            bg=COLORS['bg'],
            fg=COLORS['text']
        )
        stats_frame.pack(fill='x', pady=5)
        
        # Text widget para mostrar información
        self.info_text = tk.Text(
            stats_frame,
            height=4,
            font=('Consolas', 9),
            bg='#f5f5f5',
            fg=COLORS['text'],
            relief='flat',
            padx=10,
            pady=5
        )
        self.info_text.pack(fill='x', padx=5, pady=5)
        self.info_text.insert('1.0', 'Esperando análisis...')
        self.info_text.config(state='disabled')
    
    def select_audio(self):
        """Seleccionar archivo de audio"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de audio",
            filetypes=[
                ("Archivos de audio", "*.wav *.mp3 *.flac *.ogg"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            self.load_audio(file_path)
    
    def load_audio(self, file_path):
        """Cargar y analizar audio"""
        # Mostrar mensaje de carga
        self.label_file.config(text="⏳ Cargando audio...")
        
        def analyze():
            try:
                print(f"Cargando audio desde: {file_path}")
                
                # Cargar audio
                self.current_audio_path = file_path
                self.current_audio, sr = self.analyzer.load_audio(file_path)
                
                print(f"Audio cargado exitosamente: {len(self.current_audio)} samples")
                
                # Actualizar UI en hilo principal (verificar que la ventana existe)
                try:
                    self.root.after(0, self.on_audio_loaded, file_path)
                except Exception as e:
                    print(f"Error al actualizar UI: {e}")
                
            except Exception as e:
                print(f"Error al cargar audio: {e}")
                import traceback
                traceback.print_exc()
                
                try:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error",
                        f"Error al cargar el audio:\n{str(e)}"
                    ))
                except:
                    pass  # Ventana cerrada
        
        # Ejecutar en hilo separado
        threading.Thread(target=analyze, daemon=True).start()
    
    def on_audio_loaded(self, file_path):
        """Callback cuando el audio se carga"""
        filename = os.path.basename(file_path)
        self.label_file.config(text=f"📄 {filename}")
        
        # Habilitar botones
        self.btn_spectrogram.config(state='normal')
        self.btn_bands.config(state='normal')
        
        # Mostrar espectrograma por defecto
        self.show_spectrogram()
        
        # Mostrar información
        self.update_info()
    
    def show_spectrum(self):
        """Mostrar espectro de frecuencias"""
        if self.current_audio is None:
            messagebox.showwarning("Advertencia", "No hay audio cargado")
            return
        
        try:
            print("Generando espectro de frecuencias...")
            filename = os.path.basename(self.current_audio_path)
            fig = self.analyzer.create_spectrum_plot(
                self.current_audio,
                title=f"Espectro de Frecuencias - {filename}"
            )
            print("Espectro generado, mostrando figura...")
            self.display_figure(fig)
            print("Figura mostrada exitosamente")
        except Exception as e:
            print(f"Error al generar espectro: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al generar el espectro:\n{str(e)}")
    
    def show_spectrogram(self):
        """Mostrar espectrograma"""
        if self.current_audio is None:
            messagebox.showwarning("Advertencia", "No hay audio cargado")
            return
        
        try:
            print("Generando espectrograma...")
            filename = os.path.basename(self.current_audio_path)
            fig = self.analyzer.create_spectrogram_plot(
                self.current_audio,
                title=f"Espectrograma - {filename}"
            )
            print("Espectrograma generado, mostrando figura...")
            self.display_figure(fig)
            print("Figura mostrada exitosamente")
        except Exception as e:
            print(f"Error al generar espectrograma: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al generar el espectrograma:\n{str(e)}")
    
    def show_bands(self):
        """Mostrar análisis de bandas"""
        if self.current_audio is None:
            messagebox.showwarning("Advertencia", "No hay audio cargado")
            return
        
        try:
            print("Generando análisis de bandas...")
            filename = os.path.basename(self.current_audio_path)
            fig = self.analyzer.create_band_energy_plot(
                self.current_audio,
                title=f"Energía por Banda - {filename}"
            )
            print("Análisis de bandas generado, mostrando figura...")
            self.display_figure(fig)
            print("Figura mostrada exitosamente")
        except Exception as e:
            print(f"Error al generar análisis de bandas: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al generar el análisis:\n{str(e)}")
    
    def display_figure(self, fig):
        """Mostrar figura de matplotlib en el canvas"""
        try:
            print("Limpiando canvas anterior...")
            # Limpiar canvas anterior
            if self.current_canvas:
                self.current_canvas.get_tk_widget().destroy()
            
            # Ocultar mensaje de bienvenida
            if hasattr(self, 'welcome_label') and self.welcome_label.winfo_exists():
                self.welcome_label.destroy()
            
            print("Creando nuevo canvas...")
            # Crear nuevo canvas
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.grid(row=0, column=0, sticky='nsew')
            
            print("Agregando toolbar...")
            # Agregar toolbar de navegación
            toolbar_frame = tk.Frame(self.canvas_frame)
            toolbar_frame.grid(row=1, column=0, sticky='ew')
            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
            toolbar.update()
            
            self.current_canvas = canvas
            print("Canvas mostrado exitosamente")
            
        except Exception as e:
            print(f"Error al mostrar figura: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def update_info(self):
        """Actualizar panel de información"""
        if self.current_audio is None:
            return
        
        try:
            summary = self.analyzer.get_analysis_summary(self.current_audio_path)
            
            # Formatear información
            info_lines = []
            info_lines.append(f"⏱️  Duración: {summary['duracion']:.2f} segundos")
            info_lines.append(f"🎵 Sample Rate: {summary['sample_rate']} Hz")
            info_lines.append(f"\n📊 Top 5 Frecuencias Dominantes:")
            
            for i, (freq, mag) in enumerate(summary['frecuencias_dominantes'], 1):
                info_lines.append(f"  {i}. {freq:.1f} Hz (magnitud: {mag:.0f})")
            
            # Actualizar text widget
            self.info_text.config(state='normal')
            self.info_text.delete('1.0', 'end')
            self.info_text.insert('1.0', '\n'.join(info_lines))
            self.info_text.config(state='disabled')
            
        except Exception as e:
            print(f"Error actualizando info: {e}")
    
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
                try:
                    config = WindowConfig.get_window_config(self.window_type)
                    width = config['width']
                    height = config['height']
                except:
                    width = 1200
                    height = 800
            
            WindowConfig.save_window_config(self.window_type, width, height, is_maximized)
        except:
            pass
    
    def on_closing(self):
        """Guardar estado antes de cerrar"""
        self.save_window_state()
        plt.close('all')  # Cerrar todas las figuras de matplotlib
        self.root.destroy()
    
    def go_back(self):
        """Volver al menú principal"""
        if messagebox.askyesno("Confirmar", "¿Volver al menú principal?"):
            self.save_window_state()
            plt.close('all')
            self.root.destroy()
            from gui_app import main
            main()
            root.mainloop()
