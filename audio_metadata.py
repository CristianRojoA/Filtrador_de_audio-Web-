"""
📍 GESTOR DE METADATOS DE AUDIO
=================================
Maneja metadatos de grabaciones incluyendo:
- Ubicación geográfica (latitud, longitud, dirección)
- Fecha y hora de grabación
- Condiciones acústicas
- Información del dispositivo
"""

import json
import os
from datetime import datetime
from pathlib import Path


class AudioMetadata:
    """Gestiona metadatos de archivos de audio"""
    
    def __init__(self, audio_file_path):
        """
        Inicializar metadatos para un archivo de audio
        
        Args:
            audio_file_path: Ruta del archivo de audio
        """
        self.audio_file = Path(audio_file_path).name
        self.audio_path = str(audio_file_path)
        self.metadata = {
            "archivo": self.audio_file,
            "ruta_completa": self.audio_path,
            "fecha_analisis": datetime.now().isoformat(),
            "ubicacion": {
                "latitud": None,
                "longitud": None,
                "direccion": None,
                "ciudad": None,
                "pais": None,
                "notas_ubicacion": None
            },
            "grabacion": {
                "fecha_grabacion": None,
                "hora_grabacion": None,
                "duracion_segundos": None,
                "calidad_audio": None
            },
            "condiciones": {
                "clima": None,
                "temperatura": None,
                "hora_dia": None,  # mañana, tarde, noche
                "dia_semana": None,
                "trafico_estimado": None  # bajo, medio, alto
            },
            "analisis": {
                "clasificacion": None,
                "confianza": None,
                "detecciones_temporales": [],
                "recomendaciones": []
            },
            "dispositivo": {
                "tipo": None,  # celular, grabadora, microfono externo
                "marca_modelo": None,
                "sample_rate": None
            },
            "notas": None
        }
    
    def set_ubicacion(self, latitud=None, longitud=None, direccion=None, 
                      ciudad=None, pais=None, notas=None):
        """
        Establecer información de ubicación
        
        Args:
            latitud: Coordenada de latitud (ej: -33.4489)
            longitud: Coordenada de longitud (ej: -70.6693)
            direccion: Dirección completa (ej: "Av. Libertador 1234")
            ciudad: Ciudad (ej: "Santiago")
            pais: País (ej: "Chile")
            notas: Notas adicionales sobre la ubicación
        """
        self.metadata["ubicacion"]["latitud"] = latitud
        self.metadata["ubicacion"]["longitud"] = longitud
        self.metadata["ubicacion"]["direccion"] = direccion
        self.metadata["ubicacion"]["ciudad"] = ciudad
        self.metadata["ubicacion"]["pais"] = pais
        self.metadata["ubicacion"]["notas_ubicacion"] = notas
    
    def set_grabacion_info(self, fecha=None, hora=None, duracion=None, calidad=None):
        """
        Establecer información de la grabación
        
        Args:
            fecha: Fecha de grabación (formato: "YYYY-MM-DD")
            hora: Hora de grabación (formato: "HH:MM")
            duracion: Duración en segundos
            calidad: Calidad del audio (baja/media/alta)
        """
        self.metadata["grabacion"]["fecha_grabacion"] = fecha
        self.metadata["grabacion"]["hora_grabacion"] = hora
        self.metadata["grabacion"]["duracion_segundos"] = duracion
        self.metadata["grabacion"]["calidad_audio"] = calidad
    
    def set_condiciones(self, clima=None, temperatura=None, hora_dia=None, 
                        dia_semana=None, trafico=None):
        """
        Establecer condiciones ambientales
        
        Args:
            clima: Condición climática (soleado/nublado/lluvia/etc)
            temperatura: Temperatura en °C
            hora_dia: Momento del día (mañana/tarde/noche)
            dia_semana: Día de la semana
            trafico: Nivel de tráfico (bajo/medio/alto)
        """
        self.metadata["condiciones"]["clima"] = clima
        self.metadata["condiciones"]["temperatura"] = temperatura
        self.metadata["condiciones"]["hora_dia"] = hora_dia
        self.metadata["condiciones"]["dia_semana"] = dia_semana
        self.metadata["condiciones"]["trafico_estimado"] = trafico
    
    def set_analisis(self, clasificacion=None, confianza=None, 
                     detecciones=None, recomendaciones=None):
        """
        Establecer resultados del análisis
        
        Args:
            clasificacion: Clase predicha
            confianza: Nivel de confianza (0-1)
            detecciones: Lista de detecciones temporales
            recomendaciones: Lista de recomendaciones
        """
        self.metadata["analisis"]["clasificacion"] = clasificacion
        self.metadata["analisis"]["confianza"] = confianza
        if detecciones:
            self.metadata["analisis"]["detecciones_temporales"] = detecciones
        if recomendaciones:
            self.metadata["analisis"]["recomendaciones"] = recomendaciones
    
    def set_dispositivo(self, tipo=None, marca_modelo=None, sample_rate=None):
        """
        Establecer información del dispositivo de grabación
        
        Args:
            tipo: Tipo de dispositivo
            marca_modelo: Marca y modelo
            sample_rate: Tasa de muestreo
        """
        self.metadata["dispositivo"]["tipo"] = tipo
        self.metadata["dispositivo"]["marca_modelo"] = marca_modelo
        self.metadata["dispositivo"]["sample_rate"] = sample_rate
    
    def set_notas(self, notas):
        """Agregar notas adicionales"""
        self.metadata["notas"] = notas
    
    def get_metadata(self):
        """Obtener diccionario de metadatos"""
        return self.metadata
    
    def save_to_file(self, output_path=None):
        """
        Guardar metadatos a archivo JSON
        
        Args:
            output_path: Ruta del archivo de salida (opcional)
        """
        if output_path is None:
            # Crear carpeta datos_exportados si no existe
            export_dir = Path("datos_exportados")
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear archivo en datos_exportados con mismo nombre que el audio
            audio_name = Path(self.audio_path).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = export_dir / f"{audio_name}_metadata_{timestamp}.json"
        else:
            output_path = Path(output_path)
            # Crear directorio si no existe
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    @staticmethod
    def load_from_file(json_path):
        """
        Cargar metadatos desde archivo JSON
        
        Args:
            json_path: Ruta del archivo JSON
            
        Returns:
            dict: Diccionario de metadatos
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_location_url(self):
        """
        Obtener URL de Google Maps con la ubicación
        
        Returns:
            str: URL de Google Maps o None
        """
        lat = self.metadata["ubicacion"]["latitud"]
        lon = self.metadata["ubicacion"]["longitud"]
        
        if lat is not None and lon is not None:
            return f"https://www.google.com/maps?q={lat},{lon}"
        return None
    
    def generate_summary(self):
        """
        Generar resumen legible de los metadatos
        
        Returns:
            str: Resumen formateado
        """
        summary = []
        summary.append("📍 METADATOS DE GRABACIÓN")
        summary.append("=" * 50)
        summary.append(f"\n📁 Archivo: {self.audio_file}")
        
        # Ubicación
        if self.metadata["ubicacion"]["direccion"]:
            summary.append(f"\n📍 UBICACIÓN:")
            summary.append(f"   • Dirección: {self.metadata['ubicacion']['direccion']}")
            if self.metadata["ubicacion"]["ciudad"]:
                summary.append(f"   • Ciudad: {self.metadata['ubicacion']['ciudad']}")
            if self.metadata["ubicacion"]["pais"]:
                summary.append(f"   • País: {self.metadata['ubicacion']['pais']}")
            if self.metadata["ubicacion"]["notas_ubicacion"]:
                summary.append(f"   • Notas: {self.metadata['ubicacion']['notas_ubicacion']}")
        
        # Grabación
        if self.metadata["grabacion"]["fecha_grabacion"]:
            summary.append(f"\n🎙️  GRABACIÓN:")
            summary.append(f"   • Fecha: {self.metadata['grabacion']['fecha_grabacion']}")
            if self.metadata["grabacion"]["hora_grabacion"]:
                summary.append(f"   • Hora: {self.metadata['grabacion']['hora_grabacion']}")
            if self.metadata["grabacion"]["duracion_segundos"]:
                summary.append(f"   • Duración: {self.metadata['grabacion']['duracion_segundos']:.1f}s")
        
        # Condiciones
        if self.metadata["condiciones"]["clima"]:
            summary.append(f"\n🌤️  CONDICIONES:")
            summary.append(f"   • Clima: {self.metadata['condiciones']['clima']}")
            if self.metadata["condiciones"]["dia_semana"]:
                summary.append(f"   • Día: {self.metadata['condiciones']['dia_semana']}")
        
        # Dispositivo
        if self.metadata["dispositivo"]["tipo"]:
            summary.append(f"\n📱 DISPOSITIVO:")
            summary.append(f"   • Tipo: {self.metadata['dispositivo']['tipo']}")
            if self.metadata["dispositivo"]["marca_modelo"]:
                summary.append(f"   • Marca/Modelo: {self.metadata['dispositivo']['marca_modelo']}")
        
        # Análisis
        if self.metadata["analisis"]["clasificacion"]:
            summary.append(f"\n🔍 ANÁLISIS:")
            summary.append(f"   • Clasificación: {self.metadata['analisis']['clasificacion']}")
            if self.metadata["analisis"]["confianza"]:
                summary.append(f"   • Confianza: {self.metadata['analisis']['confianza']:.2%}")
        
        # Notas adicionales
        if self.metadata.get("notas"):
            summary.append(f"\n📝 NOTAS:")
            summary.append(f"   {self.metadata['notas']}")
        
        return "\n".join(summary)


class MetadataManager:
    """Gestiona múltiples metadatos de audio"""
    
    def __init__(self, output_dir="metadata"):
        """
        Inicializar gestor de metadatos
        
        Args:
            output_dir: Directorio donde guardar metadatos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.metadata_list = []
    
    def add_metadata(self, audio_metadata):
        """Agregar metadatos a la lista"""
        self.metadata_list.append(audio_metadata.get_metadata())
    
    def export_all(self, filename="metadata_coleccion.json"):
        """
        Exportar todos los metadatos a un archivo
        
        Args:
            filename: Nombre del archivo de salida
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata_list, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def export_csv(self, filename="metadata_coleccion.csv"):
        """
        Exportar metadatos a CSV para análisis
        
        Args:
            filename: Nombre del archivo CSV
        """
        import csv
        
        output_path = self.output_dir / filename
        
        if not self.metadata_list:
            return None
        
        # Aplanar metadatos para CSV
        flattened = []
        for meta in self.metadata_list:
            flat = {
                "archivo": meta["archivo"],
                "fecha_analisis": meta["fecha_analisis"],
                "latitud": meta["ubicacion"]["latitud"],
                "longitud": meta["ubicacion"]["longitud"],
                "direccion": meta["ubicacion"]["direccion"],
                "ciudad": meta["ubicacion"]["ciudad"],
                "pais": meta["ubicacion"]["pais"],
                "fecha_grabacion": meta["grabacion"]["fecha_grabacion"],
                "hora_grabacion": meta["grabacion"]["hora_grabacion"],
                "clima": meta["condiciones"]["clima"],
                "trafico": meta["condiciones"]["trafico_estimado"],
                "clasificacion": meta["analisis"]["clasificacion"],
                "confianza": meta["analisis"]["confianza"]
            }
            flattened.append(flat)
        
        # Escribir CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=flattened[0].keys())
            writer.writeheader()
            writer.writerows(flattened)
        
        return str(output_path)


# Ejemplo de uso
if __name__ == "__main__":
    # Crear metadatos para un audio
    metadata = AudioMetadata("ejemplo_trafico.wav")
    
    # Establecer ubicación
    metadata.set_ubicacion(
        latitud=-33.4489,
        longitud=-70.6693,
        direccion="Av. Libertador Bernardo O'Higgins 1234",
        ciudad="Santiago",
        pais="Chile",
        notas="Esquina con alta congestión vehicular"
    )
    
    # Establecer info de grabación
    metadata.set_grabacion_info(
        fecha="2025-11-18",
        hora="14:30",
        duracion=30.5,
        calidad="alta"
    )
    
    # Establecer condiciones
    metadata.set_condiciones(
        clima="soleado",
        temperatura=28,
        hora_dia="tarde",
        dia_semana="lunes",
        trafico="alto"
    )
    
    # Establecer resultados
    metadata.set_analisis(
        clasificacion="Mucho_Trafico",
        confianza=0.92,
        recomendaciones=["Considerar instalación de semáforo"]
    )
    
    # Mostrar resumen
    print(metadata.generate_summary())
    
    # Guardar
    saved_path = metadata.save_to_file()
    print(f"\n✅ Metadatos guardados en: {saved_path}")
