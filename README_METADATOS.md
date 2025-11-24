# 📍 Sistema de Metadatos Geográficos

## 📋 Descripción

Sistema completo para registrar, gestionar y exportar **metadatos de ubicación geográfica** asociados a grabaciones de audio analizadas. Ideal para estudios de acústica urbana, análisis de tráfico y documentación de condiciones sonoras.

---

## ✨ Características

### 🗺️ Información Geográfica
- **Coordenadas GPS** (latitud, longitud)
- **Dirección completa**
- **Ciudad y país**
- **Notas de ubicación específicas**
- **Generación automática de URLs de Google Maps**

### 🎙️ Información de Grabación
- Fecha y hora de grabación
- Duración del audio
- Calidad de la grabación
- Sample rate

### 🌤️ Condiciones Ambientales
- Condiciones climáticas
- Temperatura
- Momento del día (mañana/tarde/noche)
- Día de la semana
- Nivel de tráfico estimado

### 🔍 Resultados del Análisis
- Clasificación predicha
- Nivel de confianza
- Detecciones temporales completas
- Recomendaciones generadas

### 📱 Información del Dispositivo
- Tipo de dispositivo (celular/grabadora/micrófono)
- Marca y modelo
- Características técnicas

---

## 🚀 Uso en la Aplicación

### 1️⃣ Desde la Interfaz Gráfica

1. **Cargar un audio** en la ventana principal
2. **Realizar análisis temporal**
3. **Exportar resultados** (botón "💾 Exportar JSON")
4. Se te preguntará: **"¿Deseas agregar información de ubicación?"**
5. Si aceptas, se abre el **diálogo de metadatos**
6. Llena los campos deseados (todos son opcionales)
7. **Guardar** → Se crean 2 archivos:
   - `resultados.json` (análisis)
   - `audio.metadata.json` (metadatos)

### 2️⃣ Desde Código Python

```python
from audio_metadata import AudioMetadata

# Crear metadatos para un archivo
metadata = AudioMetadata("mi_audio.wav")

# Agregar ubicación
metadata.set_ubicacion(
    latitud=-33.4489,
    longitud=-70.6693,
    direccion="Av. Libertador 1234",
    ciudad="Santiago",
    pais="Chile",
    notas="Esquina con alto tráfico"
)

# Agregar condiciones
metadata.set_condiciones(
    clima="soleado",
    temperatura=25,
    hora_dia="tarde",
    trafico="alto"
)

# Agregar resultados del análisis
metadata.set_analisis(
    clasificacion="Mucho_Trafico",
    confianza=0.92,
    recomendaciones=["Instalar semáforo"]
)

# Guardar
metadata.save_to_file()

# Ver resumen
print(metadata.generate_summary())

# Obtener URL de Google Maps
print(metadata.get_location_url())
```

---

## 📂 Estructura de Archivos

### Archivo de Metadatos (`.metadata.json`)

```json
{
  "archivo": "trafico_avenida.wav",
  "ruta_completa": "C:/audios/trafico_avenida.wav",
  "fecha_analisis": "2025-11-18T14:30:00",
  "ubicacion": {
    "latitud": -33.4489,
    "longitud": -70.6693,
    "direccion": "Av. Libertador 1234",
    "ciudad": "Santiago",
    "pais": "Chile",
    "notas_ubicacion": "Intersección concurrida"
  },
  "grabacion": {
    "fecha_grabacion": "2025-11-18",
    "hora_grabacion": "14:30",
    "duracion_segundos": 30.5,
    "calidad_audio": "alta"
  },
  "condiciones": {
    "clima": "soleado",
    "temperatura": 28,
    "hora_dia": "tarde",
    "dia_semana": "lunes",
    "trafico_estimado": "alto"
  },
  "analisis": {
    "clasificacion": "Mucho_Trafico",
    "confianza": 0.92,
    "detecciones_temporales": [
      {
        "tiempo": 0.0,
        "clase": "Mucho_Trafico",
        "confianza": 0.95
      }
    ],
    "recomendaciones": [
      "Considerar instalación de semáforo"
    ]
  },
  "dispositivo": {
    "tipo": "celular",
    "marca_modelo": "Samsung Galaxy S21",
    "sample_rate": 44100
  },
  "notas": "Observaciones adicionales del analista"
}
```

---

## 🎯 Casos de Uso

### 📊 **1. Estudios de Tráfico Urbano**

Documenta múltiples puntos de la ciudad con metadatos completos:

```python
from audio_metadata import MetadataManager

manager = MetadataManager(output_dir="estudio_trafico_2025")

# Agregar múltiples ubicaciones
for punto in puntos_criticos:
    meta = AudioMetadata(punto["audio"])
    meta.set_ubicacion(...)
    meta.set_analisis(...)
    manager.add_metadata(meta)

# Exportar todo
manager.export_all("estudio_completo.json")
manager.export_csv("analisis_estadistico.csv")
```

### 🏙️ **2. Mapas de Calor Acústico**

Con las coordenadas GPS puedes crear visualizaciones:

