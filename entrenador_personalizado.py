"""
🧠 ENTRENADOR DE CLASIFICADOR PERSONALIZADO
===============================================
Sistema para entrenar tu propio clasificador de sonidos urbanos
con tus audios específicos y contexto particular.

VENTAJAS:
✅ Entrenas con TUS propios audios
✅ Contexto específico para tu entorno
✅ Mayor precisión en tus categorías
✅ Fácil de usar y expandir
"""

import os
import numpy as np
import librosa
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
import tensorflow_hub as hub
from pathlib import Path
import json
from datetime import datetime

class EntrenadorPersonalizado:
    def __init__(self):
        """Inicializar entrenador personalizado"""
        print("🧠 Inicializando Entrenador Personalizado...")
        
        # Cargar YAMNet para extraer características
        print("📥 Cargando YAMNet para extracción de características...")
        self.yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')
        
        # Configuración
        self.sample_rate = 16000
        self.features_dataset = []
        self.labels_dataset = []
        self.class_names = []
        
        # Directorio para datos de entrenamiento
        self.data_dir = "datos_entrenamiento"
        self.model_dir = "modelo_personalizado"
        
        # Crear directorios si no existen
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)
        
        print("✅ Entrenador inicializado correctamente")

    def crear_estructura_datos(self):
        """Crear estructura de carpetas para organizar audios de entrenamiento"""
        print("\n📁 CREANDO ESTRUCTURA PARA DATOS DE ENTRENAMIENTO")
        print("="*60)
        
        # Categorías específicas para tu contexto urbano
        categorias = [
            "perros_ladrando",
            "gatos_maullando",
            "autos_pasando", 
            "camiones_diesel",
            "motos_acelerando",
            "bicicletas",
            "sirenas_ambulancia",
            "sirenas_policia", 
            "sirenas_bomberos",
            "claxon_auto",
            "claxon_camion",
            "frenos_vehiculos",
            "construccion_martillos",
            "construccion_taladros",
            "voces_conversacion",
            "voces_gritos",
            "musica_fuerte",
            "musica_suave",
            "television_radio",
            "silencio_urbano",
            "lluvia_ligera",
            "lluvia_fuerte",
            "viento_fuerte",
            "pasos_personas",
            "puertas_cerrando",
            "otros_sonidos"
        ]
        
        print(f"🏗️ Creando {len(categorias)} categorías específicas...")
        
        # Crear carpetas para cada categoría
        for i, categoria in enumerate(categorias, 1):
            carpeta_path = os.path.join(self.data_dir, categoria)
            os.makedirs(carpeta_path, exist_ok=True)
            
            # Crear archivo README en cada carpeta
            readme_path = os.path.join(carpeta_path, "INSTRUCCIONES.txt")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"📁 CATEGORÍA: {categoria.upper().replace('_', ' ')}\n")
                f.write("="*50 + "\n\n")
                f.write("🎯 QUÉ PONER AQUÍ:\n")
                f.write(f"• Archivos de audio que contengan SOLO sonidos de: {categoria.replace('_', ' ')}\n")
                f.write("• Ejemplos claros y sin ruido de fondo excesivo\n")
                f.write("• Diferentes variaciones del mismo tipo de sonido\n\n")
                f.write("📋 FORMATO DE ARCHIVOS:\n")
                f.write("• Tipos: .wav, .mp3, .m4a, .flac\n")
                f.write("• Duración: 3-15 segundos (óptimo: 5-8 seg)\n")
                f.write("• Nombres: descriptivos (ej: perro_grande_ladrido_01.wav)\n\n")
                f.write("📊 CANTIDAD RECOMENDADA:\n")
                f.write("• Mínimo: 15-20 archivos por categoría\n")
                f.write("• Ideal: 30-50 archivos por categoría\n")
                f.write("• Más archivos = mejor precisión\n\n")
                
                # Contar archivos actuales
                archivos_actuales = [f for f in os.listdir(carpeta_path) 
                                   if not f.endswith('.txt')]
                f.write(f"📈 Estado actual: {len(archivos_actuales)} archivos\n")
                
                if len(archivos_actuales) < 15:
                    f.write("⚠️ NECESITAS MÁS ARCHIVOS para entrenar bien\n")
                elif len(archivos_actuales) < 30:
                    f.write("✅ Cantidad aceptable, más archivos mejorarían precisión\n")
                else:
                    f.write("🏆 ¡Excelente cantidad de datos!\n")
            
            print(f"   [{i:2d}/{len(categorias)}] ✅ {categoria}")
        
        print(f"\n🎯 ESTRUCTURA CREADA EXITOSAMENTE")
        print(f"📂 Directorio base: {os.path.abspath(self.data_dir)}")
        print(f"📁 {len(categorias)} carpetas de categorías")
        
        print(f"\n📋 PRÓXIMOS PASOS:")
        print("1️⃣ Graba o recopila audios para cada categoría")
        print("2️⃣ Colócalos en sus carpetas correspondientes") 
        print("3️⃣ Ejecuta: entrenar_modelo() cuando tengas suficientes")
        print("4️⃣ Usa: predecir_audio() para clasificar nuevos sonidos")
        
        # Mostrar ejemplo de uso
        print(f"\n💡 EJEMPLO DE USO:")
        print("```")
        print("entrenador = EntrenadorPersonalizado()")
        print("entrenador.crear_estructura_datos()  # Ya hecho ✅")
        print("# ... agregar archivos a las carpetas ...")
        print("entrenador.entrenar_modelo()")
        print("entrenador.predecir_audio('mi_audio.wav')")
        print("```")
        
        return categorias

    def verificar_datos(self):
        """Verificar qué datos están disponibles para entrenamiento"""
        print("\n🔍 VERIFICANDO DATOS DISPONIBLES")
        print("="*50)
        
        total_archivos = 0
        categorias_listas = 0
        resumen = []
        
        for categoria in os.listdir(self.data_dir):
            categoria_path = os.path.join(self.data_dir, categoria)
            if not os.path.isdir(categoria_path):
                continue
            
            # Contar archivos de audio
            archivos = []
            for archivo in os.listdir(categoria_path):
                if any(archivo.lower().endswith(ext) for ext in ['.wav', '.mp3', '.m4a', '.flac', '.ogg']):
                    archivos.append(archivo)
            
            num_archivos = len(archivos)
            total_archivos += num_archivos
            
            # Determinar estado
            if num_archivos >= 15:
                categorias_listas += 1
                estado = "✅ LISTO"
            elif num_archivos >= 5:
                estado = "⚠️ POCOS"
            else:
                estado = "❌ INSUFICIENTE"
            
            resumen.append({
                'categoria': categoria,
                'archivos': num_archivos,
                'estado': estado
            })
        
        # Mostrar resumen
        print(f"📊 RESUMEN GENERAL:")
        print(f"   📁 Categorías totales: {len(resumen)}")
        print(f"   🎵 Archivos totales: {total_archivos}")
        print(f"   ✅ Categorías listas: {categorias_listas}")
        
        print(f"\n📋 DETALLE POR CATEGORÍA:")
        for item in sorted(resumen, key=lambda x: x['archivos'], reverse=True):
            print(f"   {item['estado']} {item['categoria']:25} ({item['archivos']:2d} archivos)")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        if categorias_listas >= 2:
            print("🟢 ¡Puedes entrenar el modelo!")
            if categorias_listas < 3:
                print("⚠️ Con 2 categorías tendrás clasificación binaria (sí/no)")
            elif categorias_listas < 5:
                print("✅ Con 3-4 categorías tendrás un clasificador decente")
            return True
        else:
            print("🟡 Necesitas al menos 2 categorías con 15+ archivos cada una")
            return False

    def extraer_caracteristicas_yamnet(self, audio_path):
        """Extraer características usando YAMNet como extractor de features"""
        import warnings
        warnings.filterwarnings('ignore')
        
        try:
            # Intentar con pydub primero si es MP3 problemático
            if audio_path.lower().endswith('.mp3'):
                try:
                    from pydub import AudioSegment
                    import io
                    
                    # Cargar con pydub (más robusto para MP3 corruptos)
                    audio = AudioSegment.from_mp3(audio_path)
                    audio = audio.set_channels(1)  # Mono
                    audio = audio.set_frame_rate(self.sample_rate)  # 16kHz
                    
                    # Convertir a numpy array
                    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
                    audio_data = samples / (2**15)  # Normalizar de int16 a float32
                    
                except:
                    # Si pydub falla, usar librosa
                    audio_data, sr = librosa.load(audio_path, sr=self.sample_rate, duration=30)
            else:
                # Para WAV, FLAC, etc. usar librosa directamente
                audio_data, sr = librosa.load(audio_path, sr=self.sample_rate, duration=30)
            
            # Asegurar que no esté vacío
            if len(audio_data) == 0:
                return None
            
            # Normalizar audio
            audio_max = np.max(np.abs(audio_data))
            if audio_max > 0:
                audio_data = audio_data / audio_max
            
            # Convertir a tensor
            waveform = tf.convert_to_tensor(audio_data, dtype=tf.float32)
            
            # Obtener embeddings de YAMNet (características profundas)
            scores, embeddings, spectrogram = self.yamnet_model(waveform)
            
            # Promediar embeddings a lo largo del tiempo
            embedding_mean = tf.reduce_mean(embeddings, axis=0)
            
            return embedding_mean.numpy()
            
        except Exception as e:
            # Silenciar errores de librosa/mpg123
            return None

    def cargar_datos_entrenamiento(self):
        """Cargar y procesar todos los audios de entrenamiento"""
        print("\n🔄 CARGANDO DATOS DE ENTRENAMIENTO...")
        print("="*50)
        
        self.features_dataset = []
        self.labels_dataset = []
        self.class_names = []
        
        total_procesados = 0
        total_errores = 0
        
        # Recorrer cada carpeta de categoría
        for categoria in sorted(os.listdir(self.data_dir)):
            categoria_path = os.path.join(self.data_dir, categoria)
            if not os.path.isdir(categoria_path):
                continue
                
            print(f"\n📂 Procesando: {categoria}")
            
            # Agregar a nombres de clases si no existe
            if categoria not in self.class_names:
                self.class_names.append(categoria)
            
            categoria_idx = self.class_names.index(categoria)
            archivos_procesados = 0
            archivos_error = 0
            
            # Procesar cada archivo de audio en la categoría
            archivos_audio = []
            for archivo in os.listdir(categoria_path):
                if any(archivo.lower().endswith(ext) for ext in ['.wav', '.mp3', '.m4a', '.flac', '.ogg']):
                    archivos_audio.append(archivo)
            
            if not archivos_audio:
                print(f"   ⚠️ No hay archivos de audio")
                continue
            
            print(f"   📊 {len(archivos_audio)} archivos encontrados")
            
            for archivo in archivos_audio:
                archivo_path = os.path.join(categoria_path, archivo)
                
                # Extraer características
                features = self.extraer_caracteristicas_yamnet(archivo_path)
                
                if features is not None:
                    self.features_dataset.append(features)
                    self.labels_dataset.append(categoria_idx)
                    archivos_procesados += 1
                    total_procesados += 1
                    print(f"   ✅ {archivo}")
                else:
                    archivos_error += 1
                    total_errores += 1
            
            print(f"   📈 Resultado: {archivos_procesados} exitosos, {archivos_error} errores")
        
        print(f"\n🎯 RESUMEN FINAL:")
        print(f"   📁 Categorías procesadas: {len(self.class_names)}")
        print(f"   ✅ Archivos exitosos: {total_procesados}")
        print(f"   ❌ Archivos con error: {total_errores}")
        print(f"   🧬 Dimensión features: {len(self.features_dataset[0]) if self.features_dataset else 0}")
        
        return len(self.features_dataset) > 0

    def entrenar_modelo(self):
        """Entrenar el clasificador personalizado"""
        print("\n🧠 INICIANDO ENTRENAMIENTO...")
        print("="*50)
        
        # Verificar datos antes de entrenar
        tiene_datos_suficientes = self.verificar_datos()
        if not tiene_datos_suficientes:
            respuesta = input("\n❓ ¿Quieres continuar aunque falten datos? (s/n): ")
            if respuesta.lower() != 's':
                print("🚫 Entrenamiento cancelado")
                return False
        
        # Cargar datos
        if not self.cargar_datos_entrenamiento():
            print("❌ No se pudieron cargar datos de entrenamiento")
            return False
        
        if len(self.features_dataset) < 6:
            print(f"❌ Muy pocos datos: {len(self.features_dataset)} muestras")
            print("   Mínimo absoluto: 6 muestras (3 por categoría si tienes 2 categorías)")
            print("   Recomendado: 30+ muestras para buenos resultados")
            return False
        
        # Convertir a arrays numpy
        X = np.array(self.features_dataset)
        y = np.array(self.labels_dataset)
        
        print(f"\n📊 Preparando datos...")
        print(f"   🎵 Total muestras: {len(X)}")
        print(f"   🏷️ Clases únicas: {len(np.unique(y))}")
        
        # División entrenamiento/validación
        # Con pocos datos, usar menos para validación
        if len(X) < 20:
            test_size = 0.15  # 15% para validación
        elif len(X) < 50:
            test_size = 0.2   # 20% para validación
        else:
            test_size = 0.25  # 25% para validación
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"   📈 Entrenamiento: {len(X_train)} muestras")
        print(f"   📊 Validación: {len(X_test)} muestras")
        
        # Entrenar Random Forest
        print(f"\n🌳 Entrenando Random Forest...")
        self.modelo = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        
        self.modelo.fit(X_train, y_train)
        
        # Evaluar modelo
        print(f"\n📈 EVALUANDO RENDIMIENTO...")
        y_pred = self.modelo.predict(X_test)
        accuracy = self.modelo.score(X_test, y_test)
        
        print(f"🎯 Precisión general: {accuracy:.2%}")
        
        if len(X_test) > 0:
            print(f"\n📋 Reporte detallado por categoría:")
            report = classification_report(y_test, y_pred, target_names=self.class_names, 
                                         output_dict=True, zero_division=0)
            
            for clase in self.class_names:
                if clase in report:
                    precision = report[clase]['precision']
                    recall = report[clase]['recall']
                    f1 = report[clase]['f1-score']
                    support = int(report[clase]['support'])
                    print(f"   📊 {clase:25} P:{precision:.2f} R:{recall:.2f} F1:{f1:.2f} ({support} muestras)")
        
        # Guardar modelo
        modelo_guardado = self.guardar_modelo()
        if modelo_guardado:
            print(f"\n✅ ¡ENTRENAMIENTO COMPLETADO EXITOSAMENTE!")
            return True
        else:
            print(f"\n❌ Error al guardar el modelo")
            return False

    def guardar_modelo(self):
        """Guardar el modelo entrenado"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Guardar modelo
            modelo_path = os.path.join(self.model_dir, f"clasificador_{timestamp}.pkl")
            with open(modelo_path, 'wb') as f:
                pickle.dump(self.modelo, f)
            
            # Guardar nombres de clases
            clases_path = os.path.join(self.model_dir, f"clases_{timestamp}.json")
            with open(clases_path, 'w', encoding='utf-8') as f:
                json.dump(self.class_names, f, ensure_ascii=False, indent=2)
            
            # Guardar configuración
            config = {
                'timestamp': timestamp,
                'num_clases': len(self.class_names),
                'num_muestras': len(self.features_dataset),
                'feature_dim': len(self.features_dataset[0]),
                'sample_rate': self.sample_rate,
                'clases': self.class_names
            }
            
            config_path = os.path.join(self.model_dir, f"config_{timestamp}.json")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Archivos guardados:")
            print(f"   🤖 Modelo: {modelo_path}")
            print(f"   🏷️ Clases: {clases_path}")
            print(f"   ⚙️ Config: {config_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error guardando modelo: {e}")
            return False

    def cargar_modelo_entrenado(self, modelo_path=None):
        """Cargar modelo previamente entrenado"""
        try:
            if modelo_path is None:
                # Buscar el modelo más reciente
                modelos = [f for f in os.listdir(self.model_dir) if f.startswith('clasificador_')]
                if not modelos:
                    print("❌ No hay modelos entrenados disponibles")
                    print("   Ejecuta entrenar_modelo() primero")
                    return False
                modelo_path = os.path.join(self.model_dir, sorted(modelos)[-1])
            
            # Cargar modelo
            with open(modelo_path, 'rb') as f:
                self.modelo = pickle.load(f)
            
            # Cargar nombres de clases
            timestamp = os.path.basename(modelo_path).replace('clasificador_', '').replace('.pkl', '')
            clases_path = os.path.join(self.model_dir, f"clases_{timestamp}.json")
            
            with open(clases_path, 'r', encoding='utf-8') as f:
                self.class_names = json.load(f)
            
            print(f"✅ Modelo cargado exitosamente")
            print(f"📂 Archivo: {os.path.basename(modelo_path)}")
            print(f"🏷️ {len(self.class_names)} clases disponibles:")
            for i, clase in enumerate(self.class_names):
                print(f"   [{i+1:2d}] {clase}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            return False

    def predecir_audio(self, audio_path, mostrar_detalles=True):
        """Predecir la clase de un archivo de audio"""
        if not hasattr(self, 'modelo'):
            print("❌ Modelo no cargado. Usa cargar_modelo_entrenado() primero")
            return None
        
        if not os.path.exists(audio_path):
            print(f"❌ Archivo no encontrado: {audio_path}")
            return None
        
        # Extraer características
        print(f"🔍 Analizando: {os.path.basename(audio_path)}")
        features = self.extraer_caracteristicas_yamnet(audio_path)
        if features is None:
            print("❌ No se pudieron extraer características")
            return None
        
        # Predecir
        features_reshaped = features.reshape(1, -1)
        prediccion = self.modelo.predict(features_reshaped)[0]
        probabilidades = self.modelo.predict_proba(features_reshaped)[0]
        
        # Preparar resultado
        resultado = {
            'archivo': os.path.basename(audio_path),
            'clase_predicha': self.class_names[prediccion],
            'confianza': probabilidades[prediccion],
            'todas_probabilidades': {
                self.class_names[i]: prob 
                for i, prob in enumerate(probabilidades)
            }
        }
        
        if mostrar_detalles:
            print(f"\n🎯 RESULTADO DE PREDICCIÓN")
            print(f"="*40)
            print(f"📁 Archivo: {resultado['archivo']}")
            print(f"🏆 Predicción: {resultado['clase_predicha']}")
            print(f"🔥 Confianza: {resultado['confianza']:.1%}")
            
            # Mostrar top 5 probabilidades
            print(f"\n📊 Top 5 probabilidades:")
            sorted_probs = sorted(resultado['todas_probabilidades'].items(), 
                                key=lambda x: x[1], reverse=True)
            
            for i, (clase, prob) in enumerate(sorted_probs[:5], 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📊"
                print(f"   {emoji} {clase:25} {prob:.1%}")
        
        return resultado

def main():
    """Función principal interactiva"""
    print("🎯 ENTRENADOR DE CLASIFICADOR PERSONALIZADO")
    print("="*60)
    print("🚀 ¡Entrena tu propio clasificador de sonidos urbanos!")
    print()
    
    entrenador = EntrenadorPersonalizado()
    
    while True:
        print("\n🔧 ¿QUÉ QUIERES HACER?")
        print("="*40)
        print("1️⃣ 📁 Crear estructura de carpetas")
        print("2️⃣ 🔍 Verificar datos disponibles")
        print("3️⃣ 🧠 Entrenar nuevo modelo")
        print("4️⃣ 📂 Cargar modelo existente")
        print("5️⃣ 🎵 Predecir archivo de audio")
        print("6️⃣ 📊 Ver modelos guardados")
        print("7️⃣ 🚪 Salir")
        
        try:
            opcion = input("\n👉 Elige una opción (1-7): ").strip()
            
            if opcion == "1":
                categorias = entrenador.crear_estructura_datos()
                print(f"\n✅ ¡Estructura creada! Ahora agrega archivos a las {len(categorias)} carpetas")
                
            elif opcion == "2":
                entrenador.verificar_datos()
                
            elif opcion == "3":
                print("\n🧠 Iniciando entrenamiento...")
                if entrenador.entrenar_modelo():
                    print("\n🎉 ¡Modelo entrenado exitosamente!")
                else:
                    print("\n😞 El entrenamiento falló")
                    
            elif opcion == "4":
                if entrenador.cargar_modelo_entrenado():
                    print("\n✅ ¡Modelo cargado y listo para usar!")
                else:
                    print("\n😞 No se pudo cargar el modelo")
                    
            elif opcion == "5":
                if not hasattr(entrenador, 'modelo'):
                    print("⚠️ Primero debes cargar un modelo (opción 4)")
                    continue
                    
                archivo = input("📁 Ruta del archivo de audio: ").strip().strip('"')
                if archivo and os.path.exists(archivo):
                    resultado = entrenador.predecir_audio(archivo)
                    if resultado:
                        print(f"\n🎯 ¡Predicción completada!")
                else:
                    print("❌ Archivo no encontrado")
                    
            elif opcion == "6":
                modelo_dir = "modelo_personalizado"
                if os.path.exists(modelo_dir):
                    modelos = [f for f in os.listdir(modelo_dir) if f.startswith('clasificador_')]
                    if modelos:
                        print(f"\n📊 Modelos guardados ({len(modelos)}):")
                        for i, modelo in enumerate(sorted(modelos), 1):
                            timestamp = modelo.replace('clasificador_', '').replace('.pkl', '')
                            fecha = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                            print(f"   [{i}] {modelo} (creado: {fecha.strftime('%Y-%m-%d %H:%M')})")
                    else:
                        print("📭 No hay modelos guardados")
                else:
                    print("📭 No existe directorio de modelos")
                    
            elif opcion == "7":
                print("\n👋 ¡Hasta luego! Happy coding! 🚀")
                break
                
            else:
                print("❌ Opción inválida. Usa números 1-7")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()