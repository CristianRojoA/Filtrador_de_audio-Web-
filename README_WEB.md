# Sistema de Detección de Audio de Tráfico - Versión Web

## 📋 Descripción

Aplicación web basada en Flask para análisis de audio de tráfico vehicular con:
- 🎯 Identificación temporal de sonidos
- 🧠 Entrenamiento de modelo Random Forest personalizado
- 📊 Análisis FFT (Transformada de Fourier)
- 🎚️ Separador de audio por frecuencias con FFT/IFFT
- 📍 Sistema de metadatos geográficos
- 📥 Importador de datos exportados

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip

### Pasos de Instalación

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias**
```powershell
pip install -r requirements_web.txt
```

Las dependencias incluyen:
- Flask 3.0.0 (servidor web)
- tensorflow-hub (YAMNet para análisis de audio)
- librosa (procesamiento de audio)
- scikit-learn (Random Forest)
- numpy, scipy (procesamiento numérico)

3. **Crear estructura de carpetas**
```powershell
mkdir -p uploads, datos_entrenamiento, datos_exportados, modelo_personalizado, audios_filtrados
```

## 🎮 Uso

### Iniciar el Servidor

```powershell
python web_app.py
```

El servidor estará disponible en: `http://localhost:5000`

### Características Principales

#### 1. 🎯 Identificar Audio
- Cargar archivo de audio (.wav, .mp3, .ogg)
- Análisis temporal con ventanas configurables
- Exportar detecciones a JSON con metadatos opcionales

#### 2. 🧠 Entrenar Modelo
- Seleccionar carpeta de entrenamiento
- Configurar parámetros del Random Forest
- Ver métricas de precisión por clase
- Análisis de carpeta de datos

#### 3. 📊 Análisis FFT
- Análisis completo o por ventanas
- Identificación de frecuencias dominantes
- Exportar análisis FFT a JSON

#### 4. 🎚️ Separador de Audio
- 6 modos de filtrado predefinidos:
  - 🚗 Motores de Autos (50-500 Hz)
  - 🚨 Sirenas (400-1500 Hz)
  - 📯 Bocinas (200-800 Hz)
  - 🚛 Camiones Pesados (30-300 Hz)
  - 🏍️ Motocicletas (100-800 Hz)
  - ⚙️ Personalizado
- Comparación de espectros
- Reproducir y descargar audio filtrado

#### 5. 📥 Importador de Datos
- Visualizar archivos exportados
- Tabs: Resumen, Detecciones, Metadatos, JSON
- Estadísticas automáticas

## 📁 Estructura del Proyecto

```
IA/
├── web_app.py                 # Servidor Flask principal
├── requirements_web.txt       # Dependencias Python
│
├── templates/                 # Plantillas HTML
│   ├── index.html            # Página principal
│   ├── identificar.html      # Identificación de audio
│   ├── entrenar.html         # Entrenamiento de modelo
│   ├── fft.html              # Análisis FFT
│   ├── separador.html        # Separador de audio
│   └── importador.html       # Importador de datos
│
├── static/
│   ├── css/
│   │   └── style.css         # Estilos CSS completos
│   └── js/
│       ├── identificar.js    # Lógica de identificación
│       ├── entrenar.js       # Lógica de entrenamiento
│       ├── fft.js            # Lógica FFT
│       ├── separador.js      # Lógica separador
│       └── importador.js     # Lógica importador
│
├── uploads/                   # Archivos de audio subidos
├── datos_entrenamiento/       # Datos para entrenar modelo
├── datos_exportados/          # JSON exportados
├── modelo_personalizado/      # Modelos entrenados
├── audios_filtrados/          # Audios procesados
│
├── entrenador_personalizado.py
├── audio_metadata.py
├── fft_analyzer.py
└── audio_separator.py
```

## 🔧 Configuración

### Carpeta de Entrenamiento
Por defecto: `datos_entrenamiento/`

Estructura esperada:
```
datos_entrenamiento/
├── autos15s/
│   ├── audio1.wav
│   └── audio2.wav
├── Trafico/
│   └── audio3.wav
└── TRAFICOPESADO/
    └── audio4.wav
```

### Puertos y Configuración
- Puerto por defecto: `5000`
- Modo debug: Habilitado en desarrollo
- Carpeta de uploads: `uploads/`
- Tamaño máximo de archivo: Configurable en Flask

## 📊 API Endpoints

### Identificar Audio
- `POST /api/identificar/upload` - Subir audio
- `POST /api/identificar/simple` - Predicción simple
- `POST /api/identificar/temporal` - Análisis temporal

### Entrenar Modelo
- `POST /api/entrenar/listar-clases` - Listar clases disponibles
- `POST /api/entrenar/entrenar` - Entrenar modelo
- `GET /api/entrenar/info-modelo` - Info del modelo actual
- `POST /api/entrenar/analizar` - Analizar carpeta

### Análisis FFT
- `POST /api/fft/upload` - Subir audio
- `POST /api/fft/analizar` - Analizar FFT
- `POST /api/fft/exportar` - Exportar resultados

### Separador de Audio
- `POST /api/separador/upload` - Subir audio
- `POST /api/separador/filtrar` - Filtrar por frecuencias
- `GET /api/separador/descargar` - Descargar audio filtrado

### Importador
- `GET /api/importar/listar` - Listar archivos exportados
- `POST /api/importar/cargar` - Cargar archivo JSON

### Exportar
- `POST /api/exportar/detecciones` - Exportar detecciones
- `POST /api/exportar/metadatos` - Exportar con metadatos

## 🎨 Características de la Interfaz

- ✨ Diseño moderno con gradientes y animaciones
- 📱 Responsive (adaptado a móviles y tablets)
- 🎯 Cards interactivas con hover effects
- 📊 Gráficos ASCII en tiempo real
- 🎨 Código de colores por tipo de contenido
- ⚡ Carga asíncrona sin recargar página

## 🐛 Solución de Problemas

### Error: "No module named 'flask'"
```powershell
pip install flask
```

### Error: "No module named 'librosa'"
```powershell
pip install librosa
```

### Error al cargar audio
- Verificar formato compatible (.wav, .mp3, .ogg)
- Verificar permisos de carpeta `uploads/`

### Modelo no encontrado
- Entrenar un modelo primero desde la página de entrenamiento
- Verificar que existe `modelo_personalizado/modelo_rf.pkl`

## 📝 Notas de Desarrollo

### Diferencias con Versión Tkinter
- Interfaz web en lugar de GUI de escritorio
- API REST en lugar de llamadas directas
- Subida de archivos con FormData
- Visualización con HTML/CSS/JavaScript

### Mejoras Futuras
- [ ] Gráficos interactivos con Chart.js
- [ ] WebSockets para progreso en tiempo real
- [ ] Autenticación de usuarios
- [ ] Base de datos para historial
- [ ] API de geolocalización automática
- [ ] Exportar a múltiples formatos (CSV, Excel)

## 📄 Licencia

Este proyecto es de código abierto.

## 👤 Autor

Cristian - Sistema de Detección de Audio de Tráfico

## 🙏 Agradecimientos

- TensorFlow Hub por YAMNet
- Librosa por procesamiento de audio
- Flask por el framework web