```python
import pandas as pd
import folium

# Cargar metadatos exportados
df = pd.read_csv("metadata_coleccion.csv")

# Crear mapa
mapa = folium.Map(location=[-33.45, -70.66])

for idx, row in df.iterrows():
    folium.CircleMarker(
        location=[row['latitud'], row['longitud']],
        radius=10,
        popup=f"{row['clasificacion']} ({row['confianza']:.0%})",
        color='red' if 'Mucho' in row['clasificacion'] else 'green'
    ).add_to(mapa)

mapa.save("mapa_trafico.html")
```

### 📑 **3. Reportes para Autoridades**

Genera documentación formal con ubicaciones exactas:

```python
metadata = AudioMetadata("punto_critico.wav")
metadata.set_ubicacion(...)
metadata.set_analisis(
    clasificacion="Mucho_Trafico",
    recomendaciones=[
        "Cumple Manual de Señalización (Pág. 166)",
        "Requiere semáforo urgente"
    ]
)

# Generar resumen legible
print(metadata.generate_summary())

# Incluir link al mapa
print(f"Ubicación: {metadata.get_location_url()}")
```

---

## 🛠️ Funciones Principales

### `AudioMetadata(audio_file_path)`

Crea un objeto de metadatos para un archivo de audio.

**Métodos:**

| Método | Descripción |
|--------|-------------|
| `set_ubicacion()` | Establece coordenadas y dirección |
| `set_grabacion_info()` | Info de fecha, hora, duración |
| `set_condiciones()` | Clima, temperatura, tráfico |
| `set_analisis()` | Resultados de clasificación |
| `set_dispositivo()` | Tipo y modelo de grabadora |
| `set_notas()` | Observaciones adicionales |
| `save_to_file()` | Guarda en archivo JSON |
| `generate_summary()` | Crea resumen legible |
| `get_location_url()` | URL de Google Maps |

### `MetadataManager(output_dir)`

Gestiona múltiples metadatos.

**Métodos:**

| Método | Descripción |
|--------|-------------|
| `add_metadata()` | Agrega metadatos a la colección |
| `export_all()` | Exporta todo a JSON |
| `export_csv()` | Exporta a CSV para análisis |

---

## 📝 Ejemplos Prácticos

Ejecuta el archivo de ejemplos:

```bash
python ejemplos_metadatos.py
```

Esto muestra:
- ✅ Metadatos completos
- ✅ Metadatos mínimos
- ✅ Gestión de colecciones
- ✅ Cargar metadatos existentes
- ✅ Análisis de tráfico con metadatos

---

## 🌍 Obtener Coordenadas GPS

### **Opción 1: Google Maps**
1. Abre Google Maps
2. Haz clic derecho en la ubicación
3. Copia las coordenadas (formato: `-33.4489, -70.6693`)

### **Opción 2: GPS del Celular**
- **Android**: Usa apps como "GPS Status & Toolbox"
- **iPhone**: Compass app muestra coordenadas

### **Opción 3: Desde Dirección**
Usa la API de geocodificación (requiere API key):

```python
import googlemaps

gmaps = googlemaps.Client(key='TU_API_KEY')
resultado = gmaps.geocode('Av. Libertador 1234, Santiago')
lat = resultado[0]['geometry']['location']['lat']
lon = resultado[0]['geometry']['location']['lng']
```

---

## 📊 Exportación de Datos

### **JSON** (Metadatos completos)
- Incluye toda la información
- Ideal para backup y procesamiento

### **CSV** (Análisis estadístico)
- Compatible con Excel, Python, R
- Ideal para gráficos y mapas de calor

---

## 💡 Tips y Mejores Prácticas

### ✅ **Recomendaciones**

1. **Siempre registra la ubicación** para análisis posteriores
2. **Anota la hora del día** (afecta patrones de tráfico)
3. **Documenta el clima** (lluvia afecta niveles de ruido)
4. **Usa coordenadas GPS precisas** (Google Maps es muy exacto)
5. **Agrega notas contextuales** (eventos especiales, obras, etc.)

### ⚠️ **Consideraciones**

- Las coordenadas GPS son **opcionales** pero muy recomendadas
- Puedes llenar solo los campos relevantes para tu estudio
- Los metadatos se guardan en **archivos separados** del análisis
- Formato JSON es legible y fácil de procesar

---

## 🔗 Integración con el Sistema

El sistema de metadatos se integra automáticamente con:

- ✅ **Ventana de Análisis Temporal** → Captura al exportar
- ✅ **Sistema de Recomendaciones** → Incluye sugerencias
- ✅ **Exportación JSON** → Metadatos + Resultados
- ✅ **Generación de Reportes** → Resúmenes automáticos

---

## 📞 Soporte

Para más información revisa:
- `audio_metadata.py` → Código principal
- `ejemplos_metadatos.py` → Ejemplos de uso
- `gui/metadata_dialog.py` → Interfaz gráfica

---

## 📄 Licencia

Este sistema forma parte del proyecto de Análisis de Audio con Series de Fourier.

**Creado para:** Proyecto académico de análisis acústico urbano  
**Fecha:** Noviembre 2025  
**Propósito:** Documentación georreferenciada de condiciones acústicas
