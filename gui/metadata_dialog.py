"""
📍 VENTANA DE METADATOS
========================
Interfaz para capturar metadatos de ubicación y contexto de grabaciones
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from .styles import COLORS, FONTS


class MetadataDialog:
    """Diálogo para capturar metadatos de ubicación"""
    
    def __init__(self, parent, audio_file):
        """
        Crear diálogo de metadatos
        
        Args:
            parent: Ventana padre
            audio_file: Nombre del archivo de audio
        """
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📍 Metadatos de Ubicación")
        self.dialog.geometry("500x700")
        self.dialog.configure(bg=COLORS['bg'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"500x700+{x}+{y}")
        
        self.create_widgets(audio_file)
    
    def create_widgets(self, audio_file):
        """Crear widgets del diálogo"""
        
        # Frame principal con scroll
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Título
        title = tk.Label(
            scrollable_frame,
            text=f"📁 {audio_file}",
            font=FONTS['title'],
            bg='white',
            fg=COLORS['primary']
        )
        title.pack(pady=(0, 20))
        
        # --- UBICACIÓN ---
        self.create_section(scrollable_frame, "📍 UBICACIÓN")
        
        self.dir_entry = self.create_entry(
            scrollable_frame, 
            "Dirección:", 
            placeholder="Ej: Av. Libertador 1234"
        )
        
        self.city_entry = self.create_entry(
            scrollable_frame, 
            "Ciudad:", 
            placeholder="Ej: Santiago"
        )
        
        self.country_entry = self.create_entry(
            scrollable_frame, 
            "País:", 
            placeholder="Ej: Chile"
        )
        
        self.loc_notes_entry = self.create_text(
            scrollable_frame,
            "Notas de ubicación:",
            height=3
        )
        
        # --- GRABACIÓN ---
        self.create_section(scrollable_frame, "🎙️ INFORMACIÓN DE GRABACIÓN")
        
        # Fecha y hora por defecto: ahora
        now = datetime.now()
        
        self.date_entry = self.create_entry(
            scrollable_frame,
            "Fecha (YYYY-MM-DD):",
            default=now.strftime("%Y-%m-%d")
        )
        
        self.time_entry = self.create_entry(
            scrollable_frame,
            "Hora (HH:MM):",
            default=now.strftime("%H:%M")
        )
        
        # --- CONDICIONES ---
        self.create_section(scrollable_frame, "🌤️ CONDICIONES AMBIENTALES")
        
        self.weather_var = tk.StringVar(value="soleado")
        self.create_radio_group(
            scrollable_frame,
            "Clima:",
            self.weather_var,
            [("Soleado", "soleado"), ("Nublado", "nublado"), 
             ("Lluvia", "lluvia"), ("Viento", "viento")]
        )
        
        self.day_of_week_entry = self.create_entry(
            scrollable_frame,
            "Día de la semana:",
            placeholder="Ej: Lunes"
        )
        
        # --- DISPOSITIVO ---
        self.create_section(scrollable_frame, "📱 DISPOSITIVO DE GRABACIÓN")
        
        self.device_type_var = tk.StringVar(value="celular")
        self.create_radio_group(
            scrollable_frame,
            "Tipo:",
            self.device_type_var,
            [("Celular", "celular"), ("Grabadora", "grabadora"), 
             ("Micrófono", "microfono")]
        )
        
        self.device_model_entry = self.create_entry(
            scrollable_frame,
            "Marca/Modelo:",
            placeholder="Ej: iPhone 13 / Samsung Galaxy S21"
        )
        
        # --- NOTAS ---
        self.create_section(scrollable_frame, "📝 NOTAS ADICIONALES")
        
        self.notes_entry = self.create_text(
            scrollable_frame,
            "Observaciones:",
            height=4
        )
        
        # Botones
        btn_frame = tk.Frame(self.dialog, bg=COLORS['bg'])
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        btn_cancel = tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=self.cancel,
            font=FONTS['button'],
            bg='#e74c3c',
            fg='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        btn_cancel.pack(side='left', padx=(0, 10))
        
        btn_save = tk.Button(
            btn_frame,
            text="✅ Guardar",
            command=self.save,
            font=FONTS['button'],
            bg=COLORS['success'],
            fg='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        btn_save.pack(side='right')
        
        # Binding de scroll con rueda del mouse
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
    
    def create_section(self, parent, title):
        """Crear título de sección"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=(15, 10))
        
        label = tk.Label(
            frame,
            text=title,
            font=FONTS['subtitle'],
            bg='white',
            fg=COLORS['primary'],
            anchor='w'
        )
        label.pack(fill='x')
        
        separator = tk.Frame(frame, bg=COLORS['primary'], height=2)
        separator.pack(fill='x', pady=(5, 0))
    
    def create_entry(self, parent, label_text, placeholder="", default=""):
        """Crear campo de entrada con etiqueta"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=5)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=FONTS['body'],
            bg='white',
            anchor='w'
        )
        label.pack(fill='x')
        
        entry = tk.Entry(
            frame,
            font=FONTS['body'],
            relief='solid',
            bd=1
        )
        entry.pack(fill='x', pady=(2, 0))
        
        if default:
            entry.insert(0, default)
        elif placeholder:
            entry.insert(0, placeholder)
            entry.config(fg='gray')
            
            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg='black')
            
            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg='gray')
            
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
        
        return entry
    
    def create_text(self, parent, label_text, height=3):
        """Crear área de texto con etiqueta"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=5)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=FONTS['body'],
            bg='white',
            anchor='w'
        )
        label.pack(fill='x')
        
        text = tk.Text(
            frame,
            font=FONTS['body'],
            relief='solid',
            bd=1,
            height=height,
            wrap='word'
        )
        text.pack(fill='x', pady=(2, 0))
        
        return text
    
    def create_radio_group(self, parent, label_text, variable, options):
        """Crear grupo de radio buttons"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=5)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=FONTS['body'],
            bg='white',
            anchor='w'
        )
        label.pack(fill='x')
        
        radio_frame = tk.Frame(frame, bg='white')
        radio_frame.pack(fill='x', pady=(2, 0))
        
        for text, value in options:
            rb = tk.Radiobutton(
                radio_frame,
                text=text,
                variable=variable,
                value=value,
                font=FONTS['body'],
                bg='white',
                activebackground='white',
                cursor='hand2'
            )
            rb.pack(side='left', padx=(0, 15))
    
    def get_entry_value(self, entry, placeholder=""):
        """Obtener valor de entry, ignorando placeholder"""
        value = entry.get().strip()
        if value == placeholder or value == "":
            return None
        return value
    
    def get_text_value(self, text_widget):
        """Obtener valor de text widget"""
        value = text_widget.get("1.0", tk.END).strip()
        return value if value else None
    
    def save(self):
        """Guardar metadatos"""
        self.result = {
            "ubicacion": {
                "direccion": self.get_entry_value(self.dir_entry, "Ej: Av. Libertador 1234"),
                "ciudad": self.get_entry_value(self.city_entry, "Ej: Santiago"),
                "pais": self.get_entry_value(self.country_entry, "Ej: Chile"),
                "notas": self.get_text_value(self.loc_notes_entry)
            },
            "grabacion": {
                "fecha": self.date_entry.get().strip(),
                "hora": self.time_entry.get().strip()
            },
            "condiciones": {
                "clima": self.weather_var.get(),
                "dia_semana": self.get_entry_value(self.day_of_week_entry, "Ej: Lunes")
            },
            "dispositivo": {
                "tipo": self.device_type_var.get(),
                "marca_modelo": self.get_entry_value(self.device_model_entry, 
                                                     "Ej: iPhone 13 / Samsung Galaxy S21")
            },
            "notas": self.get_text_value(self.notes_entry)
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancelar y cerrar"""
        self.result = None
        self.dialog.destroy()
    
    def parse_float(self, value):
        """Convertir string a float, retornar None si falla"""
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            return None
    
    def show(self):
        """Mostrar diálogo y esperar resultado"""
        self.dialog.wait_window()
        return self.result
