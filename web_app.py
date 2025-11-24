"""
🌐 SERVIDOR WEB - CLASIFICADOR DE AUDIO
=========================================
API Flask para el clasificador de audio con interfaz web
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from pathlib import Path
import uuid

# Importar módulos existentes
from entrenador_personalizado import EntrenadorPersonalizado
from audio_metadata import AudioMetadata
from fft_analyzer import FFTAnalyzer
from audio_separator import AudioSeparator

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiala'  # Cambiar en producción
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Desactivar caché en desarrollo
app.config['SESSION_TYPE'] = 'filesystem'  # Usar sistema de archivos para sesiones grandes
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora

# Crear directorios necesarios
os.makedirs('uploads', exist_ok=True)
os.makedirs('datos_exportados', exist_ok=True)
os.makedirs('static/temp', exist_ok=True)
os.makedirs('flask_session', exist_ok=True)  # Para sesiones en filesystem

# Instancia global del entrenador
entrenador = None

def get_entrenador():
    """Obtener instancia del entrenador"""
    global entrenador
    if entrenador is None:
        entrenador = EntrenadorPersonalizado()
        # Intentar cargar modelo existente
        try:
            entrenador.cargar_modelo_entrenado()
        except:
            pass
    return entrenador

# Contexto para templates - agregar timestamp para evitar caché
@app.context_processor
def inject_cache_buster():
    """Inyectar timestamp para evitar caché de archivos estáticos"""
    return {'cache_buster': int(datetime.now().timestamp())}

# ==========================================
# RUTAS PRINCIPALES
# ==========================================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/entrenar')
def entrenar():
    """Página de entrenamiento"""
    return render_template('entrenar.html')

@app.route('/identificar')
def identificar():
    """Página de identificación"""
    return render_template('identificar.html')

@app.route('/fft')
def fft():
    """Página de análisis FFT"""
    return render_template('fft.html')

@app.route('/separar')
def separar():
    """Página de separación de audio"""
    return render_template('separador.html')

@app.route('/importar')
def importar():
    """Página de importación de datos"""
    return render_template('importador.html')

# ==========================================
# API - ENTRENAMIENTO
# ==========================================

@app.route('/api/entrenar/estructura', methods=['POST'])
def crear_estructura():
    """Crear estructura de carpetas para entrenamiento"""
    try:
        ent = get_entrenador()
        ent.crear_estructura_datos()
        return jsonify({'success': True, 'message': 'Estructura creada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/entrenar/listar-clases', methods=['POST'])
def listar_clases():
    """Listar clases de entrenamiento"""
    try:
        data = request.json
        carpeta = data.get('carpeta', 'datos_entrenamiento')
        
        clases = []
        total_archivos = 0
        
        if os.path.exists(carpeta):
            for clase_nombre in os.listdir(carpeta):
                clase_path = os.path.join(carpeta, clase_nombre)
                if os.path.isdir(clase_path):
                    archivos = [f for f in os.listdir(clase_path) if f.endswith(('.wav', '.mp3', '.ogg'))]
                    cantidad = len(archivos)
                    total_archivos += cantidad
                    clases.append({'nombre': clase_nombre, 'cantidad': cantidad})
        
        return jsonify({
            'success': True,
            'clases': clases,
            'total_archivos': total_archivos
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/entrenar/entrenar', methods=['POST'])
def entrenar_modelo_api():
    """Entrenar modelo con Random Forest"""
    try:
        data = request.json
        carpeta = data.get('carpeta', 'datos_entrenamiento')
        
        ent = get_entrenador()
        ent.data_dir = carpeta
        
        # Medir tiempo
        inicio = datetime.now()
        
        # Entrenar (ya llama internamente a cargar_datos_entrenamiento)
        exito = ent.entrenar_modelo()
        
        tiempo = (datetime.now() - inicio).seconds
        
        if not exito:
            return jsonify({'success': False, 'error': 'Error en el entrenamiento'}), 500
        
        # Obtener información del modelo
        archivos_procesados = len(ent.features_dataset) if hasattr(ent, 'features_dataset') else 0
        
        return jsonify({
            'success': True,
            'archivos_entrenados': archivos_procesados,
            'clases': list(ent.class_names) if hasattr(ent, 'class_names') else [],
            'tiempo_entrenamiento': tiempo,
            'reporte_clasificacion': 'Ver consola del servidor para detalles',
            'modelo_guardado': 'modelo_personalizado/modelo_rf.pkl'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/entrenar/info-modelo', methods=['GET'])
def info_modelo():
    """Información del modelo actual"""
    try:
        ent = get_entrenador()
        
        if not hasattr(ent, 'modelo') or ent.modelo is None:
            return jsonify({'success': False, 'error': 'No hay modelo entrenado'}), 404
        
        return jsonify({
            'success': True,
            'clases': list(ent.class_names) if hasattr(ent, 'class_names') else [],
            'n_estimators': ent.modelo.n_estimators if hasattr(ent.modelo, 'n_estimators') else 100,
            'max_depth': ent.modelo.max_depth if hasattr(ent.modelo, 'max_depth') else 20
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/entrenar/analizar', methods=['POST'])
def analizar_carpeta():
    """Analizar carpeta de entrenamiento"""
    try:
        import librosa
        
        data = request.json
        carpeta = data.get('carpeta', 'datos_entrenamiento')
        
        clases = []
        total_archivos = 0
        duracion_total = 0
        
        if os.path.exists(carpeta):
            for clase_nombre in os.listdir(carpeta):
                clase_path = os.path.join(carpeta, clase_nombre)
                if os.path.isdir(clase_path):
                    archivos = [f for f in os.listdir(clase_path) if f.endswith(('.wav', '.mp3', '.ogg'))]
                    cantidad = len(archivos)
                    
                    # Calcular duración
                    duracion_clase = 0
                    for archivo in archivos[:10]:  # Solo primeros 10 por velocidad
                        try:
                            audio_path = os.path.join(clase_path, archivo)
                            y, sr = librosa.load(audio_path, sr=None)
                            duracion_clase += len(y) / sr
                        except:
                            pass
                    
                    if cantidad > 10:
                        duracion_clase = duracion_clase / 10 * cantidad
                    
                    total_archivos += cantidad
                    duracion_total += duracion_clase
                    
                    clases.append({
                        'nombre': clase_nombre,
                        'archivos': cantidad,
                        'duracion': duracion_clase
                    })
        
        return jsonify({
            'success': True,
            'carpeta': carpeta,
            'total_archivos': total_archivos,
            'duracion_total': duracion_total,
            'clases': clases
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==========================================
# API - IDENTIFICACIÓN
# ==========================================

@app.route('/api/identificar/upload', methods=['POST'])
def upload_audio():
    """Subir archivo de audio"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió archivo'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nombre de archivo vacío'}), 400
        
        # Guardar archivo
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)
        
        # Guardar en sesión
        session['current_audio'] = filepath
        
        return jsonify({'success': True, 'filename': filename, 'path': unique_name})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/identificar/simple', methods=['POST'])
