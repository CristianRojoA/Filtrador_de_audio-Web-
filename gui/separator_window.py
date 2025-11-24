"""
🎵 VENTANA DE SEPARACIÓN DE AUDIO
==================================
Interfaz para separar y exportar componentes de audio
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import soundfile as sf
from .styles import COLORS, FONTS
from .window_config import WindowConfig
from audio_separator import AudioSeparator

class SeparatorWindow:
    """Ventana para separar y filtrar audio"""
    
    def __init__(self, root, entrenador_class):
        self.root = root
        self.entrenador_class = entrenador_class
        self.entrenador = None
        self.separator = None
        self.segments = []
        self.selected_segments = []
        self.window_type = "separator"
        
        self.setup_window()
        self.create_widgets()
        
        # Configurar eventos
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind('<Configure>', self.on_configure)
        
        # Cargar modelo
        self.root.after(100, self.load_model)
    
    def setup_window(self):
        """Configurar ventana"""
        self.root.title("🎵 Separador de Audio")
        
        try:
            config = WindowConfig.get_window_config(self.window_type)
        except:
            config = {"width": 1200, "height": 750, "maximized": False}
        
        self.root.minsize(1000, 700)
        
        width = max(config['width'], 1000)
        height = max(config['height'], 700)
        self.root.geometry(f"{width}x{height}")
        
        if config.get('maximized', False):
            self.root.state('zoomed')
        
        self.root.configure(bg=COLORS['bg'])
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def load_model(self):
        """Cargar modelo en segundo plano"""
        def load():
            try:
                self.entrenador = self.entrenador_class()
                # Intentar cargar modelo entrenado
                try:
                    self.entrenador.cargar_modelo_entrenado()
                    print("✅ Modelo cargado correctamente")
                except:
                    print("⚠️ No hay modelo entrenado. Entrena un modelo primero para usar el separador.")
                    self.entrenador = None
                
                self.separator = AudioSeparator(self.entrenador)
            except Exception as e:
                print(f"Error al inicializar: {e}")
                import traceback
                traceback.print_exc()
                self.separator = AudioSeparator(None)
        
        threading.Thread(target=load, daemon=True).start()
    
    def create_widgets(self):
        """Crear interfaz"""
        # Header
        header = tk.Frame(self.root, bg=COLORS['primary'], height=80)
        header.grid(row=0, column=0, sticky='ew')
        
        tk.Label(
            header,
            text="🎵 Separador de Audio",
            font=FONTS['title'],
            bg=COLORS['primary'],
            fg='white'
        ).pack(pady=20)
        
        # Contenedor principal
        main_container = tk.Frame(self.root, bg=COLORS['bg'])
        main_container.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=2)
        
        # Panel izquierdo - Controles
        self.create_control_panel(main_container)
        
        # Panel derecho - Resultados
        self.create_results_panel(main_container)
        
        # Footer con botón volver
        footer = tk.Frame(self.root, bg=COLORS['bg'])
        footer.grid(row=2, column=0, sticky='ew', padx=20, pady=10)
        
        tk.Button(
            footer,
            text="⬅️ Volver al Menú",
            font=FONTS['button'],
            bg=COLORS['gray'],
            fg='white',
            cursor='hand2',
            command=self.go_back,
            padx=20,
            pady=10,
            relief='flat',
            bd=0
        ).pack()
    
    def create_control_panel(self, parent):
        """Crear panel de controles con scroll"""
        # Frame contenedor
        panel_container = tk.Frame(parent, bg=COLORS['panel_bg'], relief='raised', bd=2)
        panel_container.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        # Canvas para scroll
        canvas = tk.Canvas(panel_container, bg=COLORS['panel_bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(panel_container, orient='vertical', command=canvas.yview)
        
        # Frame scrollable
        panel = tk.Frame(canvas, bg=COLORS['panel_bg'])
        
        # Configurar canvas
        panel.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=panel, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Título
        tk.Label(
            panel,
            text="⚙️ Controles",
            font=FONTS['heading'],
            bg=COLORS['panel_bg'],
            fg=COLORS['primary']
        ).pack(pady=15, padx=10)
        
        # 1. Cargar audio
        self.create_load_section(panel)
        
        # 2. Analizar
        tk.Frame(panel, height=2, bg=COLORS['border']).pack(fill='x', padx=20, pady=15)
        self.create_analyze_section(panel)
        
        # 3. Filtros
        tk.Frame(panel, height=2, bg=COLORS['border']).pack(fill='x', padx=20, pady=15)
        self.create_filter_section(panel)
        
        # 4. Exportar
        tk.Frame(panel, height=2, bg=COLORS['border']).pack(fill='x', padx=20, pady=15)
        self.create_export_section(panel)
    
    def create_load_section(self, parent):
        """Sección de carga de audio"""
        frame = tk.Frame(parent, bg=COLORS['panel_bg'])
        frame.pack(fill='x', padx=15, pady=5)
        
        tk.Label(
            frame,
            text="📁 Archivo de Audio",
            font=FONTS['normal'],
            bg=COLORS['panel_bg']
        ).pack(anchor='w', pady=(0, 5))
        
        tk.Button(
            frame,
            text="📂 Seleccionar Audio",
            font=FONTS['button'],
            bg=COLORS['primary'],
            fg='white',
            cursor='hand2',
            command=self.load_audio,
            padx=15,
            pady=8,
            relief='flat',
            bd=0
        ).pack(fill='x')
        
        self.label_file = tk.Label(
            frame,
            text="Sin archivo",
            font=FONTS['small'],
            bg=COLORS['panel_bg'],
            fg=COLORS['text_secondary'],
            wraplength=250
        )
        self.label_file.pack(anchor='w', pady=5)
    
    def create_analyze_section(self, parent):
        """Sección de análisis"""
        frame = tk.Frame(parent, bg=COLORS['panel_bg'])
        frame.pack(fill='x', padx=15, pady=5)
        
        tk.Label(
            frame,
            text="🔍 Análisis",
            font=FONTS['normal'],
            bg=COLORS['panel_bg']
        ).pack(anchor='w', pady=(0, 5))
        
        # Ventana de análisis
        window_frame = tk.Frame(frame, bg=COLORS['panel_bg'])
        window_frame.pack(fill='x', pady=5)
        
        tk.Label(
            window_frame,
            text="Ventana (seg):",
            font=FONTS['small'],
            bg=COLORS['panel_bg']
        ).pack(side='left')
        
        self.entry_window = tk.Entry(window_frame, width=8)
        self.entry_window.insert(0, "2.0")
        self.entry_window.pack(side='left', padx=5)
        
        self.btn_analyze = tk.Button(
            frame,
            text="🔍 Analizar Audio",
            font=FONTS['button'],
            bg=COLORS['secondary'],
            fg='white',
            cursor='hand2',
            command=self.analyze_audio,
            state='disabled',
            padx=15,
            pady=8,
            relief='flat',
            bd=0
        )
        self.btn_analyze.pack(fill='x', pady=5)
    
    def create_filter_section(self, parent):
        """Sección de filtros"""
        frame = tk.Frame(parent, bg=COLORS['panel_bg'])
        frame.pack(fill='x', padx=15, pady=5)
        
        tk.Label(
            frame,
            text="🎛️ Filtros",
            font=FONTS['normal'],
            bg=COLORS['panel_bg']
        ).pack(anchor='w', pady=(0, 5))
        
        # Frame para checkboxes de clases
        self.filter_frame = tk.Frame(frame, bg=COLORS['panel_bg'])
        self.filter_frame.pack(fill='x', pady=5)
        
        # Confianza mínima
        conf_frame = tk.Frame(frame, bg=COLORS['panel_bg'])
        conf_frame.pack(fill='x', pady=5)
        
        tk.Label(
            conf_frame,
            text="Confianza mín:",
            font=FONTS['small'],
            bg=COLORS['panel_bg']
        ).pack(side='left')
        
        self.entry_confidence = tk.Entry(conf_frame, width=8)
        self.entry_confidence.insert(0, "0.5")
        self.entry_confidence.pack(side='left', padx=5)
        
        # Checkbox para desconocidos
        self.var_unknown = tk.BooleanVar()
        tk.Checkbutton(
            frame,
            text="Solo desconocidos",
            variable=self.var_unknown,
            bg=COLORS['panel_bg'],
            font=FONTS['small']
        ).pack(anchor='w', pady=2)
        
        # Checkbox para unir
        self.var_merge = tk.BooleanVar(value=True)
        tk.Checkbutton(
            frame,
            text="Unir consecutivos",
            variable=self.var_merge,
            bg=COLORS['panel_bg'],
            font=FONTS['small']
        ).pack(anchor='w', pady=2)
        
        # Botón aplicar filtros
        self.btn_filter = tk.Button(
            frame,
            text="✅ Aplicar Filtros",
            font=FONTS['button'],
            bg=COLORS['accent'],
            fg='white',
            cursor='hand2',
            command=self.apply_filters,
            state='disabled',
            padx=15,
            pady=8,
            relief='flat',
            bd=0
        )
        self.btn_filter.pack(fill='x', pady=5)
    
    def create_export_section(self, parent):
        """Sección de exportación"""
        frame = tk.Frame(parent, bg=COLORS['panel_bg'])
        frame.pack(fill='x', padx=15, pady=5)
        
        tk.Label(
            frame,
            text="💾 Exportar",
            font=FONTS['normal'],
            bg=COLORS['panel_bg']
        ).pack(anchor='w', pady=(0, 5))
        
        # Tipo de exportación
        self.export_type = tk.StringVar(value="individual")
        
        tk.Radiobutton(
            frame,
            text="Archivos individuales",
            variable=self.export_type,
            value="individual",
            bg=COLORS['panel_bg'],
            font=FONTS['small']
        ).pack(anchor='w')
        
        tk.Radiobutton(
            frame,
            text="Audio unificado",
            variable=self.export_type,
            value="merged",
            bg=COLORS['panel_bg'],
            font=FONTS['small']
        ).pack(anchor='w')
        
        # Opción de filtrado por clase
        tk.Frame(frame, height=1, bg=COLORS['border']).pack(fill='x', pady=10)
        
        self.apply_isolation = tk.BooleanVar(value=False)
        chk_isolation = tk.Checkbutton(
            frame,
            text="🎯 Aplicar filtro de frecuencias (FFT/IFFT)",
            variable=self.apply_isolation,
            bg=COLORS['panel_bg'],
            font=FONTS['small'],
            activebackground=COLORS['panel_bg'],
            command=self.toggle_filter_options
        )
        chk_isolation.pack(anchor='w')
        
        # Frame para opciones de filtrado
        self.filter_options_frame = tk.Frame(frame, bg=COLORS['panel_bg'])
        self.filter_options_frame.pack(fill='x', padx=20, pady=5)
        
        # Modo de filtrado
        self.filter_mode = tk.StringVar(value='keep_motors')
        
        tk.Label(
            self.filter_options_frame,
            text="Modo de filtrado:",
            font=('Segoe UI', 9, 'bold'),
            bg=COLORS['panel_bg']
        ).pack(anchor='w')
        
        tk.Radiobutton(
            self.filter_options_frame,
            text="🚗 Solo motores (elimina voces, claxon, ruido)",
            variable=self.filter_mode,
            value='keep_motors',
            bg=COLORS['panel_bg'],
            font=FONTS['small']
        ).pack(anchor='w', padx=10)
        
        tk.Radiobutton(
            self.filter_options_frame,
            text="🚦 Todo el vehículo (mantiene más frecuencias)",
            variable=self.filter_mode,
            value='keep_all_vehicle',
            bg=COLORS['panel_bg'],
            font=FONTS['small']
        ).pack(anchor='w', padx=10)
        
        tk.Radiobutton(
            self.filter_options_frame,
            text="⚙️ Personalizado (rangos por defecto)",
            variable=self.filter_mode,
            value='custom',
            bg=COLORS['panel_bg'],
            font=FONTS['small']
        ).pack(anchor='w', padx=10)
        
        # Ocultar opciones inicialmente
        self.filter_options_frame.pack_forget()
        
        # Botones de exportación
        self.btn_export = tk.Button(
            frame,
            text="💾 Exportar Audio",
            font=FONTS['button'],
            bg=COLORS['success'],
            fg='white',
            cursor='hand2',
            command=self.export_audio,
            state='disabled',
            padx=15,
            pady=8,
            relief='flat',
            bd=0
        )
        self.btn_export.pack(fill='x', pady=5)
        
        self.btn_export_meta = tk.Button(
            frame,
            text="📋 Exportar JSON",
            font=FONTS['button'],
            bg=COLORS['info'],
            fg='white',
            cursor='hand2',
            command=self.export_metadata,
            state='disabled',
            padx=15,
            pady=8,
            relief='flat',
            bd=0
        )
        self.btn_export_meta.pack(fill='x', pady=5)
        
        # Separador
        tk.Frame(frame, height=2, bg=COLORS['border']).pack(fill='x', pady=10)
        
        # Exportar audio completo filtrado
        tk.Label(
            frame,
            text="🎵 Audio Completo Filtrado",
            font=('Segoe UI', 9, 'bold'),
            bg=COLORS['panel_bg']
        ).pack(anchor='w', pady=(5, 5))
        
        self.btn_export_full = tk.Button(
            frame,
            text="💾 Exportar Audio Completo (Filtrado)",
            font=FONTS['button'],
            bg=COLORS['warning'],
            fg='white',
            cursor='hand2',
            command=self.export_full_filtered,
            state='disabled',
            padx=15,
            pady=8,
            relief='flat',
            bd=0
        )
        self.btn_export_full.pack(fill='x', pady=5)
        
        tk.Label(
            frame,
            text="Exporta todo el audio con filtro de motores/vehículos",
            font=('Segoe UI', 8),
            bg=COLORS['panel_bg'],
            fg='gray'
        ).pack(anchor='w')
    
    def create_results_panel(self, parent):
        """Crear panel de resultados"""
        panel = tk.Frame(parent, bg=COLORS['panel_bg'], relief='raised', bd=2)
        panel.grid(row=0, column=1, sticky='nsew')
        
        # Título
        tk.Label(
            panel,
            text="📊 Segmentos Detectados",
            font=FONTS['heading'],
            bg=COLORS['panel_bg'],
            fg=COLORS['primary']
        ).pack(pady=15)
        
        # Frame para Treeview
        tree_frame = tk.Frame(panel, bg=COLORS['panel_bg'])
        tree_frame.pack(fill='both', expand=True, padx=15, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview con checkboxes
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('Sel', 'ID', 'Inicio', 'Fin', 'Duración', 'Clase', 'Confianza'),
            show='tree headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        # Configurar columnas
        self.tree.heading('#0', text='✓')
        self.tree.heading('Sel', text='')
        self.tree.heading('ID', text='#')
        self.tree.heading('Inicio', text='Inicio')
        self.tree.heading('Fin', text='Fin')
        self.tree.heading('Duración', text='Duración')
        self.tree.heading('Clase', text='Clase')
        self.tree.heading('Confianza', text='Confianza')
        
        self.tree.column('#0', width=30, anchor='center')
        self.tree.column('Sel', width=0, stretch=False)
        self.tree.column('ID', width=40, anchor='center')
        self.tree.column('Inicio', width=80, anchor='center')
        self.tree.column('Fin', width=80, anchor='center')
        self.tree.column('Duración', width=80, anchor='center')
        self.tree.column('Clase', width=150)
        self.tree.column('Confianza', width=100, anchor='center')
        
        # Bind para hacer clic en checkbox
        self.tree.bind('<Button-1>', self.on_tree_click)
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Botones de reproducción y selección
        action_frame = tk.Frame(panel, bg=COLORS['panel_bg'])
        action_frame.pack(pady=10)
        
        tk.Button(
            action_frame,
            text="▶️ Reproducir Seleccionado",
            font=FONTS['button'],
            bg=COLORS['info'],
            fg='white',
            cursor='hand2',
            command=self.play_selected_segment,
            padx=10,
            pady=5,
            relief='flat',
            bd=0
        ).pack(side='left', padx=5)
        
        tk.Button(
            action_frame,
            text="✓ Seleccionar Todos",
            font=FONTS['small'],
            bg=COLORS['secondary'],
            fg='white',
            cursor='hand2',
            command=self.select_all,
            padx=10,
            pady=5,
            relief='flat',
            bd=0
        ).pack(side='left', padx=5)
        
        tk.Button(
            action_frame,
            text="✗ Deseleccionar Todos",
            font=FONTS['small'],
            bg=COLORS['warning'],
            fg='white',
            cursor='hand2',
            command=self.deselect_all,
            padx=10,
            pady=5,
            relief='flat',
            bd=0
        ).pack(side='left', padx=5)
        
        # Estadísticas
        self.label_stats = tk.Label(
            panel,
            text="Esperando análisis...",
            font=FONTS['small'],
            bg=COLORS['panel_bg'],
            fg=COLORS['text_secondary'],
            justify='left'
        )
        self.label_stats.pack(pady=10)
    
    def toggle_filter_options(self):
        """Mostrar u ocultar opciones de filtrado"""
        if self.apply_isolation.get():
            self.filter_options_frame.pack(fill='x', padx=20, pady=5)
        else:
            self.filter_options_frame.pack_forget()
    
    def load_audio(self):
        """Cargar archivo de audio"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de audio",
            filetypes=[
                ("Archivos de audio", "*.mp3 *.wav *.flac *.ogg"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            if self.separator is None:
                messagebox.showwarning("Aviso", "El modelo aún se está cargando, espera un momento...")
                return
            
            if self.entrenador is None:
                messagebox.showerror(
                    "Modelo no encontrado",
                    "No hay modelo entrenado.\n\n"
                    "Para usar el Separador de Audio necesitas:\n"
                    "1. Ir a 'Entrenar Modelo'\n"
                    "2. Entrenar con tus datos de audio\n"
                    "3. Volver aquí para separar audio"
                )
                return
            
            success, message = self.separator.load_audio(file_path)
            if success:
                filename = Path(file_path).name
                self.label_file.config(
                    text=f"✅ {filename}\n{message}",
                    fg=COLORS['success']
                )
                self.btn_analyze.config(state='normal')
                self.btn_export_full.config(state='normal')
            else:
                self.label_file.config(
                    text=f"❌ {message}",
                    fg=COLORS['danger']
                )
                messagebox.showerror("Error", message)
    
    def analyze_audio(self):
        """Analizar audio en segmentos"""
        try:
            window_size = float(self.entry_window.get())
        except ValueError:
            messagebox.showerror("Error", "Ventana debe ser un número válido")
            return
        
        self.btn_analyze.config(state='disabled', text="⏳ Analizando...")
        
        def analyze():
            try:
                segments, error = self.separator.analyze_segments(window_size)
                
                if error:
                    self.root.after(0, lambda: messagebox.showerror("Error", error))
                    self.root.after(0, lambda: self.btn_analyze.config(
                        state='normal', text="🔍 Analizar Audio"
                    ))
                    return
                
                self.segments = segments
                self.root.after(0, self.display_segments)
            except Exception as e:
                print(f"Error en análisis: {e}")
                import traceback
                traceback.print_exc()
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self.btn_analyze.config(
                    state='normal', text="🔍 Analizar Audio"
                ))
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def display_segments(self):
        """Mostrar segmentos en el Treeview"""
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener clases únicas
        classes = sorted(list(set(seg['clase'] for seg in self.segments)))
        
        # Crear checkboxes para filtros
        for widget in self.filter_frame.winfo_children():
            widget.destroy()
        
        self.class_vars = {}
        for clase in classes:
            var = tk.BooleanVar(value=True)
            self.class_vars[clase] = var
            tk.Checkbutton(
                self.filter_frame,
                text=f"✓ {clase}",
                variable=var,
                bg=COLORS['panel_bg'],
                font=FONTS['small']
            ).pack(anchor='w')
        
        # Mostrar segmentos con checkbox
        self.segment_checkboxes = {}
        for i, seg in enumerate(self.segments, 1):
            item_id = self.tree.insert('', 'end', text='☑', values=(
                '',
                i,
                f"{int(seg['start']//60):02d}:{seg['start']%60:05.2f}",
                f"{int(seg['end']//60):02d}:{seg['end']%60:05.2f}",
                f"{seg['end']-seg['start']:.2f}s",
                seg['clase'],
                f"{seg['confianza']*100:.1f}%"
            ), tags=('checked',))
            self.segment_checkboxes[item_id] = True
        
        # Estadísticas
        total_duration = sum(seg['end'] - seg['start'] for seg in self.segments)
        stats = f"Total segmentos: {len(self.segments)}\n"
        stats += f"Duración total: {total_duration:.2f}s\n"
        stats += f"Clases detectadas: {len(classes)}"
        self.label_stats.config(text=stats)
        
        # Habilitar botones
        self.btn_filter.config(state='normal')
        self.btn_analyze.config(state='normal', text="🔍 Analizar Audio")
    
    def apply_filters(self):
        """Aplicar filtros a los segmentos"""
        if not self.segments:
            return
        
        filtered = self.segments.copy()
        
        # Filtrar por confianza
        try:
            min_conf = float(self.entry_confidence.get())
            filtered = self.separator.filter_by_confidence(filtered, min_conf)
        except ValueError:
            pass
        
        # Filtrar por clases seleccionadas
        selected_classes = [clase for clase, var in self.class_vars.items() if var.get()]
        filtered = self.separator.filter_by_class(filtered, selected_classes)
        
        # Filtrar desconocidos
        if self.var_unknown.get():
            filtered = self.separator.filter_unknown(filtered, 0.7)
        
        # Unir consecutivos
        if self.var_merge.get():
            filtered = self.separator.merge_segments(filtered)
        
        self.selected_segments = filtered
        
        # Actualizar display
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.segment_checkboxes = {}
        for i, seg in enumerate(filtered, 1):
            item_id = self.tree.insert('', 'end', text='☑', values=(
                '',
                i,
                f"{int(seg['start']//60):02d}:{seg['start']%60:05.2f}",
                f"{int(seg['end']//60):02d}:{seg['end']%60:05.2f}",
                f"{seg['end']-seg['start']:.2f}s",
                seg['clase'],
                f"{seg['confianza']*100:.1f}%"
            ), tags=('checked',))
            self.segment_checkboxes[item_id] = True
        
        # Actualizar estadísticas
        total_duration = sum(seg['end'] - seg['start'] for seg in filtered)
        stats = f"Segmentos filtrados: {len(filtered)}\n"
        stats += f"Duración filtrada: {total_duration:.2f}s"
        self.label_stats.config(text=stats)
        
        # Habilitar exportación
        if filtered:
            self.btn_export.config(state='normal')
            self.btn_export_meta.config(state='normal')
        else:
            messagebox.showinfo("Info", "No hay segmentos que cumplan los filtros")
    
    def on_tree_click(self, event):
        """Manejar clic en checkbox"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "tree":
            item = self.tree.identify_row(event.y)
            if item:
                # Cambiar estado del checkbox
                is_checked = self.segment_checkboxes.get(item, False)
                self.segment_checkboxes[item] = not is_checked
                self.tree.item(item, text='☐' if is_checked else '☑')
    
    def on_tree_double_click(self, event):
        """Reproducir segmento al hacer doble clic"""
        item = self.tree.identify_row(event.y)
        if item:
            self.play_segment_by_item(item)
    
    def play_segment_by_item(self, item_id):
        """Reproducir un segmento específico"""
        try:
            # Obtener índice del segmento
            values = self.tree.item(item_id)['values']
            seg_index = values[1] - 1  # ID es 1-indexed
            
            segments_to_use = self.selected_segments if self.selected_segments else self.segments
            if seg_index < len(segments_to_use):
                segment = segments_to_use[seg_index]
                self.play_segment(segment)
        except Exception as e:
            print(f"Error reproduciendo: {e}")
    
    def play_selected_segment(self):
        """Reproducir el segmento seleccionado en el tree"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Selecciona un segmento primero")
            return
        
        self.play_segment_by_item(selection[0])
    
    def play_segment(self, segment):
        """Reproducir un segmento de audio"""
        try:
            import tempfile
            import os
            
            # Extraer audio del segmento
            segment_audio = self.separator.audio_data[segment['start_idx']:segment['end_idx']]
            
            # Guardar temporalmente
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name
                sf.write(tmp_path, segment_audio, self.separator.sample_rate)
            
            # Reproducir con el reproductor del sistema
            if os.name == 'nt':  # Windows
                os.startfile(tmp_path)
            elif os.name == 'posix':  # Linux/Mac
                import subprocess
                subprocess.Popen(['xdg-open', tmp_path])
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir: {str(e)}")
    
    def select_all(self):
        """Seleccionar todos los segmentos"""
        for item in self.tree.get_children():
            self.segment_checkboxes[item] = True
            self.tree.item(item, text='☑')
    
    def deselect_all(self):
        """Deseleccionar todos los segmentos"""
        for item in self.tree.get_children():
            self.segment_checkboxes[item] = False
            self.tree.item(item, text='☐')
    
    def get_checked_segments(self):
        """Obtener segmentos marcados"""
        checked = []
        segments_to_use = self.selected_segments if self.selected_segments else self.segments
        
        for i, item in enumerate(self.tree.get_children()):
            if self.segment_checkboxes.get(item, False) and i < len(segments_to_use):
                checked.append(segments_to_use[i])
        
        return checked
    
    def export_audio(self):
        """Exportar audio seleccionado"""
        # Obtener solo los segmentos marcados
        segments_to_export = self.get_checked_segments()
        
        if not segments_to_export:
            messagebox.showwarning("Aviso", "No hay segmentos marcados para exportar")
            return
        
        export_type = self.export_type.get()
        
        if export_type == "individual":
            output_dir = filedialog.askdirectory(title="Seleccionar carpeta de salida")
            if not output_dir:
                return
            
            try:
                # Obtener el estado del checkbox de aislamiento
                apply_filter = self.apply_isolation.get()
                filter_mode = self.filter_mode.get() if apply_filter else 'keep_motors'
                
                files = self.separator.export_segments(
                    self.selected_segments, 
                    output_dir, 
                    apply_isolation=apply_filter,
                    filter_mode=filter_mode
                )
                
                # Mensaje según el modo
                if apply_filter:
                    mode_msgs = {
                        'keep_motors': '🚗 Solo motores (voces y claxon eliminados)',
                        'keep_all_vehicle': '🚦 Todo el vehículo',
                        'custom': '⚙️ Filtro personalizado'
                    }
                    filter_msg = f"\n\nFiltrado: {mode_msgs.get(filter_mode, '')}"
                else:
                    filter_msg = ""
                
                messagebox.showinfo(
                    "Éxito",
                    f"✅ {len(files)} archivos exportados a:\n{output_dir}{filter_msg}"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")
        
        else:  # merged
            output_file = filedialog.asksaveasfilename(
                title="Guardar audio unificado",
                defaultextension=".wav",
                filetypes=[("WAV files", "*.wav")]
            )
            if not output_file:
                return
            
            success, message = self.separator.export_merged_audio(
                segments_to_export,
                output_file
            )
            
            if success:
                messagebox.showinfo("Éxito", f"✅ {message}")
            else:
                messagebox.showerror("Error", message)
    
    def export_full_filtered(self):
        """Exportar audio completo con filtrado de motores/vehículos"""
        # Ventana de diálogo para elegir clase y modo
        dialog = tk.Toplevel(self.root)
        dialog.title("Exportar Audio Completo Filtrado")
        dialog.geometry("400x300")
        dialog.configure(bg=COLORS['panel_bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(
            dialog,
            text="Configuración de Filtrado",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['panel_bg']
        ).pack(pady=10)
        
        # Clase objetivo
        tk.Label(
            dialog,
            text="Tipo de vehículo a mantener:",
            font=FONTS['normal'],
            bg=COLORS['panel_bg']
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        target_class_var = tk.StringVar(value='auto')
        for clase in ['auto', 'trafico']:
            tk.Radiobutton(
                dialog,
                text=clase.title(),
                variable=target_class_var,
                value=clase,
                bg=COLORS['panel_bg'],
                font=FONTS['small']
            ).pack(anchor='w', padx=40)
        
        # Modo de filtrado
        tk.Label(
            dialog,
            text="Modo de filtrado:",
            font=FONTS['normal'],
            bg=COLORS['panel_bg']
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        filter_mode_var = tk.StringVar(value='keep_motors')
        tk.Radiobutton(
            dialog,
            text="🚗 Solo motores (sin voces/claxon)",
            variable=filter_mode_var,
            value='keep_motors',
            bg=COLORS['panel_bg'],
            font=FONTS['small']
        ).pack(anchor='w', padx=40)
        
        tk.Radiobutton(
            dialog,
            text="🚦 Todo el vehículo",
            variable=filter_mode_var,
            value='keep_all_vehicle',
            bg=COLORS['panel_bg'],
            font=FONTS['small']
        ).pack(anchor='w', padx=40)
        
        def do_export():
            dialog.destroy()
            
            output_file = filedialog.asksaveasfilename(
                title="Guardar audio filtrado completo",
                defaultextension=".wav",
                filetypes=[("WAV files", "*.wav")]
            )
            
            if not output_file:
                return
            
            try:
                success, message = self.separator.export_full_audio_filtered(
                    output_file,
                    filter_mode=filter_mode_var.get(),
                    target_class=target_class_var.get()
                )
                
                if success:
                    messagebox.showinfo("Éxito", f"✅ {message}")
                else:
                    messagebox.showerror("Error", message)
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")
        
        # Botones
        btn_frame = tk.Frame(dialog, bg=COLORS['panel_bg'])
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Exportar",
            font=FONTS['button'],
            bg=COLORS['success'],
            fg='white',
            command=do_export,
            padx=20,
            pady=5,
            relief='flat',
            bd=0
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancelar",
            font=FONTS['button'],
            bg=COLORS['danger'],
            fg='white',
            command=dialog.destroy,
            padx=20,
            pady=5,
            relief='flat',
            bd=0
        ).pack(side='left', padx=5)
    
    def export_metadata(self):
        """Exportar metadatos JSON"""
        segments_to_export = self.get_checked_segments()
        
        if not segments_to_export:
            messagebox.showwarning("Aviso", "No hay segmentos marcados")
            return
        
        output_file = filedialog.asksaveasfilename(
            title="Guardar metadatos",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if output_file:
            success, message = self.separator.export_metadata(
                segments_to_export,
                output_file
            )
            
            if success:
                messagebox.showinfo("Éxito", f"✅ {message}")
            else:
                messagebox.showerror("Error", message)
    
    def on_configure(self, event):
        """Guardar configuración al cambiar tamaño"""
        if event.widget == self.root:
            self.save_window_state()
    
    def save_window_state(self):
        """Guardar estado de la ventana"""
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
        """Manejar cierre de ventana"""
        self.save_window_state()
        self.root.destroy()
    
    def go_back(self):
        """Volver al menú principal"""
        if messagebox.askyesno("Confirmar", "¿Volver al menú principal?"):
            self.save_window_state()
            self.root.destroy()
            from gui_app import main
            main()
