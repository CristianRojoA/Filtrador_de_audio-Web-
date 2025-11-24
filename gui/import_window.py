"""
📥 VENTANA DE IMPORTACIÓN
==========================
Ventana para importar y visualizar archivos JSON exportados
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
from pathlib import Path
from .styles import COLORS, FONTS


class ImportWindow:
    """Ventana para importar y visualizar exportaciones"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📥 Importar Análisis")
        self.root.geometry("900x650")
        self.root.configure(bg=COLORS['bg'])
        
        # Datos cargados
        self.current_file = None
        self.current_data = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear interfaz"""
        
        # Header
        header = tk.Frame(self.root, bg=COLORS['primary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="📥 Importar y Visualizar Análisis",
            font=FONTS['title'],
            bg=COLORS['primary'],
            fg='white'
        )
        title.pack(pady=25)
        
        # Contenedor principal
        main_container = tk.Frame(self.root, bg=COLORS['bg'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Panel superior - Botones de acción
        top_panel = tk.Frame(main_container, bg='white', relief='solid', bd=1)
        top_panel.pack(fill='x', pady=(0, 10))
        
        btn_frame = tk.Frame(top_panel, bg='white')
        btn_frame.pack(padx=20, pady=15)
        
        # Botón cargar JSON de detecciones
        tk.Button(
            btn_frame,
            text="📄 Cargar Detecciones",
            font=FONTS['button'],
            bg=COLORS['primary'],
            fg='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.load_detections
        ).pack(side='left', padx=5)
        
        # Botón cargar JSON de metadatos
        tk.Button(
            btn_frame,
            text="📍 Cargar Metadatos",
            font=FONTS['button'],
            bg=COLORS['success'],
            fg='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.load_metadata
        ).pack(side='left', padx=5)
        
        # Botón explorar carpeta
        tk.Button(
            btn_frame,
            text="📂 Explorar Exportados",
            font=FONTS['button'],
            bg=COLORS['warning'],
            fg='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.browse_export_folder
        ).pack(side='left', padx=5)
        
        # Botón limpiar
        tk.Button(
            btn_frame,
            text="🗑️ Limpiar",
            font=FONTS['button'],
            bg=COLORS['gray'],
            fg='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.clear_display
        ).pack(side='left', padx=5)
        
        # Panel de información del archivo
        info_panel = tk.Frame(main_container, bg='white', relief='solid', bd=1)
        info_panel.pack(fill='x', pady=(0, 10))
        
        info_inner = tk.Frame(info_panel, bg='white')
        info_inner.pack(padx=20, pady=15)
        
        tk.Label(
            info_inner,
            text="Archivo cargado:",
            font=FONTS['body'],
            bg='white',
            fg=COLORS['dark']
        ).pack(side='left', padx=(0, 10))
        
        self.file_label = tk.Label(
            info_inner,
            text="Ninguno",
            font=FONTS['body'],
            bg='white',
            fg=COLORS['gray']
        )
        self.file_label.pack(side='left')
        
        # Panel de visualización
        display_panel = tk.Frame(main_container, bg='white', relief='solid', bd=1)
        display_panel.pack(fill='both', expand=True)
        
        # Notebook para tabs
        self.notebook = ttk.Notebook(display_panel)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Vista legible
        readable_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(readable_frame, text="📄 Vista Legible")
        
        self.readable_text = scrolledtext.ScrolledText(
            readable_frame,
            font=FONTS['body'],
            wrap='word',
            bg='white',
            relief='flat',
            padx=15,
            pady=15
        )
        self.readable_text.pack(fill='both', expand=True)
        
        # Tab 2: JSON Raw
        json_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(json_frame, text="🔧 JSON Raw")
        
        self.json_text = scrolledtext.ScrolledText(
            json_frame,
            font=FONTS['console'],
            wrap='word',
            bg='#f8f9fa',
            relief='flat',
            padx=15,
            pady=15
        )
        self.json_text.pack(fill='both', expand=True)
        
        # Tab 3: Tabla de detecciones (si es archivo de detecciones)
        table_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(table_frame, text="📊 Tabla de Detecciones")
        
        # Crear Treeview para tabla
        columns = ('Tiempo', 'Clase', 'Confianza', 'Duración')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Definir encabezados
        self.tree.heading('Tiempo', text='Tiempo Inicio')
        self.tree.heading('Clase', text='Clase Detectada')
        self.tree.heading('Confianza', text='Confianza')
        self.tree.heading('Duración', text='Duración (s)')
        
        # Definir anchos
        self.tree.column('Tiempo', width=120)
        self.tree.column('Clase', width=200)
        self.tree.column('Confianza', width=100)
        self.tree.column('Duración', width=100)
        
        # Scrollbar para tabla
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side='right', fill='y', pady=10, padx=(0, 10))
        
        # Botón volver
        tk.Button(
            main_container,
            text="⬅️ Volver al Menú",
            font=FONTS['button'],
            bg=COLORS['gray'],
            fg='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.go_back
        ).pack(pady=(10, 0))
    
    def load_detections(self):
        """Cargar archivo de detecciones JSON"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de detecciones",
            initialdir="datos_exportados",
            filetypes=[
                ("Archivos JSON", "*.json"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Verificar que sea un archivo de detecciones
                if 'detecciones_agrupadas' in data:
                    self.current_file = filename
                    self.current_data = data
                    self.display_detections(data)
                    self.file_label.config(
                        text=os.path.basename(filename),
                        fg=COLORS['success']
                    )
                else:
                    messagebox.showwarning(
                        "Advertencia",
                        "Este archivo no parece ser un archivo de detecciones válido."
                    )
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar archivo:\n{str(e)}")
    
    def load_metadata(self):
        """Cargar archivo de metadatos JSON"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de metadatos",
            initialdir="datos_exportados",
            filetypes=[
                ("Archivos JSON", "*.json"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Verificar que sea un archivo de metadatos
                if 'ubicacion' in data or 'metadata' in str(filename).lower():
                    self.current_file = filename
                    self.current_data = data
                    self.display_metadata(data)
                    self.file_label.config(
                        text=os.path.basename(filename),
                        fg=COLORS['success']
                    )
                else:
                    messagebox.showwarning(
                        "Advertencia",
                        "Este archivo no parece ser un archivo de metadatos válido."
                    )
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar archivo:\n{str(e)}")
    
    def display_detections(self, data):
        """Mostrar datos de detecciones"""
        # Limpiar displays
        self.readable_text.delete('1.0', tk.END)
        self.json_text.delete('1.0', tk.END)
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Vista legible
        readable = []
        readable.append("📊 ANÁLISIS DE AUDIO")
        readable.append("=" * 60)
        readable.append(f"\n📁 Archivo: {data.get('archivo', 'N/A')}")
        readable.append(f"⏱️ Duración total: {data.get('duracion_total', 0):.2f} segundos")
        readable.append(f"📅 Fecha de análisis: {data.get('fecha_analisis', 'N/A')}")
        
        detecciones = data.get('detecciones_agrupadas', [])
        readable.append(f"\n🔍 Total de detecciones: {len(detecciones)}")
        readable.append("\n" + "=" * 60)
        readable.append("\nDETECCIONES:\n")
        
        for i, det in enumerate(detecciones, 1):
            readable.append(f"\n{i}. {det.get('clase', 'N/A')}")
            readable.append(f"   • Tiempo: {det.get('tiempo_inicio', 0):.2f}s - {det.get('tiempo_fin', 0):.2f}s")
            readable.append(f"   • Duración: {det.get('duracion', 0):.2f}s")
            readable.append(f"   • Confianza: {det.get('confianza', 0):.2%}")
            
            # Agregar a tabla
            self.tree.insert('', 'end', values=(
                f"{det.get('tiempo_inicio', 0):.2f}s",
                det.get('clase', 'N/A'),
                f"{det.get('confianza', 0):.2%}",
                f"{det.get('duracion', 0):.2f}s"
            ))
        
        self.readable_text.insert('1.0', '\n'.join(readable))
        
        # JSON Raw
        self.json_text.insert('1.0', json.dumps(data, indent=2, ensure_ascii=False))
    
    def display_metadata(self, data):
        """Mostrar datos de metadatos"""
        # Limpiar displays
        self.readable_text.delete('1.0', tk.END)
        self.json_text.delete('1.0', tk.END)
        
        # Limpiar tabla (no aplica para metadatos)
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Vista legible
        readable = []
        readable.append("📍 METADATOS DE GRABACIÓN")
        readable.append("=" * 60)
        readable.append(f"\n📁 Archivo: {data.get('archivo', 'N/A')}")
        readable.append(f"📅 Fecha de análisis: {data.get('fecha_analisis', 'N/A')}")
        
        # Ubicación
        if 'ubicacion' in data and any(data['ubicacion'].values()):
            readable.append("\n📍 UBICACIÓN:")
            ubi = data['ubicacion']
            if ubi.get('direccion'):
                readable.append(f"   • Dirección: {ubi['direccion']}")
            if ubi.get('ciudad'):
                readable.append(f"   • Ciudad: {ubi['ciudad']}")
            if ubi.get('pais'):
                readable.append(f"   • País: {ubi['pais']}")
            if ubi.get('notas_ubicacion'):
                readable.append(f"   • Notas: {ubi['notas_ubicacion']}")
        
        # Grabación
        if 'grabacion' in data:
            readable.append("\n🎙️  GRABACIÓN:")
            grab = data['grabacion']
            if grab.get('fecha_grabacion'):
                readable.append(f"   • Fecha: {grab['fecha_grabacion']}")
            if grab.get('hora_grabacion'):
                readable.append(f"   • Hora: {grab['hora_grabacion']}")
            if grab.get('duracion_segundos'):
                readable.append(f"   • Duración: {grab['duracion_segundos']:.1f}s")
        
        # Condiciones
        if 'condiciones' in data:
            readable.append("\n🌤️  CONDICIONES:")
            cond = data['condiciones']
            if cond.get('clima'):
                readable.append(f"   • Clima: {cond['clima']}")
            if cond.get('dia_semana'):
                readable.append(f"   • Día: {cond['dia_semana']}")
        
        # Análisis
        if 'analisis' in data:
            readable.append("\n🔍 ANÁLISIS:")
            anal = data['analisis']
            if anal.get('clasificacion'):
                readable.append(f"   • Clasificación: {anal['clasificacion']}")
            if anal.get('confianza'):
                readable.append(f"   • Confianza: {anal['confianza']:.2%}")
            if anal.get('recomendaciones'):
                readable.append(f"   • Recomendaciones:")
                for rec in anal['recomendaciones']:
                    readable.append(f"     - {rec}")
        
        # Dispositivo
        if 'dispositivo' in data:
            readable.append("\n📱 DISPOSITIVO:")
            disp = data['dispositivo']
            if disp.get('tipo'):
                readable.append(f"   • Tipo: {disp['tipo']}")
            if disp.get('marca_modelo'):
                readable.append(f"   • Marca/Modelo: {disp['marca_modelo']}")
        
        # Notas
        if data.get('notas'):
            readable.append(f"\n📝 NOTAS:\n{data['notas']}")
        
        self.readable_text.insert('1.0', '\n'.join(readable))
        
        # JSON Raw
        self.json_text.insert('1.0', json.dumps(data, indent=2, ensure_ascii=False))
    
    def browse_export_folder(self):
        """Abrir explorador en carpeta de exportados"""
        export_dir = "datos_exportados"
        if not os.path.exists(export_dir):
            messagebox.showinfo("Información", "La carpeta 'datos_exportados' aún no existe.\nSe creará cuando exportes algo.")
            os.makedirs(export_dir, exist_ok=True)
        
        # Abrir explorador de archivos
        os.startfile(os.path.abspath(export_dir))
    
    def clear_display(self):
        """Limpiar visualización"""
        self.readable_text.delete('1.0', tk.END)
        self.json_text.delete('1.0', tk.END)
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.file_label.config(text="Ninguno", fg=COLORS['gray'])
        self.current_file = None
        self.current_data = None
    
    def go_back(self):
        """Volver al menú principal"""
        self.root.destroy()
        # Reimportar para evitar circular import
        from gui_app import main
        main()
