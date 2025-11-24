"""
Módulo para analizar y extraer perfiles de frecuencias dominantes de audios de entrenamiento.
Usa FFT para detectar automáticamente las frecuencias más importantes de cada clase.
"""

import os
import json
import numpy as np
import librosa
from scipy.signal import find_peaks
from collections import defaultdict


class FrequencyProfiler:
    """Analizador de frecuencias dominantes para clasificación de audio"""
    
    def __init__(self, data_dir='datos_entrenamiento', output_dir='modelo_personalizado'):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.perfiles = {}
        
    def analizar_audio(self, audio_path, sample_rate=16000):
        """
        Analiza un archivo de audio y extrae sus frecuencias dominantes usando FFT.
        
        Args:
            audio_path: Ruta al archivo de audio
            sample_rate: Frecuencia de muestreo
            
        Returns:
            Lista de frecuencias dominantes (en Hz)
        """
        try:
            # Cargar audio
            y, sr = librosa.load(audio_path, sr=sample_rate)
            
            # Aplicar FFT con ventana más grande para mejor resolución
            n_fft = 4096
            fft_result = np.fft.rfft(y, n=n_fft)
            magnitudes = np.abs(fft_result)
            freqs = np.fft.rfftfreq(n_fft, 1/sr)
            
            # Normalizar magnitudes
            magnitudes = magnitudes / np.max(magnitudes)
            
            # Encontrar picos significativos (altura mínima 10% del máximo)
            altura_min = 0.1
            picos, propiedades = find_peaks(magnitudes, height=altura_min, distance=5)
            
            # Obtener frecuencias de los picos
            frecuencias_picos = freqs[picos]
            magnitudes_picos = magnitudes[picos]
            
            # Filtrar frecuencias muy bajas (ruido) y muy altas
            mask = (frecuencias_picos >= 20) & (frecuencias_picos <= 5000)
            frecuencias_filtradas = frecuencias_picos[mask]
            magnitudes_filtradas = magnitudes_picos[mask]
            
            # Ordenar por magnitud y tomar las más significativas
            indices_ordenados = np.argsort(magnitudes_filtradas)[::-1]
            frecuencias_dominantes = frecuencias_filtradas[indices_ordenados]
            
            return frecuencias_dominantes.tolist()
            
        except Exception as e:
            print(f"❌ Error analizando {audio_path}: {e}")
            return []
    
    def entrenar_perfiles(self, max_archivos_por_clase=30):
        """
        Analiza todos los audios de entrenamiento y crea perfiles de frecuencia por clase.
        
        Args:
            max_archivos_por_clase: Máximo de archivos a analizar por clase
            
        Returns:
            Diccionario con perfiles de frecuencia por clase
        """
        print(f"\n🔊 ANALIZANDO FRECUENCIAS DOMINANTES...")
        print("="*60)
        
        if not os.path.exists(self.data_dir):
            print(f"❌ No existe el directorio: {self.data_dir}")
            return {}
        
        # Obtener todas las clases (subdirectorios)
        clases = [d for d in os.listdir(self.data_dir) 
                 if os.path.isdir(os.path.join(self.data_dir, d))]
        
        if not clases:
            print(f"❌ No se encontraron clases en: {self.data_dir}")
            return {}
        
        print(f"📁 Clases encontradas: {clases}\n")
        
        perfiles = {}
        
        for clase in clases:
            print(f"📊 Analizando clase: {clase}")
            clase_dir = os.path.join(self.data_dir, clase)
            
            # Obtener archivos de audio
            archivos = [f for f in os.listdir(clase_dir) 
                       if f.endswith(('.wav', '.mp3', '.flac', '.ogg'))]
            
            if not archivos:
                print(f"   ⚠️ No hay archivos de audio en {clase}")
                continue
            
            # Limitar cantidad de archivos
            archivos = archivos[:max_archivos_por_clase]
            print(f"   🎵 Analizando {len(archivos)} archivos...")
            
            # Recolectar todas las frecuencias detectadas
            todas_frecuencias = []
            
            for i, archivo in enumerate(archivos, 1):
                audio_path = os.path.join(clase_dir, archivo)
                frecuencias = self.analizar_audio(audio_path)
                
                if frecuencias:
                    todas_frecuencias.extend(frecuencias)
                
                if i % 10 == 0:
                    print(f"      Procesados {i}/{len(archivos)}...")
            
            if not todas_frecuencias:
                print(f"   ⚠️ No se encontraron frecuencias para {clase}")
                continue
            
            # Agrupar frecuencias similares (tolerancia de ±8 Hz)
            frecuencias_agrupadas = self._agrupar_frecuencias(todas_frecuencias, tolerancia=8)
            
            # Ordenar por frecuencia de aparición
            frecuencias_ordenadas = sorted(frecuencias_agrupadas.items(), 
                                          key=lambda x: x[1], reverse=True)
            
            # Tomar las 12 frecuencias más comunes
            frecuencias_dominantes = [freq for freq, count in frecuencias_ordenadas[:12]]
            frecuencias_dominantes.sort()  # Ordenar de menor a mayor
            
            # Calcular estadísticas
            fundamental = frecuencias_dominantes[0] if frecuencias_dominantes else 0
            rango_min = min(todas_frecuencias) if todas_frecuencias else 0
            rango_max = max(todas_frecuencias) if todas_frecuencias else 0
            
            perfiles[clase] = {
                'frecuencias_dominantes': frecuencias_dominantes,
                'fundamental_estimada': float(fundamental),
                'rango_min': float(rango_min),
                'rango_max': float(rango_max),
                'num_archivos_analizados': len(archivos)
            }
            
            print(f"   ✅ Frecuencias dominantes: {frecuencias_dominantes[:8]}")
            print(f"   📈 Fundamental estimada: {fundamental:.1f} Hz")
            print(f"   📊 Rango: {rango_min:.1f} - {rango_max:.1f} Hz\n")
        
        self.perfiles = perfiles
        return perfiles
    
    def _agrupar_frecuencias(self, frecuencias, tolerancia=8):
        """
        Agrupa frecuencias similares dentro de una tolerancia.
        
        Args:
            frecuencias: Lista de frecuencias
            tolerancia: Tolerancia en Hz para considerar frecuencias similares
            
        Returns:
            Diccionario {frecuencia_representativa: conteo}
        """
        if not frecuencias:
            return {}
        
        grupos = defaultdict(int)
        frecuencias_ordenadas = sorted(frecuencias)
        
        for freq in frecuencias_ordenadas:
            # Buscar si existe un grupo cercano
            grupo_encontrado = False
            for grupo_freq in list(grupos.keys()):
                if abs(freq - grupo_freq) <= tolerancia:
                    grupos[grupo_freq] += 1
                    grupo_encontrado = True
                    break
            
            if not grupo_encontrado:
                grupos[freq] = 1
        
        return dict(grupos)
    
    def guardar_perfiles(self, filename='frequency_profiles.json'):
        """Guarda los perfiles de frecuencia en un archivo JSON"""
        if not self.perfiles:
            print("⚠️ No hay perfiles para guardar")
            return False
        
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.perfiles, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Perfiles guardados en: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error guardando perfiles: {e}")
            return False
    
    def cargar_perfiles(self, filename='frequency_profiles.json'):
        """Carga perfiles de frecuencia desde un archivo JSON"""
        filepath = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"⚠️ No existe el archivo: {filepath}")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.perfiles = json.load(f)
            return self.perfiles
        except Exception as e:
            print(f"❌ Error cargando perfiles: {e}")
            return {}
    
    def obtener_perfil(self, clase):
        """Obtiene el perfil de frecuencia de una clase específica"""
        return self.perfiles.get(clase, None)


def entrenar_perfiles_frecuencia(data_dir='datos_entrenamiento', output_dir='modelo_personalizado'):
    """
    Función auxiliar para entrenar perfiles de frecuencia.
    Útil para llamar desde otros módulos.
    
    Args:
        data_dir: Directorio con datos de entrenamiento
        output_dir: Directorio donde guardar los perfiles
        
    Returns:
        True si se guardaron los perfiles, False en caso contrario
    """
    profiler = FrequencyProfiler(data_dir, output_dir)
    perfiles = profiler.entrenar_perfiles()
    
    if perfiles:
        return profiler.guardar_perfiles()
    
    return False


if __name__ == '__main__':
    # Ejemplo de uso
    profiler = FrequencyProfiler()
    perfiles = profiler.entrenar_perfiles()
    
    if perfiles:
        profiler.guardar_perfiles()
        print("\n✅ Proceso completado")
    else:
        print("\n❌ No se pudieron crear los perfiles")
