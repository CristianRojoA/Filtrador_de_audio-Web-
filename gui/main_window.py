"""
🪟 VENTANA PRINCIPAL
=====================
Ventana principal que integra todos los componentes
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
from io import StringIO
from .styles import COLORS, FONTS, DIMENSIONS
from .control_panel import ControlPanel
from .results_panel import ResultsPanel
from .window_config import WindowConfig
from .metadata_dialog import MetadataDialog
from audio_metadata import AudioMetadata

class AudioClassifierGUI:
    """Ventana principal de la aplicación"""
    
    def __init__(self, root, entrenador_class):
        self.root = root
        self.entrenador_class = entrenador_class
        self.entrenador = None
        self.archivo_actual = None
        self.resultado_temporal = None
        self.window_type = "identify"
        
        # Configurar ventana
        self.setup_window()
        
        # Crear interfaz
        self.create_widgets()
        
        # Configurar eventos de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind('<Configure>', self.on_configure)
        
        # Cargar modelo
        self.root.after(100, self.load_model)
    
    def setup_window(self):
        """Configurar la ventana principal"""
        self.root.title("🎵 Clasificador de Audio - Análisis Temporal")
        
        # Cargar configuración guardada
        config = WindowConfig.get_window_config(self.window_type)
        
        # Establecer tamaño mínimo
        self.root.minsize(900, 650)
        
        # Aplicar tamaño guardado
        width = max(config['width'], 900)
        height = max(config['height'], 650)
        self.root.geometry(f"{width}x{height}")
        
        # Aplicar estado maximizado si corresponde
        if config.get('maximized', False):
            self.root.state('zoomed')
        
        self.root.configure(bg=COLORS['bg'])
        
        # Hacer ventana responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Configurar estilo ttk
        style = ttk.Style()
        style.theme_use('clam')
    
    def create_widgets(self):
        """Crear todos los widgets"""
        # Header
        self.create_header()
        
        # Contenedor principal
        main_container = tk.Frame(self.root, bg=COLORS['bg'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Panel izquierdo - Controles
        left_panel = tk.Frame(main_container, bg='white', relief='solid', bd=1)
        left_panel.pack(side='left', fill='both', padx=(0, 10))
        
        self.control_panel = ControlPanel(
            left_panel,
            on_file_select=self.on_file_selected,
            on_predict_simple=self.predict_simple,
            on_predict_temporal=self.predict_temporal,
            on_export=self.export_json
        )
        
        # Panel derecho - Resultados
        right_panel = tk.Frame(main_container, bg='white', relief='solid', bd=1)
        right_panel.pack(side='right', fill='both', expand=True)
        
        self.results_panel = ResultsPanel(right_panel)
        
        # Botón volver
        btn_back = tk.Button(
            main_container,
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
        self.create_status_bar()
    
    def create_header(self):
        """Crear header de la aplicación"""
        header = tk.Frame(self.root, bg=COLORS['primary'], height=DIMENSIONS['header_height'])
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🎵 Clasificador de Audio con Análisis Temporal",
            font=FONTS['title'],
            bg=COLORS['primary'],
            fg='white'
        ).pack(pady=25)
    
    def create_status_bar(self):
        """Crear barra de estado"""
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
    
    def load_model(self):
        """Cargar modelo en hilo separado"""
        self.update_status("🔄 Cargando modelo...", COLORS['warning'])
        
        def load():
            try:
                self.entrenador = self.entrenador_class()
                if self.entrenador.cargar_modelo_entrenado():
                    self.root.after(0, lambda: self.update_status("✅ Modelo cargado correctamente", COLORS['success']))
                    self.root.after(0, lambda: self.results_panel.append("\n✅ Modelo cargado y listo para usar\n\n"))
                else:
                    self.root.after(0, lambda: self.update_status("❌ No hay modelo entrenado", COLORS['danger']))
                    self.root.after(0, lambda: messagebox.showerror("Error", "No hay modelo entrenado. Entrena uno primero con main.py (opción 3)"))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"❌ Error: {str(e)}", COLORS['danger']))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error cargando modelo:\n{str(e)}"))
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
    
    def on_file_selected(self, filename):
        """Callback cuando se selecciona un archivo"""
        self.archivo_actual = filename
        self.update_status(f"✅ Archivo seleccionado", COLORS['success'])
    
    def predict_simple(self):
        """Realizar predicción simple"""
        if not self.validate_ready():
            return
        
        self.control_panel.disable_buttons()
        self.update_status("🔍 Analizando audio...", COLORS['warning'])
        self.results_panel.clear()
        
        def analyze():
            try:
                # Capturar salida de consola
                old_stdout = sys.stdout
                sys.stdout = StringIO()
                
                self.entrenador.predecir_audio(self.archivo_actual, mostrar_detalles=True)
                
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                self.root.after(0, lambda: self.results_panel.set_text(output))
                self.root.after(0, lambda: self.update_status("✅ Análisis completado", COLORS['success']))
                self.root.after(0, self.control_panel.enable_buttons)
                
            except Exception as e:
                self.root.after(0, lambda: self.results_panel.set_text(f"\n❌ Error: {str(e)}\n"))
                self.root.after(0, lambda: self.update_status("❌ Error en análisis", COLORS['danger']))
                self.root.after(0, self.control_panel.enable_buttons)
        
        thread = threading.Thread(target=analyze, daemon=True)
        thread.start()
    
    def predict_temporal(self):
        """Realizar análisis temporal"""
        if not self.validate_ready():
            return
        
        ventana = self.control_panel.get_ventana()
        
        self.control_panel.disable_buttons()
        self.update_status("⏰ Realizando análisis temporal...", COLORS['warning'])
        self.results_panel.clear()
        
        def analyze():
            try:
                # Capturar salida de consola
                old_stdout = sys.stdout
                sys.stdout = StringIO()
                
                self.resultado_temporal = self.entrenador.predecir_audio_temporal(
                    self.archivo_actual,
                    ventana_segundos=ventana
                )
                
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                # Analizar porcentajes de tráfico
                self.root.after(0, lambda: self.analyze_traffic_recommendation(self.resultado_temporal))
                
                self.root.after(0, lambda: self.results_panel.set_text(output))
                self.root.after(0, lambda: self.update_status("✅ Análisis temporal completado", COLORS['success']))
                self.root.after(0, self.control_panel.enable_buttons)
                self.root.after(0, self.control_panel.enable_export)
                
            except Exception as e:
                self.root.after(0, lambda: self.results_panel.set_text(f"\n❌ Error: {str(e)}\n"))
                self.root.after(0, lambda: self.update_status("❌ Error en análisis", COLORS['danger']))
                self.root.after(0, self.control_panel.enable_buttons)
        
        thread = threading.Thread(target=analyze, daemon=True)
        thread.start()
    
    def analyze_traffic_recommendation(self, resultado):
        """Analizar si se recomienda un semáforo basado en el tráfico pesado"""
        if resultado is None:
            print("❌ Debug: resultado es None")
            return
        
        try:
            # Contar detecciones por clase
            mucho_trafico_count = 0
            poco_trafico_count = 0
            
            # Obtener lista de detecciones (puede ser dict o list)
            detecciones = resultado.get('detecciones_agrupadas', []) if isinstance(resultado, dict) else resultado
            
            print(f"🔍 Debug: Total detecciones agrupadas: {len(detecciones)}")
            
            for deteccion in detecciones:
                clase = deteccion.get('clase', '')
                print(f"🔍 Debug: Clase detectada: '{clase}'")
                
                # Detectar mucho tráfico (todas las variaciones posibles)
                if 'Mucho' in clase or 'MUCHO' in clase or 'mucho' in clase:
                    mucho_trafico_count += 1
                    print(f"✅ Contado como MUCHO_TRAFICO")
                # Detectar poco tráfico (todas las variaciones posibles)
                elif 'Poco' in clase or 'POCO' in clase or 'poco' in clase:
                    poco_trafico_count += 1
                    print(f"✅ Contado como POCO_TRAFICO")
            
            print(f"\n📊 Resumen:")
            print(f"   Mucho Tráfico: {mucho_trafico_count}")
            print(f"   Poco Tráfico: {poco_trafico_count}")
            
            # Calcular porcentajes
            total = mucho_trafico_count + poco_trafico_count
            if total == 0:
                print("⚠️ No hay detecciones de tráfico")
                return
            
            porcentaje_mucho = (mucho_trafico_count / total) * 100
            porcentaje_poco = (poco_trafico_count / total) * 100
            
            print(f"   Porcentaje Mucho: {porcentaje_mucho:.1f}%")
            print(f"   Porcentaje Poco: {porcentaje_poco:.1f}%")
            print(f"   Umbral requerido: {porcentaje_poco * 1.6:.1f}%")
            
            # Verificar si mucho tráfico supera al poco tráfico en más del 60%
            if porcentaje_mucho > porcentaje_poco * 1.6:
                print(f"✅ ¡SUGERENCIA ACTIVADA!")
                mensaje = (
                    f"💡 SUGERENCIA: Iniciar Solicitud de Semáforo\n\n"
                    f"Se cumple la condición estipulada por el Manual de Señalización\n"
                    f"de Tránsito (Pág. 166, Inciso A):\n"
                    f'"Flujos vehiculares en las horas de mayor demanda"\n\n'
                    f"Se sugiere iniciar el proceso de solicitud para la instalación\n"
                    f"de un semáforo en esta ubicación, según lo establecido en la\n"
                    f"normativa de tránsito vigente."
                )
                messagebox.showinfo("💡 Sugerencia de Análisis", mensaje)
            else:
                print(f"ℹ️ No se cumple el umbral para mostrar alerta")
        except Exception as e:
            print(f"❌ Error al analizar recomendación: {e}")
            import traceback
            traceback.print_exc()
    
    def export_json(self):
        """Exportar resultados a JSON con metadatos de ubicación"""
        if self.resultado_temporal is None:
            messagebox.showwarning("Advertencia", "Primero realiza un análisis temporal")
            return
        
        # Preguntar si desea agregar metadatos
        respuesta = messagebox.askyesno(
            "Metadatos de Ubicación",
            "¿Deseas agregar información de ubicación y contexto a la exportación?"
        )
        
        try:
            # Exportar resultados normales
            output_path = self.entrenador.exportar_detecciones_json(self.resultado_temporal)
            
            # Si acepta, abrir diálogo de metadatos
            if respuesta:
                import os
                audio_file = os.path.basename(self.archivo_actual)
                dialog = MetadataDialog(self.root, audio_file)
                metadata_data = dialog.show()
                
                if metadata_data:
                    # Crear objeto de metadatos
                    metadata = AudioMetadata(self.archivo_actual)
                    
                    # Establecer ubicación (sin latitud/longitud)
                    metadata.set_ubicacion(
                        direccion=metadata_data["ubicacion"]["direccion"],
                        ciudad=metadata_data["ubicacion"]["ciudad"],
                        pais=metadata_data["ubicacion"]["pais"],
                        notas=metadata_data["ubicacion"]["notas"]
                    )
                    
                    # Establecer grabación (sin calidad)
                    metadata.set_grabacion_info(
                        fecha=metadata_data["grabacion"]["fecha"],
                        hora=metadata_data["grabacion"]["hora"]
                    )
                    
                    # Establecer condiciones (solo clima y día de semana)
                    metadata.set_condiciones(
                        clima=metadata_data["condiciones"]["clima"],
                        dia_semana=metadata_data["condiciones"]["dia_semana"]
                    )
                    
                    # Establecer dispositivo
                    metadata.set_dispositivo(
                        tipo=metadata_data["dispositivo"]["tipo"],
                        marca_modelo=metadata_data["dispositivo"]["marca_modelo"]
                    )
                    
                    # Establecer notas
                    if metadata_data["notas"]:
                        metadata.set_notas(metadata_data["notas"])
                    
                    # Establecer resultados del análisis
                    if isinstance(self.resultado_temporal, dict):
                        detecciones = self.resultado_temporal.get('detecciones_agrupadas', [])
                        if detecciones:
                            primera = detecciones[0]
                            metadata.set_analisis(
                                clasificacion=primera.get('clase'),
                                confianza=primera.get('confianza'),
                                detecciones=[{
                                    'tiempo': d.get('tiempo_inicio'),
                                    'clase': d.get('clase'),
                                    'confianza': d.get('confianza')
                                } for d in detecciones]
                            )
                    
                    # Guardar metadatos
                    metadata_path = metadata.save_to_file()
                    
                    # Mostrar resumen
                    summary = metadata.generate_summary()
                    self.results_panel.append(f"\n{summary}\n")
                    self.results_panel.append(f"\n💾 Metadatos guardados en: {metadata_path}\n")
                    
                    messagebox.showinfo(
                        "Éxito",
                        f"Resultados exportados a:\n{output_path}\n\nMetadatos guardados en:\n{metadata_path}"
                    )
                else:
                    messagebox.showinfo("Éxito", f"Resultados exportados a:\n{output_path}")
            else:
                messagebox.showinfo("Éxito", f"Resultados exportados a:\n{output_path}")
                
            self.results_panel.append(f"\n💾 Exportado a: {output_path}\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def validate_ready(self):
        """Validar que todo esté listo para analizar"""
        if self.entrenador is None:
            messagebox.showwarning("Advertencia", "El modelo aún se está cargando. Espera un momento.")
            return False
        
        if not hasattr(self.entrenador, 'modelo'):
            messagebox.showwarning("Advertencia", "No hay modelo cargado. Entrena uno primero.")
            return False
        
        if self.archivo_actual is None:
            messagebox.showwarning("Advertencia", "Selecciona un archivo de audio primero")
            return False
        
        import os
        if not os.path.exists(self.archivo_actual):
            messagebox.showerror("Error", "El archivo seleccionado no existe")
            return False
        
        return True
    
    def update_status(self, message, color=None):
        """Actualizar barra de estado"""
        if color is None:
            color = COLORS['gray']
        self.status_bar.config(text=message, fg=color)
    
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
    
    def go_back(self):
        """Volver al menú principal"""
        from tkinter import messagebox
        if messagebox.askyesno("Confirmar", "¿Volver al menú principal?"):
            self.save_window_state()
            self.root.destroy()
            import tkinter as tk
            from .start_window import StartWindow
            from .training_window import TrainingWindow
            
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
                TrainingWindow(train_root, self.entrenador_class)
                train_root.mainloop()
            
            def open_identify():
                root.destroy()
                identify_root = tk.Tk()
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