def predecir_simple():
    """Predicción simple de audio"""
    try:
        audio_path = session.get('current_audio')
        if not audio_path or not os.path.exists(audio_path):
            return jsonify({'success': False, 'error': 'No hay audio cargado'}), 400
        
        ent = get_entrenador()
        
        # Verificar que el modelo esté cargado
        if not hasattr(ent, 'modelo') or ent.modelo is None:
            return jsonify({'success': False, 'error': 'No hay modelo entrenado. Por favor entrena un modelo primero.'}), 400
        
        resultado = ent.predecir_audio(audio_path, mostrar_detalles=False)
        
        if resultado is None:
            return jsonify({'success': False, 'error': 'Error al analizar el audio'}), 500
        
        return jsonify({
            'success': True,
            'clase': resultado['clase_predicha'],
            'confianza': resultado['confianza'],
            'probabilidades': resultado['todas_probabilidades']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/identificar/temporal', methods=['POST'])
def predecir_temporal():
    """Análisis temporal de audio"""
    try:
        data = request.json
        ventana = data.get('ventana', 2.0)
        
        audio_path = session.get('current_audio')
        if not audio_path or not os.path.exists(audio_path):
            return jsonify({'success': False, 'error': 'No hay audio cargado'}), 400
        
        ent = get_entrenador()
        
        # Verificar que el modelo esté cargado
        if not hasattr(ent, 'modelo') or ent.modelo is None:
            return jsonify({'success': False, 'error': 'No hay modelo entrenado. Por favor entrena un modelo primero.'}), 400
        
        resultado = ent.predecir_audio_temporal(audio_path, ventana_segundos=ventana)
        
        if resultado is None:
            return jsonify({'success': False, 'error': 'Error al analizar el audio'}), 500
        
        # Guardar en sesión para exportar
        session['ultimo_resultado'] = resultado
        session.modified = True  # Forzar guardado de sesión
        print(f"✅ Resultado guardado en sesión: {len(resultado.get('detecciones_agrupadas', []))} detecciones")
        
        return jsonify({
            'success': True,
            'archivo': resultado['archivo'],
            'duracion_total': resultado['duracion_total'],
            'detecciones': resultado['detecciones_agrupadas']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==========================================
# API - EXPORTACIÓN
# ==========================================

@app.route('/api/exportar/detecciones', methods=['POST'])
def exportar_detecciones():
    """Exportar detecciones a JSON"""
    try:
        # Si hay un resultado en la petición, úsalo y actualiza la sesión
        resultado = None
        
        if request.is_json:
            nuevo_resultado = request.get_json()
            print(f"📥 Datos recibidos en petición: {bool(nuevo_resultado)}")
            if nuevo_resultado:
                print(f"🔍 Claves del resultado: {nuevo_resultado.keys()}")
                # Normalizar: si tiene 'detecciones' pero no 'detecciones_agrupadas'
                if 'detecciones' in nuevo_resultado and 'detecciones_agrupadas' not in nuevo_resultado:
                    nuevo_resultado['detecciones_agrupadas'] = nuevo_resultado['detecciones']
                    print(f"✅ Normalizado: detecciones -> detecciones_agrupadas")
                
                session['ultimo_resultado'] = nuevo_resultado
                session.modified = True  # Forzar guardado de sesión
                resultado = nuevo_resultado
        
        # Si no vino en la petición, intentar obtener de sesión
        if not resultado:
            resultado = session.get('ultimo_resultado')
            print(f"📦 Resultado desde sesión: {bool(resultado)}")
        
        if not resultado:
            print("❌ No hay resultado para exportar")
            return jsonify({'success': False, 'error': 'No hay resultado para exportar. Por favor, analiza un audio primero.'}), 400

        detecciones_count = len(resultado.get('detecciones_agrupadas', resultado.get('detecciones', [])))
        print(f"✅ Exportando {detecciones_count} detecciones")
        
        ent = get_entrenador()
        output_path = ent.exportar_detecciones_json(resultado)

        return jsonify({
            'success': True,
            'path': output_path,
            'download_url': f'/api/download/{os.path.basename(output_path)}'
        })
    except Exception as e:
        print(f"❌ Error al exportar detecciones: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/exportar/metadatos', methods=['POST'])
def exportar_metadatos():
    """Exportar metadatos"""
    try:
        data = request.json
        print(f"📥 Datos recibidos: {data}")
        
        audio_path = session.get('current_audio')
        
        if not audio_path:
            return jsonify({'success': False, 'error': 'No hay audio cargado'}), 400
        
        print(f"📁 Audio path: {audio_path}")
        
        # Crear metadatos
        metadata = AudioMetadata(audio_path)
        
        # Establecer datos
        if 'ubicacion' in data:
            print(f"📍 Ubicación: {data['ubicacion']}")
            metadata.set_ubicacion(**data['ubicacion'])
        
        if 'grabacion' in data:
            print(f"🎙️ Grabación: {data['grabacion']}")
            metadata.set_grabacion_info(**data['grabacion'])
        
        # Copiar la clasificación detectada en condiciones.trafico
        condiciones = data.get('condiciones', {})
        print(f"🌤️ Condiciones recibidas: {condiciones}")
        
        resultado = session.get('ultimo_resultado')
        clasificacion_detectada = None
        if resultado:
            # Si existe agrupación, usar la primera clase
            detecciones = resultado.get('detecciones_agrupadas', [])
            if detecciones and 'clase' in detecciones[0]:
                clasificacion_detectada = detecciones[0]['clase']
            # Si existe analisis.clasificacion, usar ese valor
            elif 'analisis' in resultado and 'clasificacion' in resultado['analisis']:
                clasificacion_detectada = resultado['analisis']['clasificacion']
        
        # Si no hay trafico en condiciones pero hay clasificación detectada, usarla
        if clasificacion_detectada and not condiciones.get('trafico'):
            condiciones['trafico'] = clasificacion_detectada
            print(f"✅ Clasificación detectada: {clasificacion_detectada}")
        
        # Renombrar trafico_estimado a trafico si existe (por compatibilidad)
        if 'trafico_estimado' in condiciones:
            condiciones['trafico'] = condiciones.pop('trafico_estimado')
        
        metadata.set_condiciones(**condiciones)
        
        if 'dispositivo' in data:
            print(f"📱 Dispositivo: {data['dispositivo']}")
            metadata.set_dispositivo(**data['dispositivo'])
        
        if 'notas' in data:
            metadata.set_notas(data['notas'])
        
        # Agregar análisis si existe
        resultado = session.get('ultimo_resultado')
        if resultado:
            detecciones = resultado.get('detecciones_agrupadas', [])
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
        
        # Guardar
        output_path = metadata.save_to_file()
        print(f"💾 Archivo guardado en: {output_path}")
        
        return jsonify({
            'success': True,
            'path': output_path,
            'download_url': f'/api/download/{os.path.basename(output_path)}'
        })
    except Exception as e:
        print(f"❌ Error al exportar metadatos: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ==========================================
# API - IMPORTACIÓN
# ==========================================

@app.route('/api/importar/listar', methods=['GET'])
def listar_archivos_exportados():
    """Listar archivos exportados"""
    try:
        archivos = []
        export_dir = 'datos_exportados'
        
        if os.path.exists(export_dir):
            for filename in os.listdir(export_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(export_dir, filename)
                    stat = os.stat(filepath)
                    
                    tipo = 'metadatos' if 'metadata' in filename else 'detecciones'
                    
                    archivos.append({
                        'nombre': filename,
                        'tipo': tipo,
                        'tamano': f"{stat.st_size / 1024:.1f} KB",
                        'fecha': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        return jsonify({'success': True, 'archivos': archivos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/importar/cargar', methods=['POST'])
def cargar_archivo_exportado():
    """Cargar archivo exportado"""
    try:
        data = request.json
        nombre = data.get('nombre')
        
        if not nombre:
            return jsonify({'success': False, 'error': 'Nombre de archivo no proporcionado'}), 400
        
        ruta = os.path.join('datos_exportados', nombre)
        if not os.path.exists(ruta):
            return jsonify({'success': False, 'error': 'Archivo no encontrado'}), 404
        
        with open(ruta, 'r', encoding='utf-8') as f:
            contenido = json.load(f)
        
        return jsonify({'success': True, 'contenido': contenido})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==========================================
# API - DESCARGA
# ==========================================

@app.route('/api/download/<filename>')
def download_file(filename):
    """Descargar archivo"""
    try:
        filepath = os.path.join('datos_exportados', secure_filename(filename))
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        return jsonify({'error': 'Archivo no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==========================================
# API - FFT
# ==========================================

@app.route('/api/fft/upload', methods=['POST'])
def upload_audio_fft():
    """Subir archivo de audio para FFT"""
    return upload_audio()  # Reutilizar función

@app.route('/api/fft/analizar', methods=['POST'])
def analizar_fft():
    """Análizar FFT de audio"""
    try:
        import librosa
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')  # Backend sin GUI
        import matplotlib.pyplot as plt
        
        audio_path = session.get('current_audio')
        if not audio_path or not os.path.exists(audio_path):
            return jsonify({'success': False, 'error': 'No hay audio cargado'}), 400
        
        # Cargar audio
        y, sr = librosa.load(audio_path, sr=None)
        duracion = len(y) / sr
        
        # Generar espectrograma
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        
        # Crear imagen del espectrograma
        plt.figure(figsize=(14, 7))
        librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz', cmap='viridis')
        plt.colorbar(format='%+2.0f dB', label='Energía (dB)')
        plt.title(f'Espectrograma - {os.path.basename(audio_path)}', fontsize=16, pad=20)
        plt.xlabel('Tiempo (s)', fontsize=13)
        plt.ylabel('Frecuencia (Hz)', fontsize=13)
        plt.ylim(0, 10000)  # Limitar frecuencia hasta 10 kHz
        plt.tight_layout()
        
        # Guardar imagen
        os.makedirs('static/temp', exist_ok=True)
        img_filename = f'espectrograma_{uuid.uuid4().hex}.png'
        img_path = os.path.join('static', 'temp', img_filename)
        print(f"[FFT] Guardando espectrograma en: {img_path}")
        try:
            plt.savefig(img_path, dpi=150, bbox_inches='tight', facecolor='white')
            print(f"[FFT] Espectrograma guardado correctamente: {os.path.exists(img_path)}")
        except Exception as e:
            print(f"[FFT] Error al guardar espectrograma: {e}")
        plt.close()
        
        # Guardar ruta en sesión
        session['espectrograma_img'] = f'/static/temp/{img_filename}'
        session['ultimo_fft'] = {
            'archivo': os.path.basename(audio_path),
            'duracion': duracion,
            'sample_rate': sr
        }
        
        return jsonify({
            'success': True,
            'archivo': os.path.basename(audio_path),
            'duracion_total': duracion,
            'sample_rate': sr,
            'espectrograma_url': session.get('espectrograma_img')
        })
        
        if False:
            # Análisis completo
            fft_result = np.fft.fft(y)
            freqs = np.fft.fftfreq(len(y), 1/sr)
            
            # Solo frecuencias positivas
            positive_freqs = freqs[:len(freqs)//2]
            magnitudes = np.abs(fft_result[:len(fft_result)//2])
            
            # Top frecuencias
            indices = np.argsort(magnitudes)[-100:]
            frecuencias_dominantes = [
                {'frecuencia': float(positive_freqs[i]), 'magnitud': float(magnitudes[i])}
                for i in indices if positive_freqs[i] > 0
            ]
            
            potencia = 10 * np.log10(np.mean(magnitudes**2) + 1e-10)
            
            session['ultimo_fft'] = {
                'archivo': os.path.basename(audio_path),
                'modo': modo,
                'frecuencias_dominantes': frecuencias_dominantes
            }
            
            return jsonify({
                'success': True,
                'archivo': os.path.basename(audio_path),
                'duracion_total': duracion,
                'sample_rate': sr,
                'frecuencias_dominantes': frecuencias_dominantes,
                'potencia_promedio': float(potencia),
                'espectrograma_url': session.get('espectrograma_img')
            })
        else:
            # Análisis por ventanas
            ventanas_data = []
            muestras_ventana = int(ventana * sr)
            
            for i in range(0, len(y), muestras_ventana):
                segmento = y[i:i+muestras_ventana]
                if len(segmento) < muestras_ventana // 2:
                    continue
                
                fft_result = np.fft.fft(segmento)
                freqs = np.fft.fftfreq(len(segmento), 1/sr)
                
                positive_freqs = freqs[:len(freqs)//2]
                magnitudes = np.abs(fft_result[:len(fft_result)//2])
                
                # Frecuencia dominante
                idx_max = np.argmax(magnitudes)
                freq_dominante = float(positive_freqs[idx_max])
                
                # Top 10 frecuencias
                indices = np.argsort(magnitudes)[-10:]
                frecuencias_principales = [
                    {'frecuencia': float(positive_freqs[j]), 'magnitud': float(magnitudes[j])}
                    for j in indices if positive_freqs[j] > 0
                ]
                
                potencia = 10 * np.log10(np.mean(magnitudes**2) + 1e-10)
                
                ventanas_data.append({
                    'tiempo_inicio': i / sr,
                    'tiempo_fin': min((i + muestras_ventana) / sr, duracion),
                    'frecuencia_dominante': freq_dominante,
                    'potencia': float(potencia),
                    'frecuencias_principales': frecuencias_principales
                })
            
            session['ultimo_fft'] = {
                'archivo': os.path.basename(audio_path),
                'modo': modo,
                'ventanas': ventanas_data
            }
            
            return jsonify({
                'success': True,
                'archivo': os.path.basename(audio_path),
                'duracion_total': duracion,
                'sample_rate': sr,
                'ventanas': ventanas_data,
                'espectrograma_url': session.get('espectrograma_img')
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/fft/exportar', methods=['POST'])
def exportar_fft():
    """Exportar análisis FFT"""
    try:
        resultado = session.get('ultimo_fft')
        if not resultado:
            return jsonify({'success': False, 'error': 'No hay análisis para exportar'}), 400
        
        # Guardar
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'fft_analysis_{timestamp}.json'
        filepath = os.path.join('datos_exportados', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'path': filepath
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==========================================
# API - SEPARADOR DE AUDIO
# ==========================================

@app.route('/api/separador/upload', methods=['POST'])
def upload_audio_separador():
    """Subir archivo para separar"""
    return upload_audio()  # Reutilizar

@app.route('/api/separador/filtrar', methods=['POST'])
def filtrar_audio():
    """Suprimir frecuencias usando perfiles aprendidos del entrenamiento"""
    try:
        import librosa
        import soundfile as sf
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from frequency_profiler import FrequencyProfiler
        
        data = request.json
        clase_audio = data.get('clase_audio', 'Mucho_Trafico')
        modo_operacion = data.get('modo_operacion', 'aislar')  # 'aislar' o 'suprimir'
        
        audio_path = session.get('current_audio')
        if not audio_path or not os.path.exists(audio_path):
            return jsonify({'success': False, 'error': 'No hay audio cargado'}), 400
        
        # ===== CARGAR PERFILES DE FRECUENCIA APRENDIDOS =====
        profiler = FrequencyProfiler()
        perfiles = profiler.cargar_perfiles()
        
        if not perfiles:
            return jsonify({'success': False, 'error': 'No hay perfiles entrenados. Entrena el modelo primero.'}), 400
        
        if clase_audio not in perfiles:
            return jsonify({'success': False, 'error': f'No existe perfil para: {clase_audio}'}), 400
        
        perfil = perfiles[clase_audio]
        frecuencias_objetivo = perfil['frecuencias_dominantes']
        
        accion = 'Aislando' if modo_operacion == 'aislar' else 'Suprimiendo'
        print(f"\n🎯 {accion} frecuencias de: {clase_audio}")
        print(f"   Frecuencias objetivo: {frecuencias_objetivo[:8]}")
        
        # Cargar audio
        y, sr = librosa.load(audio_path, sr=None)
        duracion = len(y) / sr
        n = len(y)
        
        # ===== 1. FFT - TRANSFORMAR A DOMINIO DE FRECUENCIAS =====
        fft_result = np.fft.fft(y)
        freqs = np.fft.fftfreq(n, 1/sr)
        freqs_abs = np.abs(freqs)
        
        # ===== 2. CREAR MÁSCARA =====
        ventana = 15  # Hz
        
        if modo_operacion == 'aislar':
            # AISLAR: Mantener SOLO las frecuencias objetivo (eliminar ruido)
            mask = np.zeros(len(freqs), dtype=bool)
            for freq_objetivo in frecuencias_objetivo:
                mask_freq = (freqs_abs >= freq_objetivo - ventana) & \
                           (freqs_abs <= freq_objetivo + ventana)
                mask |= mask_freq
                print(f"   Aislando: {freq_objetivo} ± {ventana} Hz")
        else:
            # SUPRIMIR: Eliminar las frecuencias objetivo (mantener resto)
            mask = np.ones(len(freqs), dtype=bool)
            for freq_objetivo in frecuencias_objetivo:
                mask_suprimir = (freqs_abs >= freq_objetivo - ventana) & \
                               (freqs_abs <= freq_objetivo + ventana)
                mask &= ~mask_suprimir
                print(f"   Suprimiendo: {freq_objetivo} ± {ventana} Hz")
        
        # ===== 3. APLICAR MÁSCARA AL ESPECTRO =====
        fft_filtered = fft_result.copy()
        fft_filtered[~mask] = 0
        
        # ===== 4. ✨ IFFT - RECONSTRUIR AUDIO SIN LAS FRECUENCIAS SUPRIMIDAS ✨ =====
        y_filtered = np.real(np.fft.ifft(fft_filtered))
        y_filtered = librosa.util.normalize(y_filtered)
        
        # Guardar audio filtrado
        os.makedirs('audios_filtrados', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        prefijo = 'aislado' if modo_operacion == 'aislar' else 'suprimido'
        output_filename = f'{prefijo}_{clase_audio}_{timestamp}.wav'
        output_path = os.path.join('audios_filtrados', output_filename)
        
        sf.write(output_path, y_filtered, sr)
        
        # Calcular energías
        energia_original = np.sum(np.abs(y)**2)
        energia_filtrada = np.sum(np.abs(y_filtered)**2)
        reduccion_db = 10 * np.log10((energia_filtrada + 1e-10) / (energia_original + 1e-10))
        
        # ===== GENERAR ESPECTROGRAMAS =====
        os.makedirs('static/temp', exist_ok=True)
        
        # Espectrograma original
        D_orig = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        plt.figure(figsize=(14, 6))
        librosa.display.specshow(D_orig, sr=sr, x_axis='time', y_axis='hz', cmap='viridis')
        plt.colorbar(format='%+2.0f dB', label='Energía (dB)')
        plt.title('Espectrograma Original', fontsize=16, pad=20)
        plt.xlabel('Tiempo (s)', fontsize=13)
        plt.ylabel('Frecuencia (Hz)', fontsize=13)
        plt.ylim(0, 2000)
        plt.tight_layout()
        
        img_orig_filename = f'espectro_orig_{uuid.uuid4().hex}.png'
        img_orig_path = os.path.join('static', 'temp', img_orig_filename)
        plt.savefig(img_orig_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Espectrograma procesado
        D_filt = librosa.amplitude_to_db(np.abs(librosa.stft(y_filtered)), ref=np.max)
        plt.figure(figsize=(14, 6))
        librosa.display.specshow(D_filt, sr=sr, x_axis='time', y_axis='hz', cmap='viridis')
        plt.colorbar(format='%+2.0f dB', label='Energía (dB)')
        
        if modo_operacion == 'aislar':
            titulo = f'Audio Reconstruido con IFFT - Aisladas frecuencias de "{clase_audio}" (ruido eliminado)'
            color_linea = 'cyan'
            texto_linea = 'aislada'
        else:
            titulo = f'Audio Reconstruido con IFFT - Suprimidas frecuencias de "{clase_audio}"'
            color_linea = 'red'
            texto_linea = 'suprimida'
        
        plt.title(titulo, fontsize=16, pad=20)
        plt.xlabel('Tiempo (s)', fontsize=13)
        plt.ylabel('Frecuencia (Hz)', fontsize=13)
        plt.ylim(0, 2000)
        
        # Dibujar líneas indicando frecuencias procesadas
        for i, freq in enumerate(frecuencias_objetivo[:8]):
            if freq <= 2000:
                plt.axhline(y=freq, color=color_linea, linestyle='--', linewidth=1.5, alpha=0.7)
                plt.text(duracion * 0.02, freq, f'{freq:.0f}Hz ({texto_linea})', 
                        color=color_linea, fontsize=9, ha='left', va='bottom',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.5))
        
        plt.tight_layout()
        
        img_filt_filename = f'espectro_filt_{uuid.uuid4().hex}.png'
        img_filt_path = os.path.join('static', 'temp', img_filt_filename)
        plt.savefig(img_filt_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        metodo_texto = 'FFT → Aislamiento de frecuencias (eliminación de ruido) → IFFT' if modo_operacion == 'aislar' else 'FFT → Supresión de frecuencias → IFFT'
        
        return jsonify({
            'success': True,
            'archivo_original': os.path.basename(audio_path),
            'archivo_filtrado': output_path,
            'clase_procesada': clase_audio,
            'modo_operacion': modo_operacion,
            'frecuencias_procesadas': [float(f) for f in frecuencias_objetivo],
            'num_frecuencias': len(frecuencias_objetivo),
            'duracion': duracion,
            'energia_original': float(10 * np.log10(energia_original + 1e-10)),
            'energia_filtrada': float(10 * np.log10(energia_filtrada + 1e-10)),
            'reduccion_db': float(reduccion_db),
            'metodo': metodo_texto,
            'espectrograma_original_url': f'/static/temp/{img_orig_filename}',
            'espectrograma_filtrado_url': f'/static/temp/{img_filt_filename}'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/separador/descargar', methods=['GET'])
def descargar_audio_filtrado():
    """Descargar audio filtrado"""
    try:
        archivo = request.args.get('archivo')
        if not archivo:
            return jsonify({'error': 'Archivo no especificado'}), 400
        
        if os.path.exists(archivo):
            return send_file(archivo, as_attachment=True)
        
        return jsonify({'error': 'Archivo no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==========================================
# EJECUTAR SERVIDOR
# ==========================================

if __name__ == '__main__':
    print("🌐 Iniciando servidor web...")
    print("📍 Accede a: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
